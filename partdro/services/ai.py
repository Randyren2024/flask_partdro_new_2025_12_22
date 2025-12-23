import json
import httpx
from config import Config

def translate_product_info(name: str, description: str) -> dict:
    """
    Calls DeepSeek API to translate product name and description into
    Japanese (ja) and Spanish (es).
    Returns a dict with keys: name_ja, name_es, description_ja, description_es
    """
    if not Config.DEEPSEEK_API_KEY:
        raise ValueError("DEEPSEEK_API_KEY is not configured")

    # Prompt engineering: request JSON output
    prompt = f"""
You are a professional translator for technical drone products.
Translate the following product information into Japanese (ja) and Spanish (es).
Output ONLY a valid JSON object with these exact keys: "name_ja", "name_es", "description_ja", "description_es".
Do not include markdown formatting or extra text.

Product Name: {name}
Product Description: {description}
"""

    url = "https://api.deepseek.com/v1/chat/completions"  # Adjust if needed based on DeepSeek docs
    # Note: Using OpenAI-compatible endpoint structure common for DeepSeek
    
    # If the official endpoint differs, we might need to adjust. 
    # Assuming standard OpenAI compatibility for now:
    # Base URL often: https://api.deepseek.com or similar. 
    # Let's use the generic completion structure.
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {Config.DEEPSEEK_API_KEY}"
    }
    
    payload = {
        "model": "deepseek-chat",  # or deepseek-coder, deepseek-v3 etc.
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that outputs JSON."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }

    try:
        # Using httpx for async-capable sync request or just standard sync
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            
            content = data["choices"][0]["message"]["content"]
            # Clean potential markdown code blocks if any
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            
            return json.loads(content.strip())
            
    except Exception as e:
        # Fallback or re-raise
        raise RuntimeError(f"Translation failed: {str(e)}")
