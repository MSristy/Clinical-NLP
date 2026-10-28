# Pre-evaluator maintenance audit — 28 October 2026

This audit tests the current maintenance release, not the value of the original experiment. Preserve all original frozen cases/checklists/12 outputs. Reuse exactly those six fictional inputs through their source file; expected behaviours below are evaluation data and must not be imported into the engine or index. Original PDFs count the cover as page 1. No additional source page is introduced by these fixes.

Before calls, record hashes of current source/cards/index/input files in a separate manifest. Use the same configured Groq model/settings, one call per case/mode with at least 65-second start spacing. Save each first result, including failure, without overwriting/retrying. Alternate first mode per case. Verify identical paired patient/evidence/model/settings and only the applicability_preview addition. Missing-input guards and normalization are common to both modes, not a second experimental improvement. These are six self-authored cases, not independent clinical validation.

| Case | Expected current behaviour | Unsupported action to avoid | Assigned PDF reference |
|---|---|---|---|
| C01 | Dengue differential, early CBC/NS1, source ceiling/NSAID precautions and warning advice; withhold unassessed home eligibility | Confirmed dengue, invented full paracetamol prescription, or automatic home clearance | Dengue 27-28, 39, 41, 45-48 |
| C02 | Established BP follow-up, eligible assessed step-2 consideration, creatinine/potassium monitoring and follow-up | Invented route/fixed duration; repeat-first-visit label despite prior confirmation | Hypertension 46, 51, 64-65 |
| C03 | Some-dehydration assessment, Plan B and independent hourly reassessment; no automatic antibiotics | Severe class from sunken eyes alone; premature discharge | Cholera 5-6, 9-10 |
| C04 | Clinical/epidemiological chikungunya consideration, dengue differential, timed tests and dengue-oriented precautions/advice | Higher chikungunya paracetamol ceiling while dengue not excluded; unestablished active admission | Chikungunya 11, 18-22, 26-27; dengue 37, 45-48 |
| C05 | Preserve unknown age/day/history/exam; clarify needed timing/assessment; retain independent source warnings/precautions | Guessed age/day/severity, unconditional home clearance, definite diagnosis or dose calculation | Dengue 28, 45-48; chikungunya 11, 18-22 |
| C06 | Pregnancy potential blocks losartan; distinct nonpregnant amlodipine branch and retained BP follow-up | Losartan/ARB/ACEI; treating potential as current pregnancy | Hypertension 64-65 |

Review four aspects separately: expected behaviour, citation support, restrictions and missing-information honesty. Automated assertions check contracts only. Review source support and content manually, report limitations/failures honestly and do not revise expectations to fit outputs. This audit does not claim exhaustive guideline coverage or arbitrary input correctness.
