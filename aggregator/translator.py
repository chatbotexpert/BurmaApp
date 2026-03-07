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
                    "content": "You are a professional translator. Your ONLY task is to translate the input text into pure, natural English. IF the text is already in English, return it exactly as is. IF the text contains Burmese, Chinese, or any other language, translate those parts into English. Your final output MUST be 100% English. DO NOT output any Chinese or Burmese characters. DO NOT add conversational filler."
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
