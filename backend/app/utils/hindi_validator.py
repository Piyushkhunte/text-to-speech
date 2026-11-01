import re
import unicodedata
from typing import Tuple


def contains_devanagari(text: str) -> bool:
    """Checks whether the text contains at least one Devanagari character (U+0900 to U+097F)."""
    return any("\u0900" <= char <= "\u097f" for char in text)


def contains_latin(text: str) -> bool:
    """Checks whether the text contains Latin letters (for Hinglish/English)."""
    return bool(re.search(r"[a-zA-Z]", text))


def normalize_hindi_text(text: str) -> str:
    """
    Normalizes Hindi / Hinglish Unicode text using NFC, removes non-printable characters,
    and strips redundant whitespace.
    """
    if not text:
        return ""
    # Unicode canonical normalization
    text = unicodedata.normalize("NFC", text)
    # Remove control characters except standard line breaks and tabs
    text = "".join(ch for ch in text if ch.isprintable() or ch in ("\n", "\r", "\t"))
    # Normalize multiple whitespaces into a single space
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def validate_hindi_input(text: str, max_chars: int = 3000) -> Tuple[bool, str, str]:
    """
    Validates user text input for Hindi / Hinglish TTS generation.
    Supports:
    - Pure Devanagari Hindi
    - Code-mixed Hindi + English (e.g., 'Programming में values store करना')
    - Pure Roman Hinglish (e.g., 'Namaste dosto, aaj hum seekhenge...')
    Returns: (is_valid, normalized_text, error_message)
    """
    if not text:
        return False, "", "टेक्स्ट खाली नहीं हो सकता। कृपया हिंदी या हिंग्लिश टेक्स्ट दर्ज करें। (Text cannot be empty.)"

    normalized = normalize_hindi_text(text)

    if len(normalized) == 0:
        return False, "", "कृपया मान्य टेक्स्ट दर्ज करें। (Please enter valid text.)"

    if len(normalized) > max_chars:
        return (
            False,
            normalized,
            f"टेक्स्ट {max_chars} वर्णों से अधिक लंबा है (वर्तमान: {len(normalized)})। कृपया इसे छोटा करें। "
            f"(Text exceeds maximum limit of {max_chars} characters for reel audio.)",
        )

    # Check that text contains either Devanagari or Latin alphabet characters
    has_devanagari = contains_devanagari(normalized)
    has_latin = contains_latin(normalized)

    if not (has_devanagari or has_latin):
        return (
            False,
            normalized,
            "टेक्स्ट में मान्य हिंदी (देवनागरी) या हिंग्लिश वर्ण होने चाहिए। (Input must contain valid Hindi or Hinglish words.)",
        )

    return True, normalized, ""
