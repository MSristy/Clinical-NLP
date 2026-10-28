"""Behavioral regressions for the concrete Q2 gaps, without real API calls."""
import json
import unittest
from pathlib import Path
from src.engine import retrieve, grounded_selection, render_selection
from src.patient_facts import fact_table, missing_slots, questions_for_card
from src.observed_constraints import constraint_review
from src.clinical_context import normalized_context


class Q2RequirementsTests(unittest.TestCase):
    def decisions(self, hits):
        return {'decisions': [{'card_id': h['card']['card_id'], 'decision': 'not_applicable',
                               'fact_ids': [], 'missing_fields': []} for h in hits]}

    def test_febrile_input_retrieves_all_candidate_categories(self):
        _, _, hits = retrieve({'chief_complaint': 'Fever with headache and pain behind eyes',
                               'symptoms': {'fever': True, 'rash': True}, 'illness_day': 3})
        dengue = [h['card'] for h in hits if h['card']['disease'] == 'dengue']
        self.assertEqual({c['clinical_category'] for c in dengue},
                         {'probable_diagnosis', 'investigations', 'medication_guidance', 'advice'})
        self.assertIn('DEN_TEST_EARLY', {c['card_id'] for c in dengue})

    def test_known_weight_and_assessed_empty_history_are_not_question_slots(self):
        patient = {'chief_complaint': 'Diarrhoea', 'weight_kg': 55,
                   'history': {'current_medicines': [], 'known_allergies': [], 'pregnant': False}}
        missing = missing_slots(patient)
        for field in ('weight_kg', 'history.current_medicines', 'history.known_allergies', 'history.pregnant'):
            self.assertNotIn(field, missing)

    def test_unknown_fact_or_reasking_supplied_detail_is_rejected(self):
        patient, _, hits = retrieve({'chief_complaint': 'Fever', 'weight_kg': 55})
        payload = self.decisions(hits)
        payload['decisions'][0].update(decision='needs_information', missing_fields=['weight_kg'])
        with self.assertRaisesRegex(ValueError, 'supplied'):
            grounded_selection(patient, payload, hits)
        payload['decisions'][0].update(decision='recommend', missing_fields=[], fact_ids=['INVENTED'])
        with self.assertRaisesRegex(ValueError, 'Unknown fact'):
            grounded_selection(patient, payload, hits)

    def test_reasons_use_exact_values_and_investigation_has_timing(self):
        patient, _, hits = retrieve({'chief_complaint': 'Fever with headache and retro orbital pain',
                                    'illness_day': 3, 'symptoms': {'fever': True},
                                    'history': {'current_medicines': []}})
        fact = next(f for f in fact_table(patient) if f['path'] == 'history.current_medicines')
        payload = self.decisions(hits)
        target = next(r for r in payload['decisions'] if r['card_id'] == 'DEN_TEST_EARLY')
        target.update(decision='recommend', fact_ids=[fact['id']])
        selected = grounded_selection(patient, payload, hits)
        output = render_selection(patient, selected, hits)
        item = output['recommendations'][0]
        self.assertIn('none reported', item['patient_reason'])
        self.assertNotIn('taking paracetamol', item['patient_reason'])
        self.assertIn('1–5', item['timing'])
        self.assertTrue(item['purpose'])

    def test_every_retrieved_card_requires_a_decision(self):
        patient, _, hits = retrieve({'chief_complaint': 'Fever'})
        with self.assertRaisesRegex(ValueError, 'each retrieved card'):
            grounded_selection(patient, {'decisions': []}, hits)

    def test_explicit_pregnancy_potential_blocks_losartan_branch(self):
        cards = [json.loads(line) for line in Path('data/cards/cards.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]
        card = next(c for c in cards if c['card_id'] == 'HTN_STEP2_FOLLOWUP')
        status, _ = constraint_review(card, {'age_years': 35, 'history': {'pregnant': False, 'may_become_pregnant': True}})
        self.assertEqual(status, 'blocked')

    def test_formal_home_assessment_unknown_is_not_clearance(self):
        cards = [json.loads(line) for line in Path('data/cards/cards.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]
        card = next(c for c in cards if c['card_id'] == 'DEN_HOME_CARE')
        status, fields = constraint_review(card, {'chief_complaint': 'Fever'})
        self.assertEqual(status, 'needs_information')
        self.assertIn('clinical_assessment.home_management_eligible', fields)

    def test_selected_medication_monitoring_appears_as_investigation(self):
        cards = [json.loads(line) for line in Path('data/cards/cards.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]
        card = next(c for c in cards if c['card_id'] == 'HTN_STEP2_FOLLOWUP')
        selected = {'selections': [{'card_id': card['card_id'], 'patient_reason': 'Recorded BP and medicines'}], 'questions': [], 'limitations': []}
        output = render_selection({'chief_complaint': 'BP follow-up'}, selected, [{'card': card}])
        monitoring = [r for r in output['recommendations'] if r['category'] == 'investigations']
        self.assertEqual(len(monitoring), 1)
        self.assertIn('several weeks', monitoring[0]['timing'])
        self.assertIn('creatinine', monitoring[0]['action'])

    def test_documented_htn_aliases_and_mixed_target_readings(self):
        patient = {'history': {'current_medicines': [{'name': 'amlodipine', 'dose': '5 mg', 'frequency': 'once daily', 'months_on_regimen': 2}],
                               'medicines_taken_regularly_and_correctly': True},
                   'examination': {'clinician_recorded_bp_target': 'below 140/90 mmHg',
                                   'office_bp_readings_mmhg': [{'systolic': 149, 'diastolic': 92}, {'systolic': 150, 'diastolic': 93}]},
                   'available_tests': [{'name': 'serum potassium', 'value': 4.1, 'reviewed_by_clinician': True}]}
        context = normalized_context(patient)
        self.assertEqual(context['current_htn_step']['value'], 'amlodipine_5mg_once_daily')
        self.assertFalse(context['bp_target_met']['value'])
        self.assertTrue(context['pre_losartan_potassium_checked']['value'])
        self.assertNotIn('pre_losartan_creatinine_checked', context)
        patient['examination']['office_bp_readings_mmhg'][1] = {'systolic': 130, 'diastolic': 80}
        self.assertNotIn('bp_target_met', normalized_context(patient))
        self.assertNotIn('pregnant', context)

    def test_one_unresolved_card_does_not_discard_supported_plan(self):
        patient, _, hits = retrieve({'chief_complaint': 'Fever with headache and retro orbital pain',
                                    'illness_day': 3, 'symptoms': {'fever': True}})
        payload = self.decisions(hits)
        fact = fact_table(patient)[0]['id']
        next(r for r in payload['decisions'] if r['card_id'] == 'DEN_TEST_EARLY').update(decision='recommend', fact_ids=[fact])
        next(r for r in payload['decisions'] if r['card_id'] == 'CHIK_TEST_TIMING').update(decision='needs_information')
        result = grounded_selection(patient, payload, hits)
        self.assertIn('DEN_TEST_EARLY', {s['card_id'] for s in result['selections']})
        self.assertTrue(any('withheld' in text for text in result['limitations']))

    def test_source_entailed_reassessment_is_retained(self):
        patient, _, hits = retrieve({'chief_complaint': 'Acute watery diarrhoea and thirst',
                                    'age_years': 30, 'weight_kg': 53,
                                    'examination': {'dehydration_class': 'some', 'danger_signs_present': False}})
        payload = self.decisions(hits)
        next(r for r in payload['decisions'] if r['card_id'] == 'CHO_PLAN_B').update(
            decision='recommend', fact_ids=[fact_table(patient)[0]['id']])
        result = grounded_selection(patient, payload, hits)
        linked = next(s for s in result['selections'] if s['card_id'] == 'CHO_PLAN_B_REASSESS')
        self.assertEqual(linked['linked_from'], 'CHO_PLAN_B')

    def test_advice_link_does_not_clear_extra_home_care_prerequisites(self):
        patient, _, hits = retrieve({'chief_complaint': 'Fever with headache and pain behind eyes',
                                    'age_years': 30, 'weight_kg': 60, 'illness_day': 3})
        payload = self.decisions(hits)
        next(r for r in payload['decisions'] if r['card_id'] == 'DEN_PARACETAMOL_LIMIT').update(
            decision='recommend', fact_ids=[fact_table(patient)[0]['id']])
        result = grounded_selection(patient, payload, hits)
        self.assertNotIn('DEN_HOME_CARE', {s['card_id'] for s in result['selections']})

    def test_explicit_negative_dengue_statement_is_not_reasked(self):
        cards = [json.loads(line) for line in Path('data/cards/cards.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]
        card = next(c for c in cards if c['card_id'] == 'CHIK_PARACETAMOL_SOURCE')
        patient = {'additional_context': 'Dengue has not been excluded by the clinician. Still febrile.'}
        self.assertFalse(normalized_context(patient)['dengue_excluded_by_clinician']['value'])
        self.assertNotIn('clinical_assessment.dengue_excluded', questions_for_card(patient, card))
        self.assertEqual(constraint_review(card, patient)[0], 'blocked')

    def test_referral_requires_documented_positive_trigger(self):
        cards = [json.loads(line) for line in Path('data/cards/cards.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]
        card = next(c for c in cards if c['card_id'] == 'CHIK_ADMISSION')
        patient = {'age_years': 28, 'history': {'pregnant': False},
                   'symptoms': {'bleeding': False, 'altered_sensorium': False}}
        self.assertEqual(constraint_review(card, patient)[0], 'trigger_review')
        patient['symptoms']['bleeding'] = True
        self.assertNotIn(constraint_review(card, patient)[0], ('blocked', 'trigger_review'))
