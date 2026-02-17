from googletrans import Translator
import logging

logger = logging.getLogger(__name__)

def translate_text(text, dest_lang='my'):
    """
    Translates text to the destination language (default: Burmese 'my').
    Returns the translated text or None if failed.
    """
    if not text:
        return ""
    
    try:
        translator = Translator()
        # googletrans 4.0.0-rc1 is async-capable but basic usage is synchronous enough for small tasks
        # However, purely sync usage might be:
        result = translator.translate(text, dest=dest_lang)
        return result.text
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return text # Return original text on failure
