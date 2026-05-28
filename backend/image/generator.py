import os
from backend.image.prompt_sanitizer import build_image_prompt, sanitize_image_intent

def generate_image(intent: str, style: str = "renaissance") -> dict:
    # 1. Sanitize Intent
    sanitization = sanitize_image_intent(intent)
    if not sanitization["passed"]:
        return {"success": False, "error": sanitization["reason"]}
        
    # 2. Build Safe Prompt
    safe_prompt = build_image_prompt(intent, style)
    
    # 3. Call Image API (Mocked for Gemini Migration)
    # Gemini standard API doesn't support image generation out-of-the-box like DALL-E,
    # so we return a placeholder until Imagen 3 is fully integrated.
    return {
        "success": True, 
        "url": "/frontend/sacred_dove_descending.jpg", 
        "prompt": safe_prompt
    }
