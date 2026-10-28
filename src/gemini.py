"""Gemini free-tier configuration and REST transport. No billing setup/fallback."""
import json
from pathlib import Path
import tomllib
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
SECRETS = ROOT/'.streamlit/secrets.toml'
DEFAULT_MODEL = 'gemini-3.8-flash'
FREE_MODELS = {'gemini-3.8-flash'}
ENDPOINT = 'https://generativelanguage.googleapis.com/v1beta'
SETTINGS = {'maxOutputTokens': 4096, 'thinkingConfig': {'thinkingLevel': 'LOW'}}


def configuration():
    if SECRETS.exists():
        try:
            with SECRETS.open('rb') as file:
                return tomllib.load(file)
        except tomllib.TOMLDecodeError as exc:
            raise RuntimeError('Local secrets.toml is invalid TOML; check quotation marks and section names.') from exc
    # Community Cloud supplies private settings through Streamlit's secrets store.
    # Preserve the existing local-file path and never merge/fallback providers.
    import streamlit as st
    from streamlit.errors import StreamlitSecretNotFoundError
    try:
        return st.secrets.to_dict()
    except StreamlitSecretNotFoundError:
        return {}  # Existing free-tier/key guards fail closed before any request.


def provider():
    return configuration().get('model', {}).get('provider', 'gemini')


def model_name():
    return configuration().get('model', {}).get('name', DEFAULT_MODEL)


def credentials():
    config = configuration()
    model = config.get('model', {}).get('name', DEFAULT_MODEL)
    if model not in FREE_MODELS:
        raise RuntimeError('This prototype only permits the configured free-tier Gemini model allowlist. No paid model fallback.')
    section = config.get('gemini', {})
    if section.get('free_tier_confirmed') is not True:
        raise RuntimeError('Check that the API-key project shows Free tier with no linked billing, then set free_tier_confirmed = true in local secrets.toml. The app cannot verify your billing account.')
    key = section.get('api_key', '').strip()
    if not key or key == 'PASTE_YOUR_FREE_TIER_KEY_HERE':
        raise RuntimeError('Free-tier API key missing. Add it only to .streamlit/secrets.toml, never to chat or Git.')
    return key, model


def request(path, key, payload=None):
    body = None if payload is None else json.dumps(payload).encode('utf-8')
    req = Request(ENDPOINT+path, data=body, headers={'Content-Type': 'application/json', 'x-goog-api-key': key})
    try:
        with urlopen(req, timeout=180) as response:
            return json.load(response)
    except HTTPError as exc:
        detail = exc.read(2000).decode('utf-8', errors='replace').replace(key, '[REDACTED]')
        if exc.code == 429:
            raise RuntimeError('Free-tier quota/rate limit reached. Stopped; no retry, upgrade or paid fallback. Wait for quota reset.') from None
        raise RuntimeError(f'Gemini HTTP {exc.code}: {detail}') from None
    except (URLError, TimeoutError, OSError):
        raise RuntimeError('Gemini network request failed. No automatic retry or paid fallback.') from None


def model_status():
    status = {'provider': 'gemini', 'model': model_name(), 'endpoint': ENDPOINT,
              'settings': SETTINGS, 'installed': False, 'generation_verified': False,
              'billing_note': 'User must verify Free tier/no linked billing. This app cannot inspect Google billing.',
              'setup_hint': 'Create a free-tier API key, confirm no billing, and edit .streamlit/secrets.toml.'}
    try:
        key, model = credentials()
    except RuntimeError as exc:
        status['setup_hint'] = str(exc)
        return status
    metadata = request('/models/'+model, key)
    status.update(installed=True, model_details=metadata,
                  setup_hint='Model metadata is accessible. A successful real generation is still required to verify generation permission and quota.')
    return status


def chat(messages, schema):
    key, model = credentials()  # Fails closed before any network request.
    status = model_status()
    payload = {'systemInstruction': {'parts': [{'text': m['content']} for m in messages if m['role'] == 'system']},
               'contents': [{'role': 'user' if m['role'] == 'user' else 'model', 'parts': [{'text': m['content']}]}
                            for m in messages if m['role'] != 'system'],
               'generationConfig': {**SETTINGS, 'responseMimeType': 'application/json', 'responseJsonSchema': schema}}
    raw = request('/models/'+model+':generateContent', key, payload)
    candidates = raw.get('candidates', [])
    if not candidates:
        raise RuntimeError('Gemini returned no candidate. No answer was invented; inspect provider restrictions/quota.')
    candidate = candidates[0]
    text = ''.join(part.get('text', '') for part in candidate.get('content', {}).get('parts', []) if not part.get('thought'))
    finish = candidate.get('finishReason', 'UNKNOWN')
    if finish != 'STOP' and finish != 'MAX_TOKENS':
        raise RuntimeError('Gemini did not complete the response: ' + finish)
    status.update(generation_verified=True, model_version=raw.get('modelVersion'))
    usage = raw.get('usageMetadata', {})
    return {'message': {'role': 'assistant', 'content': text}, 'done': True,
            'done_reason': 'length' if finish == 'MAX_TOKENS' else 'stop',
            'prompt_eval_count': usage.get('promptTokenCount'), 'eval_count': usage.get('candidatesTokenCount'),
            'provider_response': raw}, status
