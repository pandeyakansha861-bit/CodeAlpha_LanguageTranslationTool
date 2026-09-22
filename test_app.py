"""
=============================================================================
Automated Unit and Integration Tests for Language Translation Tool
CodeAlpha AI Internship Project 1
=============================================================================
"""

import unittest
from app import app

class TranslationTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test client before each test."""
        self.client = app.test_client()
        self.client.testing = True

    def test_health_check(self):
        """Verify the health check endpoint returns 200 and healthy status."""
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('has_fallback_engine', data)

    def test_supported_languages_endpoint(self):
        """Verify the languages endpoint lists supported languages."""
        response = self.client.get('/api/languages')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertIn('languages', data)
        self.assertIn('en', data['languages'])
        self.assertIn('es', data['languages'])
        self.assertIn('auto', data['languages'])
        self.assertGreater(len(data['languages']), 20)

    def test_empty_text_validation(self):
        """Verify empty or whitespace-only text returns 400 Bad Request."""
        response = self.client.post('/api/translate', json={
            'text': '   ',
            'source': 'en',
            'target': 'es'
        })
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertFalse(data['success'])
        self.assertIn('error', data)

    def test_missing_payload(self):
        """Verify empty JSON request returns 400."""
        response = self.client.post('/api/translate', data='', content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_invalid_target_language(self):
        """Verify requesting an unsupported target language returns 400."""
        response = self.client.post('/api/translate', json={
            'text': 'Hello world',
            'source': 'en',
            'target': 'invalid_lang_code_xyz'
        })
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertFalse(data['success'])

    def test_identical_source_and_target_optimization(self):
        """Verify matching source and target bypasses external API call."""
        sample_text = "This is a direct bypass test."
        response = self.client.post('/api/translate', json={
            'text': sample_text,
            'source': 'en',
            'target': 'en'
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['translatedText'], sample_text)
        self.assertEqual(data['provider'], 'direct_match')

    def test_real_translation_english_to_spanish(self):
        """Verify authentic translation from English to Spanish via real API."""
        response = self.client.post('/api/translate', json={
            'text': 'Hello world',
            'source': 'en',
            'target': 'es'
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertIn('translatedText', data)
        self.assertIn('Hola', data['translatedText'])
        print(f"\n[API Test Result] 'Hello world' -> '{data['translatedText']}' (Provider: {data.get('provider')})")

    def test_real_translation_english_to_french(self):
        """Verify authentic translation from English to French via real API."""
        response = self.client.post('/api/translate', json={
            'text': 'Good morning',
            'source': 'en',
            'target': 'fr'
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertIn('translatedText', data)
        print(f"[API Test Result] 'Good morning' -> '{data['translatedText']}' (Provider: {data.get('provider')})")

    def test_real_translation_english_to_german(self):
        """Verify authentic translation from English to German via real API."""
        response = self.client.post('/api/translate', json={
            'text': 'Thank you very much',
            'source': 'en',
            'target': 'de'
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertIn('translatedText', data)
        print(f"[API Test Result] 'Thank you very much' -> '{data['translatedText']}' (Provider: {data.get('provider')})")

    def test_real_translation_english_to_hindi(self):
        """Verify authentic translation from English to Hindi via real API."""
        response = self.client.post('/api/translate', json={
            'text': 'Welcome',
            'source': 'en',
            'target': 'hi'
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertIn('translatedText', data)
        # Safely display for Windows console encodings
        safe_preview = data['translatedText'].encode('ascii', errors='backslashreplace').decode('ascii')
        print(f"[API Test Result] 'Welcome' -> {safe_preview} (Provider: {data.get('provider')})")

    def test_auto_detect_translation(self):
        """Verify Auto-Detect identifies language and returns translation with detected source."""
        response = self.client.post('/api/translate', json={
            'text': 'Bonjour tout le monde',
            'source': 'auto',
            'target': 'en'
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data.get('detectedSource'), 'fr')
        self.assertIn('translatedText', data)
        print(f"[API Test Result] Auto-Detect 'Bonjour tout le monde' -> '{data['translatedText']}' (Detected: {data.get('detectedSource')})")

    def test_index_page_serves_html(self):
        """Verify the root endpoint serves the HTML interface."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'CodeAlpha AI Internship', response.data)
        self.assertIn(b'Polyglot AI', response.data)

if __name__ == '__main__':
    unittest.main(verbosity=2)
