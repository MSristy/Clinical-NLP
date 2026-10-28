"""Traceable BP aliases and exact WHO cholera source-table observations.

No case IDs, diagnosis training or guessed laboratory thresholds. Hydration
checks use only explicit source-table observations. Unknowns stay unresolved.
"""
import re
import math
from src.patient_facts import at_path


def normalized_context(patient):
    context = {}
    def put(field, value, paths, method):
        if value is not None:
            context[field] = {'value': value, 'source_paths': paths, 'method': method}
    # Exact structured observations. These aliases do not infer a disease from
    # free text; each derived value retains the patient path used.
    aliases = {
        'fever_present': 'symptoms.fever', 'acute_fever_onset': 'symptoms.acute_fever_onset',
        'acute_watery_diarrhoea': 'symptoms.acute_watery_diarrhoea',
        'deterioration_as_fever_settles': 'symptoms.deterioration_as_fever_settles',
        'lethargy_irritability_restlessness': 'symptoms.lethargy_irritability_restlessness',
        'cold_clammy_extremities': 'symptoms.cold_clammy_extremities',
        'persistent_disabling_joint_symptoms_after_3_days_treatment': 'symptoms.persistent_disabling_joint_symptoms_after_3_days_treatment',
        'hmod_present': 'examination.hmod_present',
    }
    for field, path in aliases.items():
        value = at_path(patient, path)
        put(field, value if isinstance(value, bool) else None, [path], 'Exact structured observation')
    oral = at_path(patient, 'examination.oral_fluids_tolerated')
    put('cannot_tolerate_oral_fluids', not oral if isinstance(oral, bool) else None,
        ['examination.oral_fluids_tolerated'], 'Boolean inversion of documented oral tolerance')
    # WHO cholera PDF 5-6: danger signs take priority over some-dehydration
    # signs. Only the listed exact structured values/phrases are normalized.
    exam = patient.get('examination') or {}
    signs = {key: exam[key] for key in (
        'lethargic_or_unconscious', 'absent_or_weak_pulse', 'respiratory_distress',
        'sunken_eyes', 'drinks_poorly_or_unable', 'skin_pinch_very_slow',
        'irritable_or_restless', 'rapid_pulse', 'thirsty_drinks_eagerly', 'skin_pinch_slow')
        if isinstance(exam.get(key), bool)}
    phrase_aliases = {
        'mental_status': {'awake and alert': {'lethargic_or_unconscious': False}, 'alert': {'lethargic_or_unconscious': False},
                         'lethargic': {'lethargic_or_unconscious': True}, 'unconscious': {'lethargic_or_unconscious': True}},
        'pulse': {'rapid but not weak or absent': {'rapid_pulse': True, 'absent_or_weak_pulse': False},
                  'normal': {'rapid_pulse': False, 'absent_or_weak_pulse': False},
                  'weak': {'absent_or_weak_pulse': True}, 'absent': {'absent_or_weak_pulse': True}},
        'eyes': {'sunken': {'sunken_eyes': True}, 'not sunken': {'sunken_eyes': False}},
        'drinking': {'eagerly; can drink safely': {'thirsty_drinks_eagerly': True, 'drinks_poorly_or_unable': False},
                     'unable to drink': {'drinks_poorly_or_unable': True}, 'drinks poorly': {'drinks_poorly_or_unable': True}},
        'skin_pinch': {'returns slowly, not very slowly': {'skin_pinch_slow': True, 'skin_pinch_very_slow': False},
                       'returns very slowly': {'skin_pinch_very_slow': True},
                       'normal': {'skin_pinch_slow': False, 'skin_pinch_very_slow': False}},
    }
    for path, phrases in phrase_aliases.items():
        value = exam.get(path)
        for field, truth in phrases.get(value.strip().lower() if isinstance(value, str) else '', {}).items():
            signs.setdefault(field, truth)
    if isinstance(exam.get('restless'), bool):
        signs.setdefault('irritable_or_restless', exam['restless'])
    for field, value in signs.items():
        put(field, value, ['examination'], 'WHO_CHOLERA_2024 PDF 5-6: exact sign/phrase alias')
    dangers = [signs.get(k) for k in ('lethargic_or_unconscious', 'absent_or_weak_pulse', 'respiratory_distress')]
    danger = True if True in dangers else False if all(v is False for v in dangers) else None
    severe_signs = [signs.get(k) for k in ('sunken_eyes', 'drinks_poorly_or_unable', 'skin_pinch_very_slow')]
    severe = True if danger is True or severe_signs.count(True) >= 2 else False if danger is False and severe_signs.count(False) >= 2 else None
    some_signs = [signs.get(k) for k in ('irritable_or_restless', 'sunken_eyes', 'rapid_pulse', 'thirsty_drinks_eagerly', 'skin_pinch_slow')]
    hydration = 'severe' if severe is True else 'some' if severe is False and danger is False and some_signs.count(True) >= 2 else None
    put('danger_signs_present', danger, ['examination'], 'WHO_CHOLERA_2024 PDF 5-6: OR of three assessed danger signs')
    put('severe_dehydration_present', severe, ['examination'], 'WHO_CHOLERA_2024 PDF 5-6: danger sign or at least two severe signs')
    explicit_hydration = exam.get('dehydration_class') or at_path(patient, 'clinical_assessment.dehydration_class')
    if hydration and explicit_hydration and hydration != explicit_hydration:
        put('hydration_conflict', True, ['examination', 'clinical_assessment'], 'Recorded class conflicts with source-table signs; clinician reconciliation required')
    put('dehydration_class', hydration or explicit_hydration, ['examination', 'clinical_assessment'],
        'WHO_CHOLERA_2024 PDF 5-6 table or explicit clinician class; no classification from missing signs')
    exclusion = at_path(patient, 'clinical_assessment.dengue_excluded')
    narrative = str(patient.get('additional_context') or '').lower()
    if exclusion is None and 'dengue has not been excluded by the clinician' in narrative:
        put('dengue_excluded_by_clinician', False, ['additional_context'],
            'Exact documented negative clinician statement; not an inference from NS1 or symptoms')
    prior = at_path(patient, 'history.elevated_bp_confirmed_on_prior_visits')
    put('previous_bp_confirmation_documented', prior if isinstance(prior, bool) else None,
        ['history.elevated_bp_confirmed_on_prior_visits'], 'Direct documented-history alias')
    regular = at_path(patient, 'history.medicines_taken_regularly_and_correctly')
    put('medicines_taken_regularly_correctly', regular if isinstance(regular, bool) else None,
        ['history.medicines_taken_regularly_and_correctly'], 'Direct adherence alias')
    medicines = at_path(patient, 'history.current_medicines')
    if isinstance(medicines, list):
        named = [m for m in medicines if isinstance(m, dict)]
        known = [m for m in named if str(m.get('name', '')).strip().lower() in ('amlodipine', 'losartan')]
        active = True if known else False if not medicines else None
        put('on_antihypertensive_treatment', active, ['history.current_medicines'], 'Named medicine from the supplied protocol; empty assessed list means none')
        if len(medicines) == 1 and len(named) == 1:
            med = named[0]
            name = str(med.get('name', '')).strip().lower()
            dose = str(med.get('dose', '')).strip().lower().replace(' ', '')
            frequency = str(med.get('frequency', '')).strip().lower()
            if name == 'amlodipine' and dose == '5mg' and frequency == 'once daily':
                put('current_htn_step', 'amlodipine_5mg_once_daily', ['history.current_medicines.0'], 'Exact documented name/dose/frequency; no regimen guessed')
                months = med.get('months_on_regimen')
                put('months_since_step1_started', months if isinstance(months, (int, float)) and not isinstance(months, bool) else None,
                    ['history.current_medicines.0.months_on_regimen'], 'Direct elapsed-time alias; no time conversion')
    readings = at_path(patient, 'examination.office_bp_readings_mmhg')
    single = at_path(patient, 'examination.bp_mmhg')
    supplied_readings = readings if isinstance(readings, list) else [single] if isinstance(single, dict) else []
    valid_readings = [r for r in supplied_readings if isinstance(r, dict) and
                     all(isinstance(r.get(k), (int, float)) and not isinstance(r[k], bool) and math.isfinite(r[k])
                         for k in ('systolic', 'diastolic'))]
    positive_narrative = ''
    from src.retrieval_context import positive_text
    positive_narrative = positive_text(patient.get('chief_complaint', ''))
    prose_bp = re.findall(r'\b(?:bp|blood pressure)(?:\s+(?:is|of))?\s*[:=]?\s*(\d{2,3})\s*/\s*(\d{2,3})', positive_narrative, re.I)
    if any(r['systolic'] >= 140 or r['diastolic'] >= 90 for r in valid_readings) or any(int(s) >= 140 or int(d) >= 90 for s, d in prose_bp):
        put('elevated_bp_retrieval_cue', True, ['examination', 'chief_complaint'], 'BD_HTN_2023_2E PDF 46: numeric BP retrieval cue only, not diagnostic confirmation')
    for field, key in (('sbp_mmhg', 'systolic'), ('dbp_mmhg', 'diastolic')):
        index = 0 if key == 'systolic' else 1
        values = {r[key] for r in valid_readings} | {int(pair[index]) for pair in prose_bp}
        put(field, next(iter(values)) if len(values) == 1 else None,
            ['examination', 'chief_complaint'] if prose_bp else ['examination'],
            'Consistent explicitly recorded BP component, including literal BP N/N prose; no mean or unreported reading invented'
            if prose_bp else 'Consistent supplied BP component; no mean or unreported reading invented')
    if prior is True or isinstance(readings, list) and readings:
        put('hypertension_under_assessment', True,
            ['history.elevated_bp_confirmed_on_prior_visits', 'examination.office_bp_readings_mmhg'], 'Documented hypertension history or BP-assessment readings, not a new confirmed diagnosis')
    target = at_path(patient, 'examination.clinician_recorded_bp_target')
    numbers = re.search(r'(\d{2,3})\s*/\s*(\d{2,3})', target) if isinstance(target, str) and ('below' in target.lower() or '<' in target) else None
    if numbers and isinstance(readings, list) and readings:
        sbp, dbp = map(int, numbers.groups())
        valid = all(isinstance(r, dict) and all(isinstance(r.get(k), (int, float)) and not isinstance(r.get(k), bool) for k in ('systolic', 'diastolic')) for r in readings)
        if valid:
            below = [r['systolic'] < sbp and r['diastolic'] < dbp for r in readings]
            # Do not invent an averaging rule for mixed readings.
            met = True if all(below) else False if not any(below) else None
            put('bp_target_met', met, ['examination.office_bp_readings_mmhg', 'examination.clinician_recorded_bp_target'],
                'All supplied readings consistently below or not below the clinician-recorded target; mixed readings remain unknown')
    tests = at_path(patient, 'available_tests')
    if isinstance(tests, list):
        for name in ('creatinine', 'potassium'):
            matches = [t for t in tests if isinstance(t, dict) and name in str(t.get('name', '')).lower()]
            checked = True if any(t.get('reviewed_by_clinician') is True for t in matches) else False if not tests else None
            put('pre_losartan_'+name+'_checked', checked, ['available_tests'],
                'Named test explicitly reviewed by clinician; does not establish acceptable numeric values')
    return context
