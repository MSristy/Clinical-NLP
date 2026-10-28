# Streamlit Community Cloud deployment

Live interface: https://clinical-nlp-msristy.streamlit.app/

Deployed on 28 October 2026 using Python 3.12. Anonymous root-page access and genuine hosted C01 model generations in both modes were verified. See [evaluator instructions and email draft](hosted-evaluation-instructions.md) for access, test steps and precise verification limits. GitHub and localhost links alone are insufficient for remote evaluation.

Use the existing public `MSristy/Clinical-NLP` repository, `master`, root `app.py`, with Python 3.12 or another supported version. All runtime cards/index, fictional examples and local UI assets are tracked. No original PDFs or Windows fonts are needed to run the interface. Fonts are used only by the offline architecture renderer. `requirements.txt` pins the existing dependencies.

In Community Cloud Advanced settings, privately configure only these sections (replace the placeholder locally; do not commit a real key):

```toml
[model]
provider = "groq"
name = "qwen/qwen3.8-27b"

[groq]
api_key = "YOUR_OWN_GROQ_KEY"
free_tier_confirmed = true
```

Set confirmation true only after verifying a Free account/no payment setup. Quota is provider-controlled; no paid upgrade/fallback is implemented. Existing local `.streamlit/secrets.toml` retains precedence. When it is absent, the app reads Streamlit's private secrets store. Missing settings or missing confirmation stop generation before the API call. No credentials are included in GitHub or evaluator instructions. Never share the Groq API key as an evaluator login.

Choose public app sharing for evaluator access without an app login. The app is a fictional assessment prototype; enter only fictional data. Model selection, clinical cards, both recommendation modes, prompts and shared checks are unchanged. The stored historical 12-call experiment is not rerun or regraded by deploying.

After launch, verify: public page loads; six examples and new input work; preview retrieves source evidence; both modes produce genuine model responses; citations and missing-information warnings appear; a zero-evidence case skips the API; patient context and downloads work. A metadata check alone is not proof of a successful generation. Space fresh generations to respect the displayed free-plan cooldown and provider quota. Community Cloud can sleep; interactive run files on the host are not permanent storage, so download records you need.

Official setup: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy

Private secrets: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management
