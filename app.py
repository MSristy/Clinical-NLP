"""Streamlit patient entry, evidence review and provisional care plan."""
import copy
import json
from datetime import datetime, timezone
from pathlib import Path
import time
import streamlit as st
from src.engine import evidence_for, recommend, retrieve, POLICY_VERSION
from src.model import model_status, configured_model_name
from src.patient import prepare_patient
from src.retrieval_context import RETRIEVAL_VERSION

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title='Clinical NLP | Clinical guideline assistant', page_icon='🩺', layout='wide')
st.markdown('<style>'+(ROOT/'ui/workspace.css').read_text(encoding='utf-8')+'</style>', unsafe_allow_html=True)
if st.session_state.get('ui_appearance', 'White') == 'Black':
    st.markdown('<style>'+(ROOT/'ui/dark.css').read_text(encoding='utf-8')+'</style>', unsafe_allow_html=True)
st.markdown((ROOT/'ui/header.html').read_text(encoding='utf-8'), unsafe_allow_html=True)


@st.cache_data
def demo_cases():
    return json.loads((ROOT/'evaluation/cases/draft_cases.json').read_text(encoding='utf-8'))['cases']


def blank_patient():
    return {'chief_complaint': '', 'age_years': None, 'sex': None, 'weight_kg': None,
            'illness_day': None, 'temperature_c': None, 'symptoms': {},
            'history': {'comorbidities': None, 'current_medicines': None, 'known_allergies': None,
                        'pregnant': None, 'may_become_pregnant': None},
            'examination': {}, 'available_tests': None, 'additional_context': ''}


def load_patient(patient):
    st.session_state.editor_generation = st.session_state.get('editor_generation', 0)+1
    st.session_state.patient_json = json.dumps(patient, ensure_ascii=False, indent=2)
    for key in list(st.session_state):
        if key.startswith('form_'):
            del st.session_state[key]
    st.session_state.pop('record', None)


def form_key(name):
    return 'form_'+str(st.session_state.get('editor_generation', 0))+'_'+name.removeprefix('form_')


def human_text(value):
    if value is None or value == {}:
        return ''
    if value == []:
        return 'None'
    if isinstance(value, list):
        return '\n'.join(human_text(item) for item in value)
    if isinstance(value, dict):
        return '\n'.join(f'{key.replace("_", " ")}: {human_text(item)}' for key, item in value.items())
    return str(value)


def edit_text(label, value, key, height=100):
    initial = human_text(value)
    edited = st.text_area(label, value=initial, key=form_key(key), height=height)
    if edited == initial:
        return value
    if not edited.strip():
        return None
    return [] if edited.strip().lower() == 'none' else edited.strip()


def guided_editor(patient):
    patient = copy.deepcopy(patient)
    tabs = st.tabs(['Basics', 'History & medicines', 'Examination & tests'])
    with tabs[0]:
        patient['chief_complaint'] = st.text_area('Chief complaint / symptoms', value=patient.get('chief_complaint', ''), key=form_key('complaint'), height=130,
            placeholder='Describe symptoms and onset. A disease name is not needed.')
        a, b = st.columns(2)
        with a:
            patient['age_years'] = st.number_input('Age (years)', min_value=0.0, max_value=130.0,
                value=float(patient['age_years']) if patient.get('age_years') is not None else None, key=form_key('age'))
            patient['illness_day'] = st.number_input('Day of illness', min_value=1, max_value=36500,
                value=int(patient['illness_day']) if patient.get('illness_day') is not None else None, key=form_key('day'), help='First day of symptoms = day 1. Leave empty when unknown.')
            patient['weight_kg'] = st.number_input('Weight (kg)', min_value=0.0, max_value=500.0,
                value=float(patient['weight_kg']) if patient.get('weight_kg') is not None else None, key=form_key('weight'))
        with b:
            sexes = ['Unknown', 'female', 'male', 'other']
            initial = patient.get('sex') if patient.get('sex') in sexes else 'Unknown'
            sex = st.selectbox('Sex', sexes, index=sexes.index(initial), key=form_key('sex'))
            patient['sex'] = None if sex == 'Unknown' else sex
            patient['temperature_c'] = st.number_input('Temperature (°C)', min_value=0.0, max_value=50.0,
                value=float(patient['temperature_c']) if patient.get('temperature_c') is not None else None, key=form_key('temp'))
        st.caption('Empty means unknown. Enter “None” in history fields only when assessed and absent.')
        with st.expander('Additional symptom details from the current record'):
            original = patient.get('symptoms', {})
            updated = edit_text('Other reported symptoms / assessed negatives', original, 'form_symptoms', 120)
            if updated != original:
                patient['symptoms'] = updated if isinstance(updated, dict) else {'reported_details': updated}
    with tabs[1]:
        history = patient.get('history') or {}
        if not isinstance(history, dict):
            history = {'reported_history': history}
        for field, label in [('current_medicines', 'Current medicines — name, dose, frequency and duration'),
                             ('known_allergies', 'Medicine allergies'), ('comorbidities', 'Medical history / existing conditions')]:
            history[field] = edit_text(label, history.get(field), 'form_'+field)
        for field, label in [('pregnant', 'Currently pregnant'), ('may_become_pregnant', 'May become pregnant'),
                             ('medicines_taken_regularly_and_correctly', 'Medicines taken regularly and correctly'),
                             ('elevated_bp_confirmed_on_prior_visits', 'High blood pressure confirmed on previous visits')]:
            options = ['Unknown / not assessed', 'Yes', 'No']
            index = 1 if history.get(field) is True else 2 if history.get(field) is False else 0
            answer = st.selectbox(label, options, index=index, key=form_key(field))
            if field in history or answer != 'Unknown / not assessed':
                history[field] = True if answer == 'Yes' else False if answer == 'No' else None
        patient['history'] = history
    with tabs[2]:
        original = patient.get('examination')
        edited = edit_text('Examination — BP, warning signs, hydration, pulse, urine output', original, 'form_exam', 140)
        if edited != original:
            patient['examination'] = {'reported_findings': edited} if edited else None
        patient['available_tests'] = edit_text('Available tests — result, unit and date / illness day', patient.get('available_tests'), 'form_tests', 110)
        patient['additional_context'] = st.text_area('Other context / exposure / clinician assessment', value=patient.get('additional_context') or '', key=form_key('context'), height=110)
        assessments = patient.get('clinical_assessment') or {}
        if not isinstance(assessments, dict):
            assessments = {'reported_assessment': assessments}
        with st.expander('Explicit clinician assessments (optional)'):
            for field, label in [('home_management_eligible', 'Assessed as eligible for home management'),
                                 ('dengue_excluded', 'Dengue excluded by the clinician')]:
                options = ['Unknown / not assessed', 'Yes', 'No']
                index = 1 if assessments.get(field) is True else 2 if assessments.get(field) is False else 0
                answer = st.selectbox(label, options, index=index, key=form_key('assessment_'+field))
                if field in assessments or answer != 'Unknown / not assessed':
                    assessments[field] = True if answer == 'Yes' else False if answer == 'No' else None
        if assessments:
            patient['clinical_assessment'] = assessments
        st.caption('Use Advanced JSON for separate structured exposure, social or clinician-assessment fields.')
    return patient


if 'patient_json' not in st.session_state:
    load_patient(blank_patient())
with st.sidebar:
    with st.container(key='sidebar-identity'):
        brand_column, appearance_column = st.columns([5, 1], gap='small', vertical_alignment='center')
        with brand_column:
            st.markdown((ROOT/'ui/sidebar-brand.html').read_text(encoding='utf-8'), unsafe_allow_html=True)
        with appearance_column:
            st.button('☀' if st.session_state.get('ui_appearance', 'White') == 'Black' else '☾',
                      key='ui_theme_toggle', help='Switch between White and Black appearance',
                      on_click=lambda: st.session_state.update(ui_appearance='White' if st.session_state.get('ui_appearance', 'White') == 'Black' else 'Black'))
    st.subheader('Patient workspace')
    st.markdown('''<div class="cn-workflow cn-workflow-compact" aria-label="Workflow guide: patient information, review evidence, review care plan">
    <div class="cn-workflow-step"><span>1</span>Patient</div><span aria-hidden="true">›</span>
    <div class="cn-workflow-step"><span>2</span>Evidence</div><span aria-hidden="true">›</span>
    <div class="cn-workflow-step"><span>3</span>Care plan</div></div>''', unsafe_allow_html=True)
    recommendation_mode = st.selectbox('Recommendation mode', ['baseline', 'improved'],
                        format_func=lambda value: value.title())
    cases = demo_cases()
    names = {'C01': 'Fever / dengue assessment', 'C02': 'Blood-pressure follow-up', 'C03': 'Watery diarrhoea / hydration',
             'C04': 'Fever with marked joint pain', 'C05': 'Incomplete fever case', 'C06': 'BP follow-up / pregnancy potential'}
    selected = st.selectbox('Fictional examples', [c['case_id'] for c in cases], format_func=lambda x: x+' · '+names[x])
    if st.button('Load example', use_container_width=True):
        load_patient(next(c['patient'] for c in cases if c['case_id'] == selected))
    if st.button('New patient', use_container_width=True):
        load_patient(blank_patient())
    with st.expander('Model service & technical details'):
        st.write('Model: '+configured_model_name())
        st.caption('Configured Free plan. No billing setup or automatic paid fallback.')
        if st.button('Check model connection'):
            try:
                status = model_status()
                st.success('Model metadata accessible; real generation is checked when creating a plan.') if status['installed'] else st.warning(status.get('setup_hint'))
            except RuntimeError as exc:
                st.error(str(exc))
    st.divider()
    st.caption('Prototype for fictional cases. A probable diagnosis is not laboratory confirmation.')

left, right = st.columns([1, 1.12], gap='medium')
with left, st.container(key='patient-panel'):
    st.subheader('1 · Patient information')
    mode = st.radio('Input method', ['Guided form', 'Advanced JSON'], horizontal=True)
    if mode != st.session_state.get('last_input_mode'):
        st.session_state.editor_generation = st.session_state.get('editor_generation', 0)+1
        for key in list(st.session_state):
            if key.startswith('form_'):
                del st.session_state[key]
        st.session_state.last_input_mode = mode
    try:
        if mode == 'Advanced JSON':
            st.text_area('Editable patient JSON', key='patient_json', height=540)
            patient = json.loads(st.session_state.patient_json)
            if not isinstance(patient, dict):
                raise ValueError('Patient input must be a JSON object.')
        else:
            candidate = json.loads(st.session_state.patient_json)
            if not isinstance(candidate, dict):
                raise ValueError('Patient input must be a JSON object. Correct it in Advanced JSON or press New patient.')
            patient = guided_editor(candidate)
            st.session_state.patient_json = json.dumps(patient, ensure_ascii=False, indent=2)
    except (ValueError, TypeError) as exc:
        patient = None
        st.error('Please correct patient input: '+str(exc))
    a, b = st.columns(2)
    ready = isinstance(patient, dict) and isinstance(patient.get('chief_complaint'), str) and bool(patient['chief_complaint'].strip())
    preview = a.button('Preview evidence', use_container_width=True, disabled=not ready)
    remaining = max(0, 65-(time.time()-st.session_state.get('last_api_start', 0)))
    run = b.button('Generate care plan', type='primary', use_container_width=True, disabled=not ready or remaining > 0)
    if remaining > 0:
        st.caption(f'Free-plan cooldown: about {int(remaining)+1}s. Refresh below after waiting; requests are not retried automatically.')
        st.button('Refresh cooldown')
    if preview or run:
        try:
            patient = prepare_patient(patient)
            if preview:
                prepared, query, hits = retrieve(patient)
                st.session_state.record = {'status': 'preview' if hits else 'no_evidence', 'mode': recommendation_mode, 'patient': prepared, 'query': query, 'retrieved': hits, 'output': None, 'errors': [], 'api_call_attempted': False, 'retrieval_version': RETRIEVAL_VERSION, 'policy_version': POLICY_VERSION}
            else:
                generation_started = time.time()
                with st.spinner('Reviewing protocol evidence and patient findings…'):
                    record = recommend(patient, mode=recommendation_mode)
                if record.get('api_call_attempted'):
                    st.session_state.last_api_start = generation_started
                folder = ROOT/'evaluation/interactive_runs'
                folder.mkdir(parents=True, exist_ok=True)
                saved = folder/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'.json')
                record['saved_path'] = str(saved)
                saved.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
                st.session_state.record = record
        except (ValueError, FileNotFoundError) as exc:
            st.error(str(exc))


CARE_PLAN_LABELS = {'probable_diagnosis': 'Probable diagnoses & alternatives',
                    'investigations': 'Investigations & assessment',
                    'medication_guidance': 'Medication & treatment planning',
                    'advice': 'Advice, warnings & follow-up'}
EMPTY_RECOMMENDATION = 'No recommendation selected here. Check clarification needs and evidence; this does not mean that no care is needed.'


def show_citations(card_ids, hits):
    for ref in evidence_for(card_ids, hits):
        grouped = {}
        for evidence in ref['evidence']:
            key = (evidence['source_title'], evidence['source_version'])
            grouped.setdefault(key, set()).add(evidence['pdf_page'])
        for (title, version), pages in grouped.items():
            st.caption(f'Source: {title} · {version} · PDF pages '+', '.join(map(str, sorted(pages))))


with st.sidebar:
    if isinstance(patient, dict) and patient.get('chief_complaint'):
        st.subheader('Current patient')
        st.write(patient['chief_complaint'])
        age = patient.get('age_years')
        day = patient.get('illness_day')
        st.caption(f"Age: {age if age is not None else 'unknown'} · Sex: {patient.get('sex') or 'unknown'} · Illness day: {day if day is not None else 'unknown'}")
        with st.expander('History, medicines & allergies'):
            st.write(human_text(patient.get('history')) or 'Not supplied')


with right, st.container(key='results-panel'):
    st.subheader('2 · Evidence → 3 · Care plan')
    record = st.session_state.get('record')
    if record and (record['patient'] != patient or record.get('mode', 'baseline') != recommendation_mode or record.get('retrieval_version') != RETRIEVAL_VERSION or record.get('policy_version') != POLICY_VERSION):
        st.info('Patient information or recommendation mode has changed, or the retrieval policy was updated. Preview evidence or generate a new plan to update the results.')
        record = None
    if not record:
        with st.container(border=True):
            st.markdown('''<div class="cn-empty-illustration" aria-hidden="true"><div class="cn-empty-icon">
            <svg width="28" height="28" viewBox="0 0 28 28" fill="none" focusable="false"><rect x="7" y="4" width="15" height="21" rx="3" stroke="currentColor" stroke-width="1.4"/><path d="M11 11h7m-7 4h7m-7 4h4M4 7v8m-3-4h6" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/></svg>
            </div><span>YOUR EVIDENCE WORKSPACE</span></div>''', unsafe_allow_html=True)
            st.markdown('### Start with the patient’s symptoms')
            st.write('Enter available details on the left. Preview shows source cards; Generate creates a provisional plan with supporting findings and references.')
            st.caption('A disease name is optional. Unknown information stays unknown.')
    else:
        a, b, c = st.columns(3)
        a.metric('Retrieved source cards', len(record['retrieved']))
        plan_status = record['status'].replace('_', ' ').title()
        if record['status'] == 'no_evidence':
            plan_status = 'Insufficient evidence'
        elif record['status'] == 'completed':
            plan_status = 'Ready for review' if record['output']['recommendations'] else 'No supported plan'
        b.metric('Plan status', plan_status)
        c.metric('Elapsed', f"{record.get('timing_seconds', {}).get('total', 0):.1f} s")
        tabs = st.tabs(['Care plan', 'Source evidence', 'Patient context', 'Run details'])
        with tabs[0]:
            if record['status'] == 'no_evidence':
                st.warning('Insufficient relevant protocol evidence. The available positive findings do not match the supported guideline retrieval anchors. No model request was made.')
                st.caption('This prototype covers four protocols only. Review the patient clinically and use an appropriate source. No matching evidence does not mean no care is needed. English negation handling is limited; inspect the original patient context.')
                for label in CARE_PLAN_LABELS.values():
                    with st.container(border=True):
                        st.markdown('#### '+label)
                        st.caption(EMPTY_RECOMMENDATION)
            elif record['errors']:
                st.error('A complete plan could not be created. No answer has been substituted.')
                if any('rate limit' in error.lower() or 'quota' in error.lower() for error in record['errors']):
                    st.warning('The Free model quota has been reached. Wait for its reset before trying again. No paid upgrade or fallback was attempted.')
                else:
                    st.caption('The response could not pass the required checks. Technical details are available in Run details.')
            elif record['status'] == 'preview':
                st.info('Evidence preview is ready. Open Source evidence, or Generate care plan to continue.')
            elif record['status'] == 'completed':
                output = record['output']
                st.info('Provisional care plan · Assess source conditions and patient suitability before applying.')
                if output['missing_information']:
                    with st.container(border=True, key='clarification-panel'):
                        st.markdown('#### Clarification needed for some actions')
                        for question in output['missing_information']:
                            st.write('• '+question['question'])
                            st.caption(question['why_needed'])
                            show_citations(question['card_ids'], record['retrieved'])
                for category, label in CARE_PLAN_LABELS.items():
                    with st.container(border=True):
                        st.markdown('#### '+label)
                        items = [r for r in output['recommendations'] if r['category'] == category]
                        if not items:
                            st.caption(EMPTY_RECOMMENDATION)
                        for item in items:
                            st.write(item['action'])
                            st.caption(item['patient_reason'])
                            if category == 'investigations':
                                st.markdown('**Purpose:** '+item['purpose'])
                                st.markdown('**Timing:** '+(item['timing'] or 'Not specified by the source'))
                            if item['medication']:
                                st.table([{'Medicine detail': k.title(), 'Source-supported value': v if v is not None else 'Not specified by source'} for k, v in item['medication'].items()])
                            show_citations(item['card_ids'], record['retrieved'])
                            cards = [h['card'] for h in record['retrieved'] if h['card']['card_id'] in item['card_ids']]
                            with st.expander('Conditions, restrictions & evidence passage'):
                                for card in cards:
                                    st.write(card['clinical_context'])
                                    for limitation in card['limitations']:
                                        st.caption(limitation)
                                    for evidence in card['evidence']:
                                        st.write(evidence['passage'])
                                        st.caption(f"{evidence['source_title']} · PDF page {evidence['pdf_page']} · {evidence['locator']}")
                st.caption(' '.join(output['limitations']))
        with tabs[1]:
            st.caption('Candidate source cards are evidence to assess, not an automatic diagnosis or treatment decision.')
            for hit in record['retrieved']:
                card = hit['card']
                with st.expander(card['title']+' · '+card['clinical_category'].replace('_', ' ')):
                    st.write(card['recommended_action'])
                    show_citations([card['card_id']], record['retrieved'])
                    for evidence in card['evidence']:
                        st.write(evidence['passage'])
                    with st.expander('Structured source rule / technical details'):
                        st.json(card)
        with tabs[2]:
            st.write('Patient information used for this result')
            st.write(human_text(record['patient']))
            with st.expander('Exact input record'):
                st.json(record['patient'])
        with tabs[3]:
            st.caption(record.get('verification_scope', 'Evidence preview only; no model generation.'))
            st.write('Saved file:', record.get('saved_path', 'Preview not saved automatically'))
            st.json({'model': record.get('model'), 'prompt_version': record.get('prompt_version'), 'retrieval_version': record.get('retrieval_version'), 'retrieval_query': record.get('query'), 'card_decisions': record.get('raw_decisions')})
            if record.get('errors'):
                st.write(record['errors'])
            st.download_button('Download input, plan & evidence', json.dumps(record, ensure_ascii=False, indent=2), 'clinical-nlp-run.json', 'application/json')
