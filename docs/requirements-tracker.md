# Clinical NLP Progress Tracker

Current maintenance verification: Post-comparison retrieval maintenance (2026-10-23): 10 cards is a maximum, not a target. Explicit English negative/unknown clauses are excluded from search text, positive source-authored symptom anchors are required, and category coverage never pads with unrelated/zero-score cards. Zero relevant cards displays Insufficient evidence and skips the model call. Raw patient information remains unchanged. The complete software suite passes 49 tests. This limited heuristic is not comprehensive NER or clinical validation. The original 12-output experiment and its results are unchanged and apply to the original 19 source files preserved exactly in evaluation/experiment/frozen-source.zip. A separate maintenance-release.json verifies current runtime hashes; this maintenance release has not undergone a new paired model comparison.

Branding update: Clinical NLP, GitHub MSristy/Clinical-NLP. App, card-schema title, docs, architecture and Canva/PPTX branding updated. Original clinical corpus/index, cases/checklists, freeze manifest and twelve outputs are unchanged. A separate reversible branding amendment accounts for renamed runtime bytes; 40 post-rename tests passed. The submission folder/ZIP are rebuilt from the renamed release. Working-directory paths remain literal for the existing environment.

Current milestone: Q1 and Q2 implementation/experiment package completed for the current assessment scenarios. Two modes in one app; 37 software tests passed. Six unchanged inputs and source-linked checklists frozen BEFORE the 12 fresh comparison calls; code/data hashes and exact pair isolation verified. Assistant source review: Baseline 23/24 checks and 5/6 all-four-pass cases; Improved 23/24 and 5/6, with 708 extra input tokens and no extra calls. C05 key-behaviour failure remains in both; no net improvement demonstrated. Complete table/manual reasons/392-word comparison note are in evaluation/experiment/. These self-authored cases are not independent clinical validation. Prior development outputs/replay remain separate. Free model: Qwen 3.8 27B, temperature 0, reasoning none, max completion 900; maximum 10 retrieved cards. Google remains Restricted; no billing enabled. Q3 architecture and design defence are complete (master section 18). Q4 includes a 256-word summary and ten-slide editable Canva deck with Bengali notes and ten-minute timing targets (master section 19). Portal-ready submission folder and ZIP are prepared and checked, with the actual offline PPTX, 37 passing package tests and unchanged frozen evidence (master section 20). User upload, rehearsal and live demonstration remain pending.

- [x] 01. Verify VS Code interpreter, folders and Python environment setup
- [x] 02. Collect correct protocol editions and register sources
- [x] 03. Review assigned 45 pages, tables, footnotes and hypertension algorithm
- [x] 04. Prepare source-linked evidence notes
- [x] 05. Define canonical card schema and field explanations (schema v1.0; user-run validation passed)
- [x] 06. Compare two representations of a complex recommendation and implement one (structured conditions selected; limited source-condition runtime checks now implemented)
- [x] 07. Create and verify cards covering all four protocols and output categories (Q1 source/coverage audit completed; user rebuilt and validated revised 32-card package successfully)
- [x] 08. Create six fictional patient cases including a single-prerequisite modification; original development drafts retained, authoritative final experiment copies frozen in evaluation/experiment/
- [x] 08a. Preserve original input, null/false/assessed-empty distinctions, exact fact references and traceable limited clinical normalization; no exhaustive free-text extraction claim
- [x] 08b. Implement limited three-state observed prerequisite/exclusion checks and source-advice links as baseline corrections; unresolved clinical interpretations retain model/clinician review
- [x] 09. Build RAG index and reproducible rebuild script (32 canonical cards only; hash freshness check and retrieval tests passed)
- [x] 10. Working explicit Groq Free connection: qwen/qwen3.8-27b, temperature 0, reasoning none, max completion 900; six successful real development generations and an independent new-input live UI generation. Quota-limited; no automatic fallback or deterministic guarantee
- [x] 11. Light guided editable UI; fix identified investigation retrieval/purpose/timing, unsupported reason text, supplied-fact questions and omitted dependent advice. Four ordinary cases cover all four output categories. Inline citations, exact patient context, medication fields and missing information visible; 46/46 targeted saved-output checks passed
- [x] 12. Add one improvement: pre-model applicability preview only; same model/corpus/retrieval/guards. Prespecified hypothesis/falsifier/cost in evaluation/experiment/plan.md; 37 software tests passed
- [x] 13. Functional development tests: 34 software tests passed; final new guided-form patient generated all four output categories, purpose/timing, medicine table and source references. Exact 55 kg weight retained, not asked again. Run: evaluation/interactive_runs/20261021T175859123945Z.json. Clinical interpretation is not independently validated
- [x] 14. Freeze six unchanged cases and source-linked expected checklists before final comparison; 22 Oct 2026 00:58:49 Asia/Dhaka, 19 files hashed in evaluation/experiment/manifest.json
- [x] 15. Save 12 fresh final outputs with full evidence, exact requests/responses, settings, timings and freeze-manifest hash; no replay, retries or replaced failure
- [x] 16. Source-review all four checks for each output; manual_reviews.json holds verdicts/reasons/PDF pages and exact output hashes. results-table.md/results.json report denominators and honest C05 failures
- [x] 17. Write 392-word one-page comparison note plus separate table; report unchanged/worse cost, C05 partial gain/remaining failure, raw C04 weakness, model variability and next test
- [x] 18. Q3 complete architecture diagram (SVG/PNG/Mermaid), implemented/future labels, pre-model tested-preview location, source-ID flow, patient-detail counterfactual, design defence and cost trade-off; future NER/doctor acceptance/feedback/prescription connections are design only. See master section 18
- [x] 19. Read assigned paper and write 200-300-word summary with referenced result and Bangladesh transfer limitation. 256-word summary in docs/paper-summary.txt; Figure 2 and Extended Data Table 2 checked, including hallucination trade-off. Master section 19 records sources and inference boundaries
- [x] 20. Prepare 5-10 slides and approximately 10-minute presentation. Actual ten-page Canva deck created and reviewed; Bengali presenter notes, sources and manual-delivery targets total 600 seconds. Link/review metadata in slides/canva-delivery.json, content backup in slides/q4-slide-content.json. User rehearsal/live demonstration still pending
- [x] 21a. Q2 README launch/rebuild instructions, current model/settings, replay caveat and AI assistance disclosure
- [x] 21. Complete whole-assessment submission README/disclosure and requirement map. Portal package builder includes actual offline Canva PPTX, all requested evidence and runnable code, with credential exclusions and package/frozen hashes. Final performed checks are recorded in submission/submission-validation.json
- [x] 22a. Verify copied submission without real credentials: 37 tests, card/case checks, saved experiment verification, 19 frozen hashes, 12 reviewed outputs, 10 slides/notes and ZIP integrity passed; zero real API calls during packaging
- [ ] 22. User uploads archive, rehearses the ten-minute presentation and performs the interview/live demonstration




- [x] Care-plan no-evidence display retains four categories and the existing empty-recommendation message.

- [x] Local visual redesign preview implemented and checked (49 existing tests; backend/widget contract unchanged; desktop/tablet/mobile reviewed).
- [ ] User visual approval, then GitHub publication and submission refresh for the redesigned interface. Prior approved submission and remote remain unchanged.

- [x] User approved the redesigned interface for GitHub publication, including White/Black icon and corrected workflow spacing. Backend and historical experiment evidence remain unchanged.

- [x] Minimal flat submission_assessment prepared: 31 files, no subfolders; required deliverables only, runnable flat imports/paths verified, 12 original outputs combined without changing values, no private keys.

- [x] User approved the concise visual architecture for GitHub; repository SVG/PNG/Mermaid and renderer updated to match the flat submission diagram.

- [x] Hosted-evaluation preparation authorized; Cloud secrets fallback added without changing clinical/model behavior; 53 tests pass; metadata accessible.
- [x] Public deployment at https://clinical-nlp-msristy.streamlit.app/; anonymous root-page HTTP 200 and genuine hosted C01 Baseline/Improved model generations verified; downloadable records retained locally and evaluator instructions/email draft prepared. Historical comparison unchanged.
- [ ] User sends the verified hosted URL/instructions to the assessors by the requested deadline; no email/form submitted by the assistant.
