"""Check explicit observed prerequisites only; no inferred diagnosis/dehydration class."""
import operator
from src.patient_facts import at_path, FIELD_SLOTS, EXAM_FIELDS
from src.clinical_context import normalized_context

PATHS = {'age_years': 'age_years', 'illness_day': 'illness_day', 'temperature_c': 'temperature_c',
         'pregnant': 'history.pregnant', 'may_become_pregnant': 'history.may_become_pregnant',
         'home_management_eligible_assessed': 'clinical_assessment.home_management_eligible',
         'dengue_excluded_by_clinician': 'clinical_assessment.dengue_excluded',
         'preexisting_liver_or_kidney_disease': 'history.preexisting_liver_or_kidney_disease',
         'severe_arthralgia_or_arthritis': 'symptoms.severe_arthralgia_or_arthritis',
         'joint_symptoms_explained_by_other_condition': 'history.alternative_condition_explaining_joint_symptoms',
         'residence_or_travel_to_epidemic_area': 'epidemiology.residence_or_travel_to_epidemic_area',
         'reported_transmission_within_15_days_before_onset': 'epidemiology.reported_local_transmission_within_15_days_before_onset',
         'cholera_outbreak_declared': 'epidemiology.cholera_outbreak_declared_in_area'}
PATHS.update({'bleeding_present': 'symptoms.bleeding', 'severe_abdominal_pain': 'symptoms.severe_abdominal_pain',
              'breathing_difficulty': 'symptoms.breathing_difficulty', 'altered_sensorium': 'symptoms.altered_sensorium',
              'haemodynamic_instability': 'examination.haemodynamic_instability',
              'oliguria_assessed_by_clinician': 'examination.oliguria_assessed_by_clinician',
              'chikungunya_high_risk': 'clinical_assessment.chikungunya_high_risk'})
PATHS.update({field: 'examination.'+field for field in (
    'dehydration_class', 'danger_signs_present', 'severe_dehydration_present',
    'lethargic_or_unconscious', 'absent_or_weak_pulse', 'respiratory_distress', 'sunken_eyes',
    'drinks_poorly_or_unable', 'skin_pinch_very_slow', 'irritable_or_restless', 'rapid_pulse',
    'thirsty_drinks_eagerly', 'skin_pinch_slow', 'walks_without_assistance', 'passing_urine', 'ors_without_vomiting')})
PATHS['hours_without_watery_stool'] = 'examination.hours_since_last_watery_stool'
PATHS.update({field: 'clinical_assessment.'+field for field in (
    'pre_losartan_creatinine_checked', 'pre_losartan_potassium_checked')})
# Disease suspicion remains a model judgment. Other registered source conditions
# must not be treated as satisfied merely because normalization was incomplete.
MODEL_REVIEW_FIELDS = {'acute_febrile_illness', 'dengue_suspected', 'chikungunya_suspected',
                      'cholera_suspected', 'hypertension_under_assessment', 'acute_fever_onset',
                      'fever_present', 'acute_watery_diarrhoea'}
OPS = {'eq': operator.eq, 'ne': operator.ne, 'gt': operator.gt, 'gte': operator.ge, 'lt': operator.lt, 'lte': operator.le}


def observed(node, patient, derived=None):
    """Return True/False/None using only registered exact fields."""
    derived = normalized_context(patient) if derived is None else derived
    if node['op'] in ('all', 'any'):
        values = [observed(child, patient, derived) for child in node['conditions']]
        if node['op'] == 'all':
            return False if False in values else True if all(v is True for v in values) else None
        return True if True in values else False if all(v is False for v in values) else None
    path = PATHS.get(node['field'])
    value = at_path(patient, path) if path else None
    if value is None:
        value = derived.get(node['field'], {}).get('value')
    if value is None:
        return None
    expected = node['value']
    if isinstance(expected, bool) and not isinstance(value, bool):
        return None
    if node['op'] in ('gt', 'gte', 'lt', 'lte') and (isinstance(value, bool) or not isinstance(value, (int, float))):
        return None
    try:
        return OPS[node['op']](value, expected)
    except TypeError:
        return None


def mandatory_unknowns(node, patient):
    if observed(node, patient) is not None:
        return []
    if node['op'] in ('all', 'any'):
        # An unresolved OR is not clearance. These are clarification options,
        # not a claim that every OR member must become true.
        return [field for child in node['conditions'] for field in mandatory_unknowns(child, patient)]
    if node['field'] in MODEL_REVIEW_FIELDS:
        return []
    if node['field'] in EXAM_FIELDS and node['field'] not in FIELD_SLOTS:
        return ['examination']
    path = PATHS.get(node['field'])
    slots = FIELD_SLOTS.get(node['field'], [path] if path else [])
    if at_path(patient, 'examination') in (None, {}):
        slots = ['examination' if field.startswith('examination.') else field for field in slots]
    return slots


def medicine_allergy_conflict(card, patient):
    """Exact named medicine allergy only; never infer class/cross-reactivity."""
    import re
    allergies = at_path(patient, 'history.known_allergies')
    if isinstance(allergies, str):
        names = [allergies]
    elif isinstance(allergies, list):
        names = [a.get('name', '') if isinstance(a, dict) else a for a in allergies]
    else:
        names = []
    for medicine in card['medications']:
        for name in names:
            if not isinstance(name, str):
                continue
            text = name.strip().lower()
            if re.search(r'\b(?:no|denies|not|without)\b', text):
                continue  # Ambiguous negative prose is left for clinical review.
            if re.search(r'(?<!\w)'+re.escape(medicine['name'].lower())+r'(?!\w)', text):
                return True
    return False


def constraint_review(card, patient):
    if medicine_allergy_conflict(card, patient):
        return 'blocked', []
    if card['disease'] == 'cholera' and normalized_context(patient).get('hydration_conflict', {}).get('value'):
        return 'needs_information', ['clinical_assessment.dehydration_class']
    truth = observed(card['applicability'], patient)
    exclusions = [observed(exclusion, patient) for exclusion in card['exclusions']]
    if truth is False:
        return 'blocked', []
    if any(value is True for value in exclusions):
        return 'blocked', []
    # Active referral/escalation advice with OR-trigger criteria requires an
    # established trigger. Keep independent anticipatory warning education.
    if card['clinical_category'] == 'advice' and card['applicability']['op'] == 'all':
        triggers = [node for node in card['applicability']['conditions'] if node['op'] == 'any']
        if any(observed(node, patient) is None for node in triggers):
            return 'trigger_review', []
    unknown = mandatory_unknowns(card['applicability'], patient)
    for exclusion in card['exclusions']:
        unknown.extend(mandatory_unknowns(exclusion, patient))
    if unknown:
        return 'needs_information', sorted(set(unknown))
    return ('eligible', []) if truth is True and all(value is False for value in exclusions) else ('model_review', [])
