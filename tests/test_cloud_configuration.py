"""Cloud configuration only: no network calls or real credentials."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from streamlit.errors import StreamlitSecretNotFoundError
from src import gemini, groq_api


class CloudConfigurationTests(unittest.TestCase):
    def test_cloud_store_used_without_local_file(self):
        cloud={'model':{'provider':'groq','name':groq_api.DEFAULT_MODEL},
               'groq':{'api_key':'FAKE_CLOUD_TEST_KEY','free_tier_confirmed':True}}
        with tempfile.TemporaryDirectory() as folder, patch.object(gemini,'SECRETS',Path(folder)/'missing.toml'), patch('streamlit.runtime.secrets.Secrets.to_dict',return_value=cloud):
            self.assertEqual(gemini.configuration(),cloud)
            self.assertEqual(groq_api.credentials(),('FAKE_CLOUD_TEST_KEY',groq_api.DEFAULT_MODEL))

    def test_local_configuration_keeps_precedence(self):
        with tempfile.TemporaryDirectory() as folder:
            file=Path(folder)/'local.toml'
            file.write_text('[model]\nprovider="groq"\nname="qwen/qwen3.8-27b"\n')
            with patch.object(gemini,'SECRETS',file), patch('streamlit.runtime.secrets.Secrets.to_dict') as cloud:
                self.assertEqual(gemini.configuration()['model']['provider'],'groq')
                cloud.assert_not_called()

    def test_absent_cloud_secrets_fail_closed(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(gemini,'SECRETS',Path(folder)/'missing.toml'), patch('streamlit.runtime.secrets.Secrets.to_dict',side_effect=StreamlitSecretNotFoundError('No secrets')), patch.object(groq_api,'request') as network:
            self.assertEqual(gemini.configuration(),{})
            with self.assertRaisesRegex(RuntimeError,'Confirm Groq Free plan'):
                groq_api.chat([], {})
            network.assert_not_called()

    def test_cloud_key_without_confirmation_cannot_generate(self):
        cloud={'model':{'provider':'groq','name':groq_api.DEFAULT_MODEL},
               'groq':{'api_key':'FAKE_CLOUD_TEST_KEY','free_tier_confirmed':False}}
        with tempfile.TemporaryDirectory() as folder, patch.object(gemini,'SECRETS',Path(folder)/'missing.toml'), patch('streamlit.runtime.secrets.Secrets.to_dict',return_value=cloud), patch.object(groq_api,'request') as network:
            with self.assertRaisesRegex(RuntimeError,'Confirm Groq Free plan'):
                groq_api.chat([], {})
            network.assert_not_called()

