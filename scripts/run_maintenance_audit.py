"""Separate maintenance smoke calls; never writes the original experiment."""
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.engine import recommend
from src.groq_api import SETTINGS
from src.model import configured_model_name

FOLDER = ROOT/'evaluation/maintenance_audit'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    destination = FOLDER/'outputs'
    if destination.exists() and list(destination.glob('*.json')):
        raise SystemExit('Audit outputs already exist; do not overwrite or cherry-pick a retry.')
    destination.mkdir(exist_ok=True)
    files = ['evaluation/experiment/cases.json', 'evaluation/maintenance_audit/plan.md',
             'app.py', 'data/cards/cards.jsonl', 'data/index/bm25.json',
             'sources/source_manifest.json'] + [str(p.relative_to(ROOT)).replace('\\', '/') for p in sorted((ROOT/'src').glob('*.py'))]
    manifest = {'date': '2026-10-28', 'scope': 'Current-release maintenance smoke audit; original experiment unchanged.',
                'model': configured_model_name(), 'settings': SETTINGS,
                'sha256': {name: digest(ROOT/name) for name in files}}
    (FOLDER/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
    cases = json.loads((ROOT/'evaluation/experiment/cases.json').read_text())['cases']
    previous = None
    for index, case in enumerate(cases):
        for mode in (('baseline', 'improved') if index % 2 == 0 else ('improved', 'baseline')):
            if previous is not None:
                remaining = 65-(time.monotonic()-previous)
                while remaining > 0:
                    time.sleep(min(15, remaining))
                    remaining = 65-(time.monotonic()-previous)
            for name, expected in manifest['sha256'].items():
                if digest(ROOT/name) != expected:
                    raise SystemExit('Source/input changed during audit: '+name)
            previous = time.monotonic()
            record = recommend(case['patient'], mode=mode)
            record.update(case_id=case['case_id'], audit='maintenance-2026-10-28',
                          audit_manifest_sha256=digest(FOLDER/'manifest.json'))
            (destination/(case['case_id']+'_'+mode+'.json')).write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
            print(json.dumps({'case': case['case_id'], 'mode': mode, 'status': record['status'],
                              'seconds': record['timing_seconds']['total'], 'errors': record['errors']}), flush=True)
            if record['status'] != 'completed':
                raise SystemExit('First failure preserved; stopped without retry or fallback.')


if __name__ == '__main__':
    main()
