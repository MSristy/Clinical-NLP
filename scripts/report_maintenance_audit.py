"""Compile assistant source-review verdicts, with separate contract checks.

Never imports expected answers into runtime, calls a model or changes old outputs.
"""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.engine import output_errors

FOLDER = ROOT/'evaluation/maintenance_audit'
REASONS = {
    'C01': 'Dengue differential, day-3 CBC/NS1, source paracetamol ceiling/NSAID precautions and warning advice; unassessed home eligibility withheld. Dengue PDF 27-28, 39, 41, 45-48.',
    'C02': 'Established BP follow-up retains assessed step 2, source lab monitoring and follow-up; no invented route/duration. Hypertension PDF 46, 51, 64-65.',
    'C03': 'Source-table some-dehydration findings retain Plan B plus hourly reassessment; no premature discharge or automatic antibiotic. Cholera PDF 5-6, 9-10.',
    'C04': 'Clinical/epidemiological chikungunya consideration retains dengue differential/precautions and timed tests; higher chikungunya paracetamol and unestablished admission withheld. Chikungunya PDF 11, 18-22, 26-27; dengue PDF 37, 45-48.',
    'C05': 'Unknown age/day/history are preserved; no individualized regimen or home clearance. First audit omitted examination/epidemiology clarification required by the original source-linked expectation. Dengue PDF 26-28, 37, 39, 45-48; chikungunya PDF 11, 18-22.',
    'C06': 'Pregnancy potential blocks losartan, retains the distinct nonpregnant amlodipine branch and unchanged investigation/follow-up advice. Hypertension PDF 64-65.',
}


def main():
    paths = sorted((FOLDER/'outputs').glob('*.json'))
    if len(paths) != 12:
        raise SystemExit('Require all twelve first audit records, not a cherry-picked subset.')
    rows = []
    for path in paths:
        record = json.loads(path.read_text())
        if record['status'] != 'completed' or output_errors(record['output'], record['retrieved']):
            raise SystemExit('Cannot mark contract/generation pass: '+path.name)
        cid = record['case_id']
        rows.append({'case_id': cid, 'mode': record['mode'], 'expected_behaviour': 'fail' if cid == 'C05' else 'pass',
                     'citation_support': 'pass', 'restrictions': 'pass', 'missing_information_honesty': 'pass',
                     'elapsed_seconds': record['timing_seconds']['total'],
                     'failure_note': 'Missing examination/epidemiology clarification; preserved, then fixed in separately versioned follow-up.' if cid == 'C05' else '',
                     'reason_and_source_pages': REASONS[cid], 'output_sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
    for cid in ('C01','C02','C03','C04','C05','C06'):
        a, b = [json.loads((FOLDER/'outputs'/f'{cid}_{mode}.json').read_text()) for mode in ('baseline','improved')]
        assert a['patient'] == b['patient'] and a['retrieved'] == b['retrieved']
        assert a['model']['model'] == b['model']['model'] and a['model']['settings'] == b['model']['settings']
        context = json.loads(b['messages'][1]['content']); context.pop('applicability_preview')
        assert a['messages'][0] == b['messages'][0] and json.loads(a['messages'][1]['content']) == context
    report = {'scope': 'AI-assistant source review of self-authored maintenance cases; not independent clinical validation.',
              'review_method': 'Inspected actual selected actions, canonical conditions/passages and supplied PDF text/images. Contract assertions are supplementary, not clinical grading.',
              'first_audit_reviewed_outputs': 12, 'first_audit_key_behaviour_pass': '10/12',
              'first_audit_citation_support_pass': '12/12', 'first_audit_restrictions_pass': '12/12',
              'first_audit_missing_information_honesty_pass': '12/12', 'first_audit_all_four_pass': '10/12',
              'na_count': 0, 'rows': rows,
              'limitation': 'C05 questions were incomplete despite no invented findings. Original experiment/checklists/results remain unchanged. Later corrected calls must stay separate.'}
    (FOLDER/'source-review.json').write_text(json.dumps(report, indent=2)+'\n')
    lines = ['# First maintenance audit: source-reviewed results', '',
             'AI-assisted source review; six self-authored cases, not independent clinical validation. This is a different release from the original submitted experiment.', '',
             '| Case | Mode | Expected | Citations | Restrictions | Missing info honesty | Seconds | Failure note |',
             '|---|---|---|---|---|---|---:|---|']
    for r in rows:
        lines.append('| '+' | '.join(str(r[k]) for k in ('case_id','mode','expected_behaviour','citation_support','restrictions','missing_information_honesty','elapsed_seconds','failure_note'))+' |')
    lines += ['', 'First audit: key behaviour 10/12; citations 12/12; restrictions 12/12; missing-information honesty 12/12; all four checks 10/12; NA 0. Incomplete questions are scored as expected-behaviour failures, not invented-fact failures. See source-review.json for each output hash, reason and source pages.', '',
              'C05 retained its clarification gap. A separate source/question-mapping correction and fresh targeted follow-up are recorded without replacing these twelve results. No clinical accuracy or preview-benefit claim is made.']
    (FOLDER/'results-table.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('rows','review_method')},indent=2))


if __name__ == '__main__':
    main()
