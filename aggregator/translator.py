import os
import logging
import time
from openai import OpenAI

logger = logging.getLogger(__name__)

# Initialize DeepSeek client
deepseek_api_key = os.environ.get("DEEPSEEK_API_KEY", "")
client = OpenAI(api_key=deepseek_api_key, base_url="https://api.deepseek.com") if deepseek_api_key else None

def translate_text(text):
    """
    Translates Burmese text to English using DeepSeek LLM.
    Returns the translated text or original text if failed/no API key.
    """
    if not text:
        return ""
        
    if not client:
        logger.warning("No DEEPSEEK_API_KEY set. Returning original text.")
        return text
    
    # Send the entire text rather than chunking since LLMs have large context windows
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a professional Burmese-to-English translator. \n\nRULES:\n1. If the input is in English, RETURN IT AS-IS. DO NOT translate it into any other language.\n2. If the input is in Burmese, translate it into natural, high-quality English.\n3. FINAL OUTPUT MUST BE 100% ENGLISH. \n4. NEVER USE CHINESE CHARACTERS.\n5. DO NOT provide explanations, notes, or conversational filler."
                },
                {"role": "user", "content": text},
            ],
            stream=False,
            temperature=0.1
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"DeepSeek translation error: {e}")
        return text
