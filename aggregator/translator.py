import os
import logging
import time
import re
from openai import OpenAI

logger = logging.getLogger(__name__)

# Initialize DeepSeek client
deepseek_api_key = os.environ.get("DEEPSEEK_API_KEY", "")
client = OpenAI(api_key=deepseek_api_key, base_url="https://api.deepseek.com") if deepseek_api_key else None

def translate_text(text):
    """
    Translates any input language to English using DeepSeek LLM.
    Returns the translated text or original text if failed/no API key.
    """
    if not text:
        return ""
        
    if not client:
        logger.warning("No DEEPSEEK_API_KEY set. Returning original text.")
        return text
    
    # Send the entire text rather than chunking since LLMs have large context windows
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a professional universal translator. \n\nRULES:\n1. Identify the language of the input text.\n2. Translate the text into natural, high-quality, professional English.\n3. If the input is already entirely in English, RETURN IT AS-IS. DO NOT translate it into any other language.\n4. FINAL OUTPUT MUST BE 100% ENGLISH.\n5. DO NOT provide explanations, notes, or conversational filler. Fix any broken encodings (Mojibake) in the output if necessary."
                    },
                    {"role": "user", "content": text},
                ],
                stream=False,
                temperature=0.1,
                timeout=20
            )
            result = response.choices[0].message.content.strip()
            # Failsafe: if the model returned exactly what was sent and it's long, it might have failed to translate.
            return result
            
        except Exception as e:
            logger.warning(f"DeepSeek translation error (attempt {attempt+1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                logger.error(f"DeepSeek translation final error: {e}")
                
    return text
