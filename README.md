# Clinical NLP

**Live assessment interface:** https://clinical-nlp-msristy.streamlit.app/ — public access without an evaluator login. [Input/output instructions and access notes](docs/hosted-evaluation-instructions.md). Hosted Baseline and Improved model generation verified on 28 October 2026. Free-tier quotas and Cloud cold starts may cause delays.

Post-comparison retrieval maintenance (2026-10-23): 10 cards is a maximum, not a target. Explicit English negative/unknown clauses are excluded from search text, positive source-authored symptom anchors are required, and category coverage never pads with unrelated/zero-score cards. Zero relevant cards displays Insufficient evidence and skips the model call. Raw patient information remains unchanged. The complete software suite passes 49 tests. This limited heuristic is not comprehensive NER or clinical validation. The original 12-output experiment and its results are unchanged and apply to the original 19 source files preserved exactly in evaluation/experiment/frozen-source.zip. A separate maintenance-release.json verifies current runtime hashes; this maintenance release has not undergone a new paired model comparison.

Post-experiment branding release: the project and repository are now **Clinical NLP** / **MSristy/Clinical-NLP**. The clinical corpus/index, six frozen inputs/checklists, original freeze manifest and twelve saved outputs are unchanged. `evaluation/experiment/branding-amendment.json` records exact reversible substitutions for the renamed app labels, download filename, component docstring and transport label, plus the integrity adapter. Verification reconstructs original frozen bytes rather than pretending the renamed runtime existed before the experiment. Interactive Baseline/Improved remain runnable; the historical batch runner requires a separately versioned plan/freeze for new calls. The post-rename suite has **40 passing tests**, including rejection of unrelated runtime/case changes. Existing local workspace-path references remain literal paths, not display branding.

Interactive Streamlit guideline assistant for fictional assessment patients. Existing Groq-hosted Qwen 3.8 27B selects source-backed recommendations; no training is performed.

Approved interface update: a compact sidebar with a sun/moon appearance button switches between White and Black themes. The three-stage workflow guide, native patient form, four result categories and source evidence retain the same clinical behavior. Local presentation assets are in `ui/`; include this folder when copying the application. The backend, model configuration, canonical corpus/index and historical experiment outputs are unchanged. All 49 existing software tests passed; appearance switching also preserved patient information and the retrieved record without a model call.

## Status and scope

Q1 contains 32 canonical cards across the four supplied protocols. Original PDFs, assigned-page extraction/rendering, source IDs and PDF positions are retained. Q2's light guided interface and two runnable modes are implemented. Q2 continued is complete: frozen cases/checklists, 12 fresh paired outputs, source-reviewed verdicts, compact table and a 392-word comparison note are under `evaluation/experiment/`. Result: both modes 23/24 checks and 5/6 cases passing all four; the preview did not demonstrate net benefit and used 708 extra input tokens. Do not interpret software completion or self-authored case checks as independent clinical validation. Training, ASR/NER training and hospital integration remain outside scope; the hosted assessment demo was added for the follow-up evaluation request, without production deployment claims.

## System architecture (Question 3)

![Complete Clinical NLP architecture: implemented components, optional tested preview and future integrations](docs/architecture.svg)

Teal boxes are implemented; orange is the tested pre-model preview; purple boxes/dashed connections are future NER, doctor acceptance, prescription draft and governed feedback design. The app implements neither NER nor a signed prescription workflow. Full Q3 explanation, architectural defence, patient-detail example and cost trade-off: [master documentation, section 18](docs/project-documentation.md#18-question-3-complete-system-architecture). [PNG preview](docs/architecture.png), [editable Mermaid](docs/architecture.mmd); regenerate using `python scripts/render_architecture.py` (Pillow, Windows Segoe UI fonts in the current authoring environment). The diagram shows the current maintenance retrieval gate; original experiment results apply to the archived source snapshot.

## Install and launch

For the follow-up hosted evaluation, see [Community Cloud deployment](docs/deployment.md). Cloud configuration uses private Streamlit secrets when the existing local file is absent; clinical/model behavior is retained. Public root-page access and real generation in both modes have been verified; this smoke test does not replace the original experiment.

For a new checkout:

```powershell
git clone https://github.com/MSristy/Clinical-NLP.git
cd Clinical-NLP
```

From the project root in PowerShell (create the environment only if absent):

```powershell
if (-not (Test-Path .venv)) { python -m venv .venv }
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts/build_index.py
```

Use [Groq API Keys](https://console.groq.com/keys) with **Free ($0), Current Plan**, without adding a payment method or upgrading. Save the key only in `.streamlit/secrets.toml`, which is ignored by Git. For a fresh checkout, copy `.streamlit/secrets.toml.example` only if the actual file does not exist. Never put a real key in the example, chat, screenshots or submission.

```toml
[model]
provider = "groq"
name = "qwen/qwen3.8-27b"

[groq]
api_key = "YOUR_KEY_IN_LOCAL_FILE_ONLY"
free_tier_confirmed = true
```

Set the confirmation flag only after checking the Free plan/no payment setup. The app cannot inspect account billing. It has no upgrade action or automatic paid/provider fallback.

```powershell
python scripts/check_runtime.py
python -m streamlit run app.py --server.address 127.0.0.1 --browser.gatherUsageStats false
```

Open [the local app](http://127.0.0.1:8501). The health endpoint is `http://127.0.0.1:8501/_stcore/health`. Localhost works on this computer while the server is running; public hosting is not required by the assessment.

## Using the interface

1. Enter symptoms in the default **Guided form**. Basics, History & medicines and Examination & tests hold the available patient details. No disease label is required. Leave unknown fields empty; use “None” only for assessed absent history/medicines/allergies.
2. Optionally load and edit one of the six fictional examples. **Advanced JSON** supports detailed structured exposure, social context, laboratory values and explicit clinician assessments.
3. **Preview evidence** retrieves source cards without an API generation. **Generate care plan** makes one model request and displays provisional diagnoses/alternatives, investigations with purpose/timing, medication/treatment fields and advice.
4. Choose **Recommendation mode: Baseline or Improved** in Patient workspace. Improved adds the existing source-check status preview before the model decision; all other components stay fixed. Switching mode hides the old result until regeneration. Review inline source title/version/PDF pages and expand conditions/passages. Unknown medicine fields remain **Not specified by source**. Missing patient information produces focused questions; independent supported actions remain available.
5. Patient summary/history stay in the sidebar; **Patient context** shows the exact input used. Changing input hides stale results until regeneration. **Source evidence** and **Run details** separate clinical review from technical details.

Generated records are automatically saved in `evaluation/interactive_runs/` and can be downloaded from Run details. They include input, full original retrieved cards/passages, exact model messages, model response, fact references, derived-field provenance, output and timings. The interface uses `.streamlit/config.toml` and a light palette; JSON editing is optional.

## Recommendation procedure

`data/cards/cards.jsonl` is the only indexed corpus. BM25 uses k1=1.5 and b=0.75; source/corpus SHA256 detects stale indexes. Diagnostic-card scores and their source-authored symptom terms nominate up to two candidate protocols. Only positive-score cards from the nominated protocols with a matching source symptom anchor (or no symptom list) enter category coverage. The primary protocol is prioritized, then secondary differential evidence, with **0 to 10 cards**, without padding. Explicit English negative/unknown clauses are omitted only from search text. No positive diagnostic anchor means no evidence and no model call. Candidate protocols are retrieval choices, not diagnoses. Cases, checklists, expected answers and saved outputs never enter the index or runtime prompt.

The model receives readable canonical actions, applicability/exclusions, medicine fields, purpose/timing/monitoring metadata and source locators. Full supporting passages remain in the original retrieved cards and UI; they are not duplicated in the selection request. The old lossless codec in `src/prompt_transport.py` is historical and no longer used by the active engine.

An individually unresolved card is withheld with an explicit review note, while valid independent actions remain available; no missing question is invented to explain the model's uncertainty. Advice is also retained when its complete AND-prerequisites are entailed by a selected treatment's prerequisites. This source-policy link does not flatten OR, add treatments, or clear extra home-care eligibility conditions.

Known input values are registered as exact F-references. Questions use Q-references restricted to genuinely unknown, card-relevant slots. The model reviews every retrieved card and selects IDs/facts, rather than authoring displayed clinical actions, dosing, patient claims or questions. Python checks reference validity, card coverage and unknown-slot relevance, then renders clinical text from canonical cards and reasons from exact supplied findings.

`src/clinical_context.py` makes documented-history/regimen/adherence aliases, checks explicitly reviewed laboratory names, and compares consistently above/below readings with the clinician-recorded BP target. Each derived value records its input paths and method. Mixed readings, unrecognized regimens and unreviewed laboratory details are not guessed. A checked test does not prove numerical drug eligibility. `src/observed_constraints.py` checks registered observed prerequisites/exclusions, preserves unknowns and applies a source rule when all predicates are explicitly resolved; remaining clinical interpretations still require model/clinician judgment. It does not implement exhaustive free-text normalization or all disease severity pathways.

Investigation fields and medication-monitoring actions have supporting canonical evidence IDs. The losartan pathway's creatinine/potassium monitoring appears in Investigations as well as the medication plan. Doses/routes/frequencies/durations are copied only where the source supplies them. No confirmed diagnosis is invented from a symptom-only presentation.

## Model and free quota

Explicit provider: Groq. Current model: `qwen/qwen3.8-27b`. Requested settings: temperature 0, reasoning disabled (`none`), maximum completion 900 tokens; structured JSON. GPT-OSS 120B was used during development until its daily free quota was exhausted; configuration was explicitly migrated to listed-free Qwen, not switched by runtime fallback. Qwen's account-enforced output allowance is 1,000 tokens/minute, so extended reasoning is disabled rather than consuming it. Prompt version is recorded in every run. Fixed requested settings do not guarantee identical output. A metadata GET alone does not prove generation permission; actual run records verify successful generations.

The verified Free organization lists 8,000 tokens/minute and 200,000/day for this model; actual API responses also enforced separate 7,000 input/1,000 output token allowances per minute. [Current limits](https://console.groq.com/docs/rate-limits) may change. The batch runner starts requests at least 65 seconds apart. Use `--initial-wait-seconds 65` after another recent call. The UI has a session cooldown. Quota/format/network errors stop without automatic retry, upgrade or provider switch; arbitrary long inputs can still exceed the free request budget.

The earlier Google project is Restricted despite its Gemini API being Enabled. It was not fixed by enabling billing; the user explicitly authorized Groq instead. Optional Gemini/Ollama adapters remain historical alternatives selected only by explicit local configuration. Tiny local Qwen outputs were poor; no quality claim is made for them. `.local/` binaries/models are ignored and not required by the active Groq setup.

## Demonstration and checks

Inputs: `evaluation/cases/draft_cases.json`. Source-linked draft checklists: `evaluation/checklists/draft_checklists.json`, read only by validation/evaluation work, never the engine. C01–C04 represent the four protocols; C05 is incomplete/ambiguous. C06 changes only C02's pregnancy-potential flag: the losartan branch should become unavailable while documented BP/history/tests, follow-up and lifestyle needs remain unchanged. Hypertension PDF page 64 supplies the policy.

```powershell
python scripts/validate_cards.py --input data/cards/cards.jsonl
python scripts/validate_cases.py
python -m unittest discover -s tests -v
python scripts/run_baseline.py
python scripts/summarize_development.py
python scripts/audit_q2_development.py
```

`run_baseline.py` makes real API calls and saves `evaluation/baseline_development/C01.json` through `C06.json`. Select a subset with `--case C02 C06`, or use `--patient path/to/patient.json` for a new patient. The batch stops at its first failure. Summarize/audit scripts read saved files without API calls. Summary and targeted requirement audit are in the same folder. A passed development audit addresses specific regressions; it is not final clinical grading or the formal one-improvement experiment. Earlier outputs are preserved under `evaluation/development_trials/`.

If editing source-authored cards, rebuild and validate before indexing:

```powershell
python scripts/build_cards.py
python scripts/validate_cards.py --input data/cards/cards.jsonl
python scripts/build_index.py
```

Current development verification: **34 software tests passed**, canonical 32-card and six-case validation passed, and **46/46 targeted saved-output checks passed**. These six Qwen requests are genuine model generations. After the final source-observation/advice corrections, `scripts/replay_development_policy.py` uniformly reapplied deterministic postprocessing to those exact saved decisions without new API calls. Original requests, responses and generation timings remain intact; replay timing and provenance are recorded separately. Pre-replay copies are retained in `evaluation/development_trials/qwen_before_policy_replay/`. This is development evidence, not a frozen paired experiment or six new model calls under the final policy.

A separate new patient was entered manually through the guided form and generated with the final baseline policy: `evaluation/interactive_runs/20261021T175859123945Z.json`. The live result shows all four output categories, investigation purpose/timing, ORS fields and PDF citations; supplied weight was not requested again. Light-interface screenshots are in `.local/app/q2-light-interface.png` and `.local/app/q2-light-care-plan.png`. These earlier baseline corrections are not the experimental change.

## Q2 two-mode experiment

The sole change is the improved user-context field `applicability_preview`, a compact card/status mapping from the same limited checker already used after selection in both modes. Baseline retains its reasonable evidence/missing-information prompt, source guards and existing BM25 diagnostic-protocol/category ranking; it was not stripped to manufacture an advantage. No extra API call. Model, settings, patient inputs, corpus, retrieval hits/order, schema and renderer are held fixed. This isolates a within-RAG change, not RAG versus no retrieval.

Prespecified plan: `evaluation/experiment/plan.md`. Frozen six inputs/checklists: `evaluation/experiment/cases.json` and `checklists.json`. Freeze timestamp, code/data hashes and model settings: `manifest.json`. No checklist or expected answer is imported into runtime or indexed. Final paired outputs are saved in `evaluation/experiment/outputs/`; these are fresh calls without development-policy replay. Per-case first mode alternates, with 65-second start spacing. Existing outputs are never overwritten by the runner.

```powershell
python scripts/run_comparison.py
python scripts/inspect_comparison.py --case C02 C06
python scripts/report_comparison.py
```

`run_comparison.py` makes 12 real Free-plan requests, checks frozen hashes and exact paired prompt isolation, and stops at the first failure without retry/provider switch. It refuses a nonempty output directory: preserve delivered originals; use a separate clean project copy with an empty experiment output folder for a new replication, and keep its results distinct. `inspect_comparison.py` reads saved records only. `report_comparison.py` requires completed manual source reviews in `manual_reviews.json`; it verifies reviewed output hashes and compiles counts/table without an AI judge or further calls. Evaluation source review is by the assistant against supplied original pages, not independent clinical validation. Frozen checklists must never be edited to fit model outputs.

Delivered experiment artifacts:

- `outputs/C01_baseline.json` through `C06_improved.json`: 12 exact fresh records, with no policy replay.
- `manual_reviews.json`: 48 individual pass/fail/NA decisions with source-linked reasons and reviewed-output SHA256. All checks applicable; NA count is zero.
- `results-table.md` and `results.json`: compact 12-row table, pass/fail/NA denominators, elapsed time, failure notes and cost. Both modes key behaviour 5/6; citations/restrictions/missing-information honesty each 6/6. No matched gains/losses; C05 clarification coverage still fails.
- `comparison-note.md`: 392-word note reporting the negative result, partial conditional-test gain in C05, unchanged raw admission error in C04 prevented by common guards, likely causes/model variability and next test.

Mean elapsed: baseline 1.4882 s, improved 1.5371 s, quota waits excluded. Total input tokens 35,905 versus 36,613; completion tokens 2,516 versus 2,525. One call per case/mode, no added call. A small latency difference from six observations does not establish a performance effect. Source support was reviewed by the assistant against actual source text/diagrams, not inferred solely from valid card IDs. Keep Baseline as the default; the name Improved identifies the experimental variant, not proven superiority. Pre-freeze software suite: 37 tests passed. Subsequent report generation verified all frozen code/data hashes unchanged.

## Documentation and AI assistance

Portal package: the local `submission/` folder and `submission.zip` contain all requested deliverables, including the actual ten-slide offline PPTX, a requirement-to-file map, disclosure and integrity manifests. They are excluded from Git to avoid duplicating the repository and large deck. Preparation passed 37 software tests and offline evidence verification without real API calls. Run `python scripts/verify_submission.py` from the untouched submission folder for a standard-library integrity check. `scripts/build_submission.py` assembles a new snapshot from explicit files and the Canva-exported PPTX in Downloads; it refuses to overwrite an existing submission. The detailed template is `docs/submission-readme-template.md`. The archive is approximately 18 MB; portal upload and interview rehearsal remain the user's steps.

Q4 paper discussion: [256-word summary](docs/paper-summary.txt), [editable ten-slide Canva deck](https://www.canva.com/design/DAHYtmFW57U/o3QoYfGj5_GTCnqDOCQQfg/edit), [content with Bengali rehearsal notes](slides/q4-slide-content.json), and master documentation section 19. Bengali notes and per-slide targets in Canva total ten minutes for manual delivery, followed by a live demonstration. Default animation timing is not the talk schedule. [Delivery metadata](slides/canva-delivery.json) records review/editability limits; Canva account permissions govern access and no public-sharing setting was changed. Paper references distinguish printed journal pages from supplied PDF positions and separate automated ablations from the human simulated study. Bangladesh transfer concerns are stated as inference, not local validation results.

Repository: https://github.com/MSristy/Clinical-NLP (Public), current publishing branch `master`. Changes are uploaded through reviewed commits and `git push`; uploading source code does not host the Streamlit website. A fresh checkout still needs dependencies and its own local API configuration before generation. For later updates, stage the intended files, review `git diff --cached --stat`, run the public-upload check successfully, commit with a descriptive message and push. No background auto-publishing service is configured.

Public source snapshot: original protocol/paper PDFs, rendered page images, temporary files, virtual environments, credentials, local account diagnostics and interactive/development-trial archives remain local and are excluded by `.gitignore`. Canonical cards, extracted assigned-page text, BM25 index, code, development summary outputs and the complete frozen 12-output experiment are included. See `sources/protocols/README.md` for exact source filenames and extraction/render rebuild commands. The app can use the included cards/index without original PDFs. `.gitattributes` preserves exact file bytes so Windows line-ending conversion does not invalidate frozen SHA256 hashes. Do not run `freeze_experiment.py` again to overwrite the delivered experiment.

Before a public commit, stage intended changes and run `python scripts/check_public_upload.py`; it checks staged blobs for local credential values/patterns and byte agreement with the frozen manifest without displaying keys. This is a targeted check, not a guarantee that arbitrary future files contain no sensitive data. Never force-add ignored secret or patient files.

The single narrative master is `docs/project-documentation.md`; the checklist is `docs/requirements-tracker.md`. Current corrections and actual verification results supersede the earlier development history. The assistant helped inspect source evidence, curate cards, author code/documentation, troubleshoot connections and run checks. The user read assigned pages and executed earlier extraction/build commands. Source selection, model interpretation and this small self-authored test set do not establish independent clinical validation.
