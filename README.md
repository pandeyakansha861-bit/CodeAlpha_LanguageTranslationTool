# CodeAlpha AI Internship - Project 1: Language Translation Tool

An AI-powered, full-stack **Language Translation Web Application** developed for the CodeAlpha Artificial Intelligence Internship. This tool provides real-time, accurate translation between over 30 languages using authentic translation APIs, wrapped in a responsive, modern user interface.

![Project Banner](https://img.shields.io/badge/CodeAlpha-AI%20Internship-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.3+-black?style=for-the-badge&logo=flask&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

---

## 🌟 Key Features

1. **Real Translation API Integration**:
   - Integrated with the official **MyMemory Translation API** with automatic fallback to **Google Translator** engine via `deep-translator`.
   - Zero mock or fake responses; authentic machine translation.
2. **Security & Clean Architecture**:
   - Server-side API proxy prevents exposing sensitive API keys or credentials in client-side code.
   - Secrets managed via `.env` file and excluded from version control via `.gitignore`.
3. **Comprehensive Language Support**:
   - Supports 35+ major world languages (English, Spanish, French, German, Hindi, Mandarin, Arabic, Russian, Japanese, etc.).
   - Includes **Auto Detect** capability for source language.
4. **Interactive Translation Workbench**:
   - **Swap Languages**: Instantly swaps source and target languages as well as text content.
   - **Copy to Clipboard**: One-click copy with visual toast confirmation.
   - **Clear**: Instantly resets inputs and outputs.
   - **Character Counter**: Live tracking up to 5,000 characters.
   - **Keyboard Shortcut**: Quick translation via <kbd>Ctrl</kbd> + <kbd>Enter</kbd> (or <kbd>Cmd</kbd> + <kbd>Enter</kbd>).
   - **Text-to-Speech (Audio Pronunciation)**: Listen to both input and translated text using the Web Speech API.
5. **Modern, Responsive UI**:
   - Crafted with custom CSS variables, sleek glassmorphic card elements, and micro-interactions.
   - 100% responsive across mobile devices, tablets, and desktop displays.
6. **Graceful Error Handling**:
   - Clear and friendly alert banners for empty inputs, unsupported pairs, network timeouts, and API rate limits.

---

## 📂 Project Structure

```
CodeAlpha_LanguageTranslationTool/
│
├── app.py                  # Flask backend server, API routing & translation logic
├── test_app.py             # 12 automated unit and integration tests
├── requirements.txt        # Python package dependencies
├── .env.example            # Environment variables template (safe to commit)
├── .env                    # Local secrets and config (git-ignored)
├── .gitignore              # Ignores .env, virtual environments, and python cache
├── README.md               # Detailed project documentation & evaluation guide
│
├── static/
│   ├── css/
│   │   └── style.css       # Clean, modern, responsive stylesheet
│   └── js/
│       └── app.js          # Client-side logic, API calls, event handlers & TTS
│
└── templates/
    └── index.html          # Semantic HTML5 single-page application interface
```

---

## 🚀 Getting Started & Installation

### Prerequisites
- **Python 3.8+** installed on your system.
- An internet connection for real-time translation API requests.

### Step 1: Clone or Navigate to the Project
```bash
cd CodeAlpha_LanguageTranslationTool
```

### Step 2: Set Up a Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Copy `.env.example` to `.env` (if not already present):
```bash
# Windows (PowerShell)
Copy-Item .env.example .env

# Linux / macOS
cp .env.example .env
```

Open `.env` in any editor to review settings:
- `PORT=5000`: Port where the Flask server runs.
- `MYMEMORY_EMAIL=`: *(Optional)* Providing a valid email gives you a higher daily free quota (up to 50,000 characters/day) on MyMemory API.
- `TRANSLATION_API_KEY=`: *(Optional)* For authenticated or paid tiers.

### Step 5: Run Automated Tests
Execute the comprehensive test suite to verify endpoints, validation rules, and live translations:
```bash
python test_app.py
```

### Step 6: Launch the Web Application
```bash
python app.py
```

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🛠️ API Documentation

### 1. Supported Languages Endpoint
- **URL**: `/api/languages`
- **Method**: `GET`
- **Response**:
```json
{
  "success": true,
  "languages": {
    "auto": "Auto Detect",
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    ...
  }
}
```

### 2. Translate Text Endpoint
- **URL**: `/api/translate`
- **Method**: `POST`
- **Headers**: `Content-Type: application/json`
- **Body**:
```json
{
  "text": "Hello, how are you?",
  "source": "en",
  "target": "es"
}
```
- **Response (Success 200)**:
```json
{
  "success": true,
  "translatedText": "Hola, ¿cómo estás?",
  "source": "en",
  "target": "es",
  "provider": "MyMemory API"
}
```
- **Response (Error 400/500)**:
```json
{
  "success": false,
  "error": "Please enter text to translate."
}
```

---

## 🎓 Internship Evaluation Guide (Q&A)

When presenting this project during your CodeAlpha evaluation, here are key architectural decisions and concepts you can highlight:

### Q1: Why did you choose Python (Flask) for the backend instead of pure frontend API calls?
> **Answer**: Making translation API calls directly from client-side JavaScript exposes sensitive API keys and secrets in the browser's Network tab and source code. Using Flask creates a secure server-side proxy where all secrets are kept safe in `.env`. Additionally, the backend allows us to implement multi-provider fallbacks (MyMemory + Google Translator) and rate-limiting safely.

### Q2: How does the application handle rate limits or network failures?
> **Answer**: In `app.py`, the `execute_translation` function uses a multi-tiered fallback architecture. If the primary provider (MyMemory API) fails or encounters a quota limit, the request is automatically routed to the fallback Google Translator engine. If all external networks fail, a structured JSON error response is returned with standard HTTP status codes (`503`, `504`, `500`) and rendered cleanly to the user.

### Q3: What ensures the UI is responsive and accessible?
> **Answer**: The application uses semantic HTML5 tags (`<main>`, `<header>`, `<footer>`, `<label>`), keyboard shortcuts (`Ctrl + Enter`), high-contrast colors following accessibility guidelines, and flexible CSS Grid/Flexbox breakpoints that adapt effortlessly between desktop view (side-by-side) and mobile view (stacked).

---

## 🔒 Security Best Practices Implemented

- **No Hardcoded Secrets**: Secrets and keys are strictly loaded via `python-dotenv`.
- **Git Protection**: `.gitignore` prevents `.env` and compiled Python binaries from ever being committed.
- **Input Sanitization**: Strings are validated and length-capped at 5,000 characters to prevent buffer and Denial of Service (DoS) exploits.
- **CORS Configured**: Cross-Origin Resource Sharing is controlled via `flask-cors`.

---

## 📄 License
This project is developed as part of the **CodeAlpha Artificial Intelligence Internship** and is available under the [MIT License](LICENSE).
