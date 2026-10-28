# Clinical NLP: hosted evaluation

Live interface: https://clinical-nlp-msristy.streamlit.app/

Access: public interface; no evaluator login, password or provider API key is required. The provider credential is stored privately on the server. Use fictional patient information only.

1. Choose **Baseline** or **Improved** in the sidebar.
2. Select one of the six fictional examples and click **Load example**, or click **New patient** and enter a new case. Supply symptoms, illness duration and available age, sex, history, current medicines, allergies, examination and tests. A disease name is not required. Unknown values can remain unknown. **Advanced JSON** is an alternative editable input method.
3. **Preview evidence** retrieves the canonical source cards without requesting a model response. **Generate care plan** makes the live Groq request when relevant source evidence exists.
4. Read the four care-plan categories: probable diagnoses/alternatives, investigations, medication/treatment planning and advice. Each selected recommendation includes source references; missing patient details and unavailable medicine fields are identified.
5. **Source evidence** shows retrieved cards and supporting passages/pages; **Patient context** preserves the information used. **Run details → Download input, plan & evidence** exports the record, including the actual model response.
6. Observe the displayed cooldown before another generation. No matching evidence produces abstention rather than an invented answer. Free provider quotas can temporarily block generation; there is no paid fallback or automatic retry.

Both modes use Groq `qwen/qwen3.8-27b`, temperature 0, reasoning effort none and maximum completion 900 tokens. Improved adds only the pre-model applicability preview. The model still makes imperfect selection judgments; these are provisional assessment outputs requiring clinician review.

The app runs in Streamlit Community Cloud and does not require the developer's computer to remain on. Cloud sleeping/cold starts, platform availability and provider quotas can cause delays; uninterrupted availability is not guaranteed. Host-side interactive files are temporary: download records you need to retain.

## Deployment verification (28 October 2026)

Latest pre-evaluator maintenance audit: source-boundary fixes and 72 software tests, four fresh targeted clarification checks, and final live Baseline/Improved generations on a new non-demo numeric-BP patient have been verified. See [audit findings and precise limits](pre-evaluator-audit.md). Earlier audit failures remain preserved; no independent clinical validation or exhaustive-input correctness is claimed. The original submitted comparison results apply to its archived release.

The root URL returned HTTP 200 without signed-in account cookies or a login redirect. Actual hosted C01 generations completed in both modes, returned Groq responses with finish reason `stop`, and exposed downloadable input/output records. Baseline elapsed 1.3738 seconds; Improved 1.3590 seconds (one observation each, excluding cooldown). Both displayed all four output categories, source references and clarification needs. A new fictional urinary-symptom input returned zero cards and explicit insufficient evidence, with no model request. Offline inspection of the downloaded pair confirmed identical patient/evidence/model/settings and only the added applicability_preview context. This is a deployment smoke test, not a new clinical comparison or accuracy measurement. The original frozen six-case/12-output experiment remains separate and unchanged.

## Ready-to-copy email reply

Dear Md Ridone Khan,

Thank you for your email. Please find the hosted interactive prototype and access instructions below.

**Live interface:** https://clinical-nlp-msristy.streamlit.app/

**Input/output instructions:** Select Baseline or Improved in the sidebar. Load a fictional example or click New patient and enter symptoms, illness duration and available patient details. Click Generate care plan to obtain model-selected, source-linked recommendations. Preview evidence and the result tabs show retrieved protocol evidence, provisional diagnoses, investigations, medication planning, advice and missing-information prompts. The complete input/output record can be downloaded from Run details.

**Access credentials:** No login or password is required. No provider API key is required from evaluators. Both modes have been tested on the hosted interface with live model responses. The app uses a free-tier connection; please observe its displayed cooldown. A cold start or provider quota limit may temporarily delay access or generation.

Please use fictional inputs only. This is an assessment prototype requiring clinician review.

Kind regards,
[Your name]

This draft has not been emailed or submitted to the assessment form by the assistant.
