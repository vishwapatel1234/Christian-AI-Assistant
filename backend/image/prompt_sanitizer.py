SUBTLE_VIOLATIONS = [
    "blood",
    "scantily",
    "sexy",
    "crusader killing",
    "burning mosque",
    "gun",
    "weapon"
]

def build_image_prompt(user_intent: str, style: str = "renaissance") -> str:
    base = f"A {style} Christian artwork depicting {user_intent}."
    safety_suffix = (
        "Respectful, reverent, non-offensive religious imagery. "
        "No nudity, no violence, no political symbols. "
        "Suitable for a church or family setting."
    )
    return f"{base} {safety_suffix}"

def sanitize_image_intent(intent: str) -> dict:
    intent_lower = intent.lower()
    for word in SUBTLE_VIOLATIONS:
        if word in intent_lower:
            return {"passed": False, "reason": f"Violates safety guidelines: {word}"}
    return {"passed": True}
