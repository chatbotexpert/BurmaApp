from deep_translator import GoogleTranslator
import logging

logger = logging.getLogger(__name__)

def translate_text(text):
    """
    Translates text dynamically. Detects any source language and translates to English ('en').
    Returns the translated text or original text if failed.
    """
    if not text:
        return ""
    
    try:
        # We always want the destination to be English
        translated = GoogleTranslator(source='auto', target='en').translate(text)
        return translated if translated else text
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return text # Return original text on failure
