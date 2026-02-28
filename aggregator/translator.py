from googletrans import Translator
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
        translator = Translator()
        
        # We always want the destination to be English
        dest_lang = 'en'
        
        result = translator.translate(text, dest=dest_lang)
        return getattr(result, 'text', text)
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return text # Return original text on failure
