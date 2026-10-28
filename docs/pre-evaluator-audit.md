# Pre-evaluator audit — 28 October 2026

This is a maintenance audit of the hosted assessment prototype, not independent clinical validation or a claim that every possible input is correct. The existing Qwen model was not trained on the protocols. Manually curated cards from 45 assigned PDF pages are retrieved by BM25 and supplied to an existing API model for selection. No extra protocol page, model training or source-corpus expansion was introduced in this audit.

## Issues reproduced and corrected

| Finding | Correction and boundary | Source / verification |
|---|---|---|
| Numeric BP without an explicit high-BP phrase returned no cards | Elevated numeric BP supplies a retrieval cue. It does not confirm hypertension or invent prior measurements. Normal/negated BP does not supply this cue. | Hypertension PDF 46; numeric-BP/negation regressions |
| A missing or partially reviewed losartan lab prerequisite could remain unresolved in the final checker | Registered unknown source conditions now withhold the dependent action, including when no new question slot exists. Creatinine and potassium review questions remain separate. Reviewed tests do not prove safe numeric results. | Hypertension PDF 64, Figure 8 and footnotes; pregnancy, adherence, interval, regimen, target and lab counterfactuals |
| Exact named medicine allergy relied on model attention | A supplied matching medicine allergy blocks the whole dependent medicine card. Other independent cards remain possible. No drug-class/cross-reactivity inference is implemented; ambiguous prose still needs clinician review. | Supplied patient restriction and Q2 medication-context requirement; paracetamol allergy regressions |
| Structured hydration findings could remain unresolved or conflict with a model-selected plan | Limited exact sign/phrase aliases implement the source table's danger-sign OR / two-severe-sign rule and some-dehydration conditions. Known danger/severe findings prevent Plan B; conflicting recorded class/signs withhold dependent actions for reconciliation. Missing signs never imply normal hydration. | WHO cholera PDF 5-6, 9-10; 64 fully observed danger/severe combinations, single-sign and conflict regressions |
| Invalid nested JSON could reach clinical processing; non-object JSON could break switching to the guided form | Reject malformed container types and non-finite numeric values; show an actionable input error for non-object JSON. | Input-validation and UI tests |

All corrections are shared by Baseline and Improved. The only mode-specific change remains the pre-model applicability_preview. The 32 cards and BM25 corpus are unchanged. The source table uses explicit assessed findings only; free-text interpretation, disease suspicion and unresolved relevance still depend on the model and clinician.

## Assessment requirement audit

| Requirement | Evidence / status |
|---|---|
| Q1 consistent cards, source metadata/passages, medicine fields | 32 canonical JSONL cards, schema, source registry and index consistency validated. Assigned source title/version/page references retained; unavailable prescription fields remain null. |
| Q1 representation reasoning | docs/q1-card-guide.md compares prose versus structured losartan prerequisites/exclusions, justifies the chosen representation and gives the pregnancy-potential failure scenario. Only the structured option is implemented. |
| Q2 editable new case, no required disease name | Guided form and Advanced JSON; source evidence, patient context, four care-plan categories, citations, missing-information prompts and record export. Numeric BP and no-evidence cases specifically tested. |
| Q2 existing model and indexed RAG | Groq qwen/qwen3.8-27b with fixed settings; canonical-card BM25 index and rebuild command. No paid fallback or training. |
| Six examples, ambiguous and modified inputs | Six original inputs retained, including C02/C06 pregnancy-potential-only difference. Original case/checklist files are not rewritten. |
| Two-mode experiment | Original predeclared plan, frozen 19-file source archive, six source-linked checklists, 12 actual outputs, 48 reviews, compact results table and 392-word note remain intact. Original result is still 23/24 checks and 5/6 all-check passes per mode, with unchanged C05 failure. These scores belong to the original archived release. |
| Q3 architecture | SVG/PNG/Mermaid show preparation, cards/index, input, retrieval, model, shared checks, interface and future NER/doctor acceptance/feedback/prescription connections. Design defence, patient-detail change and cost trade-off are in master section 18. Future components remain design only. |
| Q4 summary/slides | Summary is 256 words. Actual offline PPTX contains 10 slides; editable Canva deck and content/notes are retained. Source Figure 2, Figure 6 and Extended Data Table 2 were checked against the supplied paper. Bengali timing notes total 600 seconds; actual rehearsal/delivery remains the candidate's task. |
| Tools/AI disclosure | docs/ai-assistance-disclosure.md describes substantial Codex assistance, manual curation, tools, API model and the lack of independent clinician validation. |
| Remote evaluator access | Public Streamlit link and unsent English reply/instructions in docs/hosted-evaluation-instructions.md. Private provider key is never an evaluator credential. |

## Verification results

Pre-change suite: 53 tests passed. Post-fix suite: 70 tests passed, including 17 new test methods; the hydration test method contains 64 sign combinations. UI tests also cover invalid JSON recovery; the prompt-data test verifies source actions remain authoritative for instruction-like patient text. These counts are software checks, not patient-level clinical accuracy.

Real current-release model calls are being saved separately under evaluation/maintenance_audit/outputs/, with a prespecified plan and separate source/input hash manifest. The original experiment outputs are not overwritten. Final call/source-review results and hosted release checks are recorded after completion.

## Limits that remain

Only four protocols and selected recommendation coverage are implemented, not every recommendation in all PDFs. Additional pages are not silently incorporated. English lexical retrieval/negation and exact aliases do not provide comprehensive NER, multilingual understanding or temporal/conflict resolution. A matching source citation does not prove an action is appropriate. Complete free-text drug histories may need structured clarification rather than automatic escalation. Unknown numerical lab suitability, diagnostic interpretation and emergency care require clinician judgement. This audit is based on self-authored fictional inputs and AI-assisted source review; it cannot guarantee every evaluator input will pass. Free provider quotas and Cloud sleeping can temporarily block a request. Rehearsal, final email submission and real-world clinical validation remain outside these software checks.
