"""
=============================================================================
CodeAlpha AI Internship Project 1: Language Translation Tool
Author: CodeAlpha Intern
Description: A full-stack web application for translating text between 
             multiple languages using real-time translation APIs.
Backend: Python (Flask) with fallback translation engines.
=============================================================================
"""

import os
import logging
import requests
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Optional fallback engine: deep-translator
try:
    from deep_translator import GoogleTranslator
    HAS_DEEP_TRANSLATOR = True
except ImportError:
    HAS_DEEP_TRANSLATOR = False

# AI Language Detection engine: langdetect
try:
    from langdetect import detect as detect_lang_code
    HAS_LANGDETECT = True
except ImportError:
    HAS_LANGDETECT = False

# -----------------------------------------------------------------------------
# 1. Environment & Application Configuration
# -----------------------------------------------------------------------------
# Load environment variables from .env file (keeps secrets secure & out of git)
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing for API flexibility

# Security & Port settings from environment variables
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "codealpha-default-dev-key")
PORT = int(os.getenv("PORT", 5000))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1", "t")

# API Keys and Credentials from .env
MYMEMORY_EMAIL = os.getenv("MYMEMORY_EMAIL", "").strip()
TRANSLATION_API_KEY = os.getenv("TRANSLATION_API_KEY", "").strip()

# Configure logging for monitoring and debugging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# 2. Supported Languages Catalog
# -----------------------------------------------------------------------------
# Dictionary of ISO 639-1 language codes mapped to their display names
SUPPORTED_LANGUAGES = {
    "auto": "Auto Detect",
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "hi": "Hindi",
    "zh": "Chinese (Simplified)",
    "ar": "Arabic",
    "ru": "Russian",
    "pt": "Portuguese",
    "ja": "Japanese",
    "it": "Italian",
    "ko": "Korean",
    "tr": "Turkish",
    "nl": "Dutch",
    "pl": "Polish",
    "sv": "Swedish",
    "ur": "Urdu",
    "bn": "Bengali",
    "ta": "Tamil",
    "te": "Telugu",
    "mr": "Marathi",
    "id": "Indonesian",
    "vi": "Vietnamese",
    "th": "Thai",
    "el": "Greek",
    "cs": "Czech",
    "ro": "Romanian",
    "hu": "Hungarian",
    "da": "Danish",
    "fi": "Finnish",
    "uk": "Ukrainian",
    "fa": "Persian",
    "he": "Hebrew",
    "no": "Norwegian"
}

# -----------------------------------------------------------------------------
# 3. Translation Engine Logic (Real API with Graceful Fallback)
# -----------------------------------------------------------------------------
def translate_via_mymemory(text: str, source_lang: str, target_lang: str) -> str:
    """
    Translates text using the official MyMemory Translation API.
    MyMemory is a free, real translation memory service.
    
    API Docs: https://mymemory.translated.net/doc/spec.php
    """
    # If source is set to 'auto', default to 'en' or let MyMemory auto-pair
    src = "en" if source_lang == "auto" else source_lang
    langpair = f"{src}|{target_lang}"
    
    endpoint = "https://api.mymemory.translated.net/get"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 CodeAlphaTranslator/1.0"
    }
    
    params = {
        "q": text,
        "langpair": langpair
    }
    
    # Optional parameters from .env for higher rate limits (up to 50k chars/day)
    # Filter out dummy/example placeholder emails to prevent 504 gateway timeouts
    email_to_use = MYMEMORY_EMAIL if (MYMEMORY_EMAIL and "@" in MYMEMORY_EMAIL and not MYMEMORY_EMAIL.endswith("example.com")) else None
    if email_to_use:
        params["de"] = email_to_use
    if TRANSLATION_API_KEY:
        params["key"] = TRANSLATION_API_KEY

    try:
        response = requests.get(endpoint, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
    except (requests.exceptions.HTTPError, requests.exceptions.Timeout) as initial_err:
        # If request with email/key failed, attempt retry once without custom credentials
        if "de" in params or "key" in params:
            logger.warning(f"MyMemory request with credentials failed ({initial_err}). Retrying with default endpoint...")
            params.pop("de", None)
            params.pop("key", None)
            response = requests.get(endpoint, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
        else:
            raise initial_err
    
    status_code = data.get("responseStatus")
    response_data = data.get("responseData", {})
    translated_text = response_data.get("translatedText")

    # Check for quota or API error status
    if status_code != 200:
        error_msg = data.get("responseDetails", "Translation provider returned an error.")
        raise RuntimeError(f"MyMemory error ({status_code}): {error_msg}")
        
    if not translated_text:
        raise ValueError("Received empty translation response from MyMemory API.")

    return translated_text


def translate_via_google_fallback(text: str, source_lang: str, target_lang: str) -> str:
    """
    Fallback translation engine using GoogleTranslator via deep-translator.
    Useful when MyMemory daily limit is reached or for advanced auto-detection.
    """
    if not HAS_DEEP_TRANSLATOR:
        raise RuntimeError("deep-translator is not installed.")
        
    src = "auto" if source_lang == "auto" else source_lang
    translator = GoogleTranslator(source=src, target=target_lang)
    translated = translator.translate(text)
    
    if not translated:
        raise ValueError("Received empty response from Google Translator.")
        
    return translated


def detect_source_language(text: str) -> str:
    """
    Detects the source language code using langdetect.
    Returns standard 2-letter ISO code or defaults to 'en'.
    """
    if not HAS_LANGDETECT:
        return "en"
    try:
        detected = detect_lang_code(text)
        # Normalize code (e.g. 'zh-cn' -> 'zh')
        code = detected.split("-")[0].lower()
        if code in SUPPORTED_LANGUAGES and code != "auto":
            return code
        return "en"
    except Exception as e:
        logger.warning(f"Language detection notice: {e}. Defaulting to 'en'.")
        return "en"


def execute_translation(text: str, source_lang: str, target_lang: str) -> dict:
    """
    Coordinates translation across providers with automatic language detection and fallback.
    Returns dictionary with translated text, detected source language (if auto), and provider used.
    """
    actual_source = source_lang
    detected_code = None

    # Handle Auto-Detect
    if source_lang == "auto":
        detected_code = detect_source_language(text)
        actual_source = detected_code
        logger.info(f"Auto-detected language '{detected_code}' for input text.")

    # If source and target are identical, return input directly
    if actual_source == target_lang:
        detected_name = SUPPORTED_LANGUAGES.get(actual_source, actual_source.upper())
        provider_name = f"Direct Match ({detected_name})" if source_lang == "auto" else "direct_match"
        return {
            "translatedText": text,
            "provider": provider_name,
            "detectedSource": actual_source if source_lang == "auto" else None
        }

    # 1. Attempt Primary Provider: MyMemory
    try:
        logger.info(f"Attempting translation via MyMemory ({actual_source} -> {target_lang})")
        result = translate_via_mymemory(text, actual_source, target_lang)
        detected_name = SUPPORTED_LANGUAGES.get(actual_source, actual_source.upper())
        provider_name = f"MyMemory API (Detected: {detected_name})" if source_lang == "auto" else "MyMemory API"
        return {
            "translatedText": result,
            "provider": provider_name,
            "detectedSource": actual_source if source_lang == "auto" else None
        }
    except Exception as e_mymemory:
        logger.warning(f"MyMemory translation failed: {e_mymemory}. Trying fallback engine...")

        # 2. Attempt Fallback Provider: Google Translator
        try:
            result = translate_via_google_fallback(text, actual_source, target_lang)
            detected_name = SUPPORTED_LANGUAGES.get(actual_source, actual_source.upper())
            provider_name = f"Google Translator (Detected: {detected_name})" if source_lang == "auto" else "Google Translator"
            return {
                "translatedText": result,
                "provider": provider_name,
                "detectedSource": actual_source if source_lang == "auto" else None
            }
        except Exception as e_google:
            logger.error(f"Fallback translation also failed: {e_google}")
            # Raise descriptive error explaining the root cause
            raise RuntimeError(
                f"Translation failed across all providers. Details: {str(e_mymemory)} | Fallback: {str(e_google)}"
            )

# -----------------------------------------------------------------------------
# 4. Web & API Routes
# -----------------------------------------------------------------------------
@app.route("/")
def index():
    """Serves the main application user interface."""
    return render_template("index.html")


@app.route("/api/languages", methods=["GET"])
def get_languages():
    """
    API endpoint returning the supported language map.
    Frontend fetches this dynamically to populate the dropdowns.
    """
    return jsonify({
        "success": True,
        "languages": SUPPORTED_LANGUAGES
    }), 200


@app.route("/api/translate", methods=["POST"])
def translate():
    """
    Main Translation API endpoint.
    Expects JSON payload:
    {
        "text": "Hello world",
        "source": "en",
        "target": "es"
    }
    """
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({
                "success": False,
                "error": "Invalid request body. Expected JSON data."
            }), 400

        text = data.get("text", "").strip()
        source_lang = data.get("source", "auto").strip().lower()
        target_lang = data.get("target", "").strip().lower()

        # Validation 1: Text presence
        if not text:
            return jsonify({
                "success": False,
                "error": "Please enter text to translate."
            }), 400

        # Validation 2: Maximum length check (prevents buffer overload and API throttling)
        if len(text) > 5000:
            return jsonify({
                "success": False,
                "error": "Text exceeds maximum limit of 5,000 characters."
            }), 400

        # Validation 3: Target language specified and valid
        if not target_lang:
            return jsonify({
                "success": False,
                "error": "Please select a target language."
            }), 400

        if target_lang not in SUPPORTED_LANGUAGES or target_lang == "auto":
            return jsonify({
                "success": False,
                "error": f"Target language '{target_lang}' is not supported."
            }), 400

        # Validation 4: Source language validity
        if source_lang not in SUPPORTED_LANGUAGES:
            return jsonify({
                "success": False,
                "error": f"Source language '{source_lang}' is not supported."
            }), 400

        # Perform translation
        translation_outcome = execute_translation(text, source_lang, target_lang)

        return jsonify({
            "success": True,
            "translatedText": translation_outcome["translatedText"],
            "source": source_lang,
            "target": target_lang,
            "detectedSource": translation_outcome.get("detectedSource"),
            "provider": translation_outcome["provider"]
        }), 200

    except requests.exceptions.Timeout:
        logger.error("Translation request timed out.")
        return jsonify({
            "success": False,
            "error": "Translation service timed out. Please check your internet connection and try again."
        }), 504

    except requests.exceptions.ConnectionError:
        logger.error("Network connection error to translation service.")
        return jsonify({
            "success": False,
            "error": "Unable to connect to translation server. Please check your internet connection."
        }), 503

    except Exception as e:
        logger.exception("Unexpected error during translation.")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint to verify backend status."""
    return jsonify({
        "status": "healthy",
        "service": "CodeAlpha Language Translation Tool",
        "has_fallback_engine": HAS_DEEP_TRANSLATOR
    }), 200


# -----------------------------------------------------------------------------
# 5. Application Entry Point
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 60)
    print(f" CodeAlpha AI Internship - Language Translation Tool")
    print(f" Server running at: http://127.0.0.1:{PORT}")
    print("=" * 60)
    app.run(host="0.0.0.0", port=PORT, debug=FLASK_DEBUG)
