/**
 * =============================================================================
 * CodeAlpha AI Internship Project 1: Language Translation Tool
 * Client-Side Application Logic
 * 
 * Features:
 *  - Dynamic language list retrieval from backend API
 *  - Asynchronous translation dispatch with loading overlay
 *  - Swap languages and bidirectional content transfer
 *  - Copy to clipboard with instant visual feedback
 *  - Input reset and live character counter
 *  - Text-to-Speech audio pronunciation (Web Speech API)
 *  - Accessible error alerts and banner notifications
 * =============================================================================
 */

document.addEventListener("DOMContentLoaded", () => {
    // -------------------------------------------------------------------------
    // 1. DOM Element Selectors
    // -------------------------------------------------------------------------
    const sourceText = document.getElementById("sourceText");
    const targetText = document.getElementById("targetText");
    const sourceLang = document.getElementById("sourceLang");
    const targetLang = document.getElementById("targetLang");
    
    const translateBtn = document.getElementById("translateBtn");
    const swapLangBtn = document.getElementById("swapLangBtn");
    const clearBtn = document.getElementById("clearBtn");
    const copyBtn = document.getElementById("copyBtn");
    const copyBtnText = document.getElementById("copyBtnText");
    
    const speakSourceBtn = document.getElementById("speakSourceBtn");
    const speakTargetBtn = document.getElementById("speakTargetBtn");
    
    const loadingOverlay = document.getElementById("loadingOverlay");
    const charCount = document.getElementById("charCount");
    const providerBadge = document.getElementById("providerBadge");
    const providerName = document.getElementById("providerName");
    
    const alertBanner = document.getElementById("alertBanner");
    const alertMessage = document.getElementById("alertMessage");
    const alertCloseBtn = document.getElementById("alertCloseBtn");
    const toast = document.getElementById("toast");
    
    // Application state
    let lastDetectedLanguage = null;

    // -------------------------------------------------------------------------
    // 2. Initial Setup: Populate Supported Languages from Backend
    // -------------------------------------------------------------------------
    async function loadSupportedLanguages() {
        try {
            const response = await fetch("/api/languages");
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();

            if (data.success && data.languages) {
                // Clear existing options except defaults
                sourceLang.innerHTML = "";
                targetLang.innerHTML = "";

                // Populate Source dropdown (includes Auto Detect)
                for (const [code, name] of Object.entries(data.languages)) {
                    const srcOption = document.createElement("option");
                    srcOption.value = code;
                    srcOption.textContent = name;
                    if (code === "en") srcOption.selected = true;
                    sourceLang.appendChild(srcOption);

                    // Target dropdown cannot be 'auto'
                    if (code !== "auto") {
                        const tgtOption = document.createElement("option");
                        tgtOption.value = code;
                        tgtOption.textContent = name;
                        if (code === "es") tgtOption.selected = true; // Default target: Spanish
                        targetLang.appendChild(tgtOption);
                    }
                }
            }
        } catch (error) {
            console.error("Failed to load language list:", error);
            showAlert("Could not retrieve supported languages list. Using default languages.", "warning");
        }
    }

    // -------------------------------------------------------------------------
    // 3. Translation Execution Handler
    // -------------------------------------------------------------------------
    async function performTranslation() {
        const textToTranslate = sourceText.value.trim();
        const src = sourceLang.value;
        const tgt = targetLang.value;

        // Validation: Verify input text is not empty
        if (!textToTranslate) {
            showAlert("Please enter some text in the source box to translate.", "warning");
            sourceText.focus();
            return;
        }

        // Validation: Ensure target language is specified
        if (!tgt) {
            showAlert("Please select a target language.", "warning");
            return;
        }

        // Clear any previous alerts
        hideAlert();
        setLoadingState(true);

        try {
            // Send asynchronous POST request to the backend translation proxy
            const response = await fetch("/api/translate", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    text: textToTranslate,
                    source: src,
                    target: tgt
                })
            });

            const data = await response.json();

            if (!response.ok || !data.success) {
                const errorMessage = data.error || `Translation error (Status: ${response.status})`;
                throw new Error(errorMessage);
            }

            // Populate translated output
            targetText.value = data.translatedText;

            // Track detected language for smart swapping
            if (data.detectedSource) {
                lastDetectedLanguage = data.detectedSource;
            }

            // Display translation provider indicator
            if (data.provider) {
                providerName.textContent = data.provider;
                providerBadge.classList.remove("hidden");
            }

        } catch (error) {
            console.error("Translation request failed:", error);
            showAlert(error.message || "Failed to translate text. Please verify your connection.", "error");
        } finally {
            setLoadingState(false);
        }
    }

    // -------------------------------------------------------------------------
    // 4. Swap Languages & Content Handler
    // -------------------------------------------------------------------------
    function swapLanguages() {
        const currentSrc = sourceLang.value;
        const currentTgt = targetLang.value;

        // If source is 'auto', check if we have a resolved detected language
        if (currentSrc === "auto") {
            if (lastDetectedLanguage && lastDetectedLanguage !== currentTgt) {
                sourceLang.value = currentTgt;
                targetLang.value = lastDetectedLanguage;
            } else {
                showAlert("Please select an explicit source language or translate text first before swapping from Auto Detect.", "info");
                return;
            }
        } else {
            // Swap selected language dropdown values
            sourceLang.value = currentTgt;
            targetLang.value = currentSrc;
        }

        // Swap text contents if target has a translation already
        const currentSrcText = sourceText.value;
        const currentTgtText = targetText.value;

        if (currentTgtText.trim() !== "") {
            sourceText.value = currentTgtText;
            targetText.value = currentSrcText;
            updateCharacterCount();
        }

        hideAlert();
    }

    // -------------------------------------------------------------------------
    // 5. Copy Translation to Clipboard
    // -------------------------------------------------------------------------
    async function copyTranslation() {
        const translatedContent = targetText.value.trim();

        if (!translatedContent) {
            showAlert("No translation available to copy. Please translate text first.", "warning");
            return;
        }

        try {
            if (navigator.clipboard && window.isSecureContext) {
                await navigator.clipboard.writeText(translatedContent);
            } else {
                // Fallback for non-secure contexts or environments without navigator.clipboard
                targetText.select();
                targetText.setSelectionRange(0, 99999);
                const successful = document.execCommand('copy');
                window.getSelection().removeAllRanges();
                if (!successful) {
                    throw new Error("Clipboard copy command failed");
                }
            }
            
            // Visual feedback on the Copy button
            copyBtn.classList.add("copied");
            copyBtn.innerHTML = '<i class="fa-solid fa-check"></i> <span>Copied!</span>';
            showToast("Copied translation to clipboard!");

            // Revert button appearance after 2 seconds
            setTimeout(() => {
                copyBtn.classList.remove("copied");
                copyBtn.innerHTML = '<i class="fa-regular fa-copy"></i> <span id="copyBtnText">Copy</span>';
            }, 2000);

        } catch (err) {
            console.error("Clipboard copy failed:", err);
            showAlert("Failed to copy to clipboard. Please copy manually.", "error");
        }
    }

    // -------------------------------------------------------------------------
    // 6. Clear Input & Output Fields
    // -------------------------------------------------------------------------
    function clearFields() {
        sourceText.value = "";
        targetText.value = "";
        updateCharacterCount();
        providerBadge.classList.add("hidden");
        hideAlert();
        sourceText.focus();
    }

    // -------------------------------------------------------------------------
    // 7. Text-to-Speech (Audio Pronunciation via Web Speech API)
    // -------------------------------------------------------------------------
    function speakText(text, langCode) {
        if (!("speechSynthesis" in window)) {
            showAlert("Text-to-speech is not supported by your browser.", "info");
            return;
        }

        const trimmedText = text.trim();
        if (!trimmedText) {
            showAlert("No text available to read aloud.", "warning");
            return;
        }

        // Cancel any ongoing speech
        window.speechSynthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(trimmedText);
        if (langCode && langCode !== "auto") {
            utterance.lang = langCode;
        }

        utterance.rate = 0.95; // Natural speaking pace
        utterance.onerror = (e) => {
            console.warn("Speech synthesis notice:", e);
        };

        window.speechSynthesis.speak(utterance);
    }

    // -------------------------------------------------------------------------
    // 8. Character Count Tracker
    // -------------------------------------------------------------------------
    function updateCharacterCount() {
        const currentLength = sourceText.value.length;
        charCount.textContent = `${currentLength.toLocaleString()} / 5,000`;

        if (currentLength >= 4800) {
            charCount.style.color = "#ef4444"; // Warning red
        } else {
            charCount.style.color = "";
        }
    }

    // -------------------------------------------------------------------------
    // 9. UI State Management: Loading & Alerts
    // -------------------------------------------------------------------------
    function setLoadingState(isLoading) {
        if (isLoading) {
            loadingOverlay.classList.remove("hidden");
            translateBtn.disabled = true;
            translateBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> <span>Translating...</span>';
        } else {
            loadingOverlay.classList.add("hidden");
            translateBtn.disabled = false;
            translateBtn.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles"></i> <span>Translate Now</span>';
        }
    }

    function showAlert(message, type = "error") {
        alertMessage.textContent = message;
        alertBanner.className = `alert-banner ${type}`;

        const alertIcon = document.getElementById("alertIcon");
        if (type === "warning") {
            alertIcon.className = "fa-solid fa-triangle-exclamation";
        } else if (type === "info") {
            alertIcon.className = "fa-solid fa-circle-info";
        } else {
            alertIcon.className = "fa-solid fa-circle-exclamation";
        }

        alertBanner.classList.remove("hidden");
    }

    function hideAlert() {
        alertBanner.classList.add("hidden");
    }

    function showToast(message) {
        toast.textContent = message;
        toast.classList.remove("hidden");
        setTimeout(() => {
            toast.classList.add("hidden");
        }, 2200);
    }

    // -------------------------------------------------------------------------
    // 10. Event Listeners Registration
    // -------------------------------------------------------------------------
    translateBtn.addEventListener("click", performTranslation);
    swapLangBtn.addEventListener("click", swapLanguages);
    clearBtn.addEventListener("click", clearFields);
    copyBtn.addEventListener("click", copyTranslation);
    alertCloseBtn.addEventListener("click", hideAlert);

    // Textarea input changes
    sourceText.addEventListener("input", updateCharacterCount);

    // Keyboard shortcut: Ctrl + Enter or Cmd + Enter to trigger translation
    sourceText.addEventListener("keydown", (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
            e.preventDefault();
            performTranslation();
        }
    });

    // Pronunciation buttons
    speakSourceBtn.addEventListener("click", () => {
        const lang = (sourceLang.value === "auto" && lastDetectedLanguage)
            ? lastDetectedLanguage
            : sourceLang.value;
        speakText(sourceText.value, lang);
    });

    speakTargetBtn.addEventListener("click", () => {
        speakText(targetText.value, targetLang.value);
    });

    // Initialize application
    loadSupportedLanguages();
    updateCharacterCount();
});
