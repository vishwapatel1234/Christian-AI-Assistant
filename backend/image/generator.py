import os
import base64
import urllib.request
import urllib.parse
from backend.image.prompt_sanitizer import build_image_prompt, sanitize_image_intent
from dotenv import load_dotenv

load_dotenv()

def generate_image(intent: str, style: str = "renaissance") -> dict:
    # 1. Sanitize Intent
    sanitization = sanitize_image_intent(intent)
    if not sanitization["passed"]:
        return {"success": False, "error": sanitization["reason"]}

    # 2. Build Safe Prompt
    safe_prompt = build_image_prompt(intent, style)

    # 3. Generate via Pollinations.ai (free, no API key, Flux model)
    try:
        encoded = urllib.parse.quote(safe_prompt)
        poll_url = (
            f"https://image.pollinations.ai/prompt/{encoded}"
            f"?width=512&height=512&nologo=true&model=flux"
        )
        print(f"Generating image via Pollinations.ai ...")

        req = urllib.request.Request(
            poll_url,
            headers={"User-Agent": "Christian-AI-Assistant/1.0"}
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            img_bytes = resp.read()

        if img_bytes and len(img_bytes) > 1000:
            b64 = base64.b64encode(img_bytes).decode("utf-8")
            data_url = f"data:image/jpeg;base64,{b64}"
            return {
                "success": True,
                "url": data_url,
                "prompt": safe_prompt
            }
        else:
            raise ValueError("Empty or too-small image returned")

    except Exception as e:
        print(f"Pollinations.ai failed: {e}")

    # 4. Last resort — serve the local sacred dove image as base64
    try:
        dove_paths = [
            "frontend/sacred_dove_descending.jpg",
            "d:/Trentiums/Assignment/christian-ai-assistant/frontend/sacred_dove_descending.jpg"
        ]
        for path in dove_paths:
            if os.path.exists(path):
                with open(path, "rb") as f:
                    img_bytes = f.read()
                b64 = base64.b64encode(img_bytes).decode("utf-8")
                data_url = f"data:image/jpeg;base64,{b64}"
                return {
                    "success": True,
                    "url": data_url,
                    "prompt": safe_prompt,
                    "note": "Showing sacred art placeholder (image service temporarily unavailable)"
                }
    except Exception as e:
        print(f"Fallback image load failed: {e}")

    return {
        "success": False,
        "error": "Image generation is currently unavailable. Please try again in a moment."
    }
