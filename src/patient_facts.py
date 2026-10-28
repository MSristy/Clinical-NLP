"""Exact input fact references and genuinely unknown question slots; no diagnosis."""
import json

SLOTS = {
    'age_years': 'What is the patient’s age in years?',
    'sex': 'What is the patient’s sex?',
    'weight_kg': 'What is the patient’s measured weight in kilograms?',
    'illness_day': 'Which day of illness is this, counting symptom onset as day 1?',
    'temperature_c': 'What is the measured temperature in °C?',
    'history.current_medicines': 'Which medicines is the patient currently taking, including doses and duration?',
    'history.known_allergies': 'Are there any known medicine allergies?',
    'history.comorbidities': 'Are there any pre-existing medical conditions?',
    'history.pregnant': 'Has current pregnancy status been assessed?',
    'history.may_become_pregnant': 'Has pregnancy potential been assessed?',
    'history.preexisting_liver_or_kidney_disease': 'Is there pre-existing liver or kidney disease?',
    'history.alternative_condition_explaining_joint_symptoms': 'Is another condition known to explain the joint symptoms?',
    'history.medicines_taken_regularly_and_correctly': 'Has regular and correct use of the current medicines been checked?',
    'epidemiology.cholera_outbreak_declared_in_area': 'Has a cholera outbreak been declared in the patient’s area?',
    'epidemiology.residence_or_travel_to_epidemic_area': 'Was there residence in or travel to an epidemic area?',
    'epidemiology.reported_local_transmission_within_15_days_before_onset': 'Was local transmission reported within 15 days before onset?',
    'examination': 'What are the examination findings, including mental state, pulse, breathing, eyes, drinking and skin pinch?',
    'examination.warning_sign_screen': 'What did the clinician’s complete warning-sign assessment find?',
    'examination.office_bp_readings_mmhg': 'What repeated blood pressure readings were recorded?',
    'examination.clinician_recorded_bp_target': 'What blood pressure target has the clinician recorded?',
    'examination.oral_fluids_tolerated': 'Can the patient tolerate oral fluids?',
    'examination.urine_output_report': 'What is the recent urine output?',
    'social_context': 'Are caregiver support, transport and access to healthcare available?',
    'clinical_assessment.home_management_eligible': 'Has a clinician explicitly assessed eligibility for home management?',
    'clinical_assessment.dengue_excluded': 'Has the clinician excluded dengue after considering test timing and findings?',
    'symptoms.severe_joint_pain': 'Is the joint pain severe, and is there arthritis?',
    'available_tests': 'What test results are available, with dates or illness day and clinician review?',
    'clinical_assessment.pre_losartan_creatinine_checked': 'Has the clinician reviewed serum creatinine before considering losartan?',
    'clinical_assessment.pre_losartan_potassium_checked': 'Has the clinician reviewed serum potassium before considering losartan?',
    'clinical_assessment.dehydration_class': 'What dehydration class does the clinician establish after reconciling the danger signs and hydration findings?',
}

FIELD_SLOTS = {
    'age_years': ['age_years'], 'illness_day': ['illness_day'], 'temperature_c': ['temperature_c'],
    'fever_present': ['temperature_c'], 'acute_fever_onset': ['illness_day'],
    'pregnant': ['history.pregnant'], 'may_become_pregnant': ['history.may_become_pregnant'],
    'coexisting_condition_present': ['history.comorbidities'],
    'high_risk_condition_present': ['age_years', 'history.pregnant', 'history.comorbidities'],
    'social_risk_present': ['social_context'], 'home_management_eligible_assessed': ['clinical_assessment.home_management_eligible'],
    'dengue_warning_signs_present': ['examination.warning_sign_screen'],
    'current_htn_step': ['history.current_medicines'], 'months_since_step1_started': ['history.current_medicines'],
    'medicines_taken_regularly_correctly': ['history.medicines_taken_regularly_and_correctly'],
    'bp_target_met': ['examination.clinician_recorded_bp_target', 'examination.office_bp_readings_mmhg'],
    'sbp_mmhg': ['examination.office_bp_readings_mmhg'], 'dbp_mmhg': ['examination.office_bp_readings_mmhg'],
    'pre_losartan_creatinine_checked': ['clinical_assessment.pre_losartan_creatinine_checked'],
    'pre_losartan_potassium_checked': ['clinical_assessment.pre_losartan_potassium_checked'],
    'dehydration_class': ['clinical_assessment.dehydration_class'],
    'cholera_outbreak_declared': ['epidemiology.cholera_outbreak_declared_in_area'],
    'severe_arthralgia_or_arthritis': ['symptoms.severe_joint_pain'],
    'joint_symptoms_explained_by_other_condition': ['history.alternative_condition_explaining_joint_symptoms'],
    'residence_or_travel_to_epidemic_area': ['epidemiology.residence_or_travel_to_epidemic_area'],
    'reported_transmission_within_15_days_before_onset': ['epidemiology.reported_local_transmission_within_15_days_before_onset'],
    'dengue_excluded_by_clinician': ['clinical_assessment.dengue_excluded'],
    'preexisting_liver_or_kidney_disease': ['history.preexisting_liver_or_kidney_disease'],
    'cannot_tolerate_oral_fluids': ['examination.oral_fluids_tolerated'],
    'reduced_urine_output': ['examination.urine_output_report'],
}
EXAM_FIELDS = {'dehydration_class', 'danger_signs_present', 'severe_dehydration_present',
               'lethargic_or_unconscious', 'absent_or_weak_pulse', 'respiratory_distress', 'sunken_eyes',
               'drinks_poorly_or_unable', 'skin_pinch_very_slow', 'irritable_or_restless', 'rapid_pulse',
               'thirsty_drinks_eagerly', 'skin_pinch_slow', 'haemodynamic_instability', 'altered_sensorium',
               'bleeding_present', 'oliguria_assessed_by_clinician', 'hmod_present'}


def questions_for_card(patient, card):
    """Link source-required concepts to input slots; not a clinical eligibility gate."""
    fields = set()
    for prerequisite in card['required_patient_fields']:
        fields.update(FIELD_SLOTS.get(prerequisite, []))
        if prerequisite in EXAM_FIELDS:
            fields.add('examination')
    if card['medications']:
        fields.update(('age_years', 'weight_kg', 'history.current_medicines', 'history.known_allergies'))
    unknown = missing_slots(patient)
    from src.clinical_context import normalized_context
    if 'dengue_excluded_by_clinician' in normalized_context(patient):
        unknown.pop('clinical_assessment.dengue_excluded', None)
    derived = normalized_context(patient)
    for concept, slot in (
        ('pre_losartan_creatinine_checked', 'clinical_assessment.pre_losartan_creatinine_checked'),
        ('pre_losartan_potassium_checked', 'clinical_assessment.pre_losartan_potassium_checked'),
        ('dehydration_class', 'clinical_assessment.dehydration_class')):
        if concept in derived and not (concept == 'dehydration_class' and derived.get('hydration_conflict')):
            unknown.pop(slot, None)
    return {field: unknown[field] for field in sorted(fields) if field in unknown}


def question_maps(patient, hits):
    by_card = {h['card']['card_id']: questions_for_card(patient, h['card']) for h in hits}
    fields = sorted({field for slots in by_card.values() for field in slots})
    lookup = {f'Q{i}': field for i, field in enumerate(fields)}
    codes = {field: code for code, field in lookup.items()}
    return lookup, {cid: [codes[field] for field in slots] for cid, slots in by_card.items()}


def at_path(patient, path):
    value = patient
    for part in path.split('.'):
        if isinstance(value, dict):
            value = value.get(part)
        elif isinstance(value, list) and part.isdigit() and int(part) < len(value):
            value = value[int(part)]
        else:
            return None
    return value


def fact_table(patient):
    facts = []
    def walk(value, path):
        if isinstance(value, dict) and value:
            for key, child in value.items():
                walk(child, f'{path}.{key}' if path else key)
        elif isinstance(value, list) and value:
            for i, child in enumerate(value):
                walk(child, f'{path}.{i}')
        elif value is not None and value != {} and value != '':
            facts.append({'id': f'F{len(facts)}', 'path': path, 'value': value})
    walk(patient, '')
    return facts


def missing_slots(patient):
    missing = {key: text for key, text in SLOTS.items()
               if at_path(patient, key) is None or at_path(patient, key) == '' or at_path(patient, key) == {}}
    # Ask one examination overview rather than redundant individual questions.
    if 'examination' in missing:
        missing = {key: text for key, text in missing.items() if not key.startswith('examination.')}
    if at_path(patient, 'symptoms.severe_arthralgia_or_arthritis') is not None:
        missing.pop('symptoms.severe_joint_pain', None)
    return missing


def display_fact(fact):
    value = fact['value']
    shown = 'yes' if value is True else 'no' if value is False else 'none reported' if value == [] else str(value)
    label = fact['path'].replace('_', ' ').replace('.', ' › ')
    return f'{label}: {shown}'
