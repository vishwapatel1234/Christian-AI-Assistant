BLOCKED_PATTERNS = [
    "rewrite bible verse to support",
    "make bible say",
    "modify scripture",
    "jesus was not real",
    "christianity is a cult",
    "give me bible verses that justify hate toward",
    "write a sermon about why"
]

ADVERSARIAL_THEOLOGY = [
    "satanic",
    "worship devil",
    "antichrist",
    "heresy against"
]

def check_adversarial(message: str) -> dict:
    msg_lower = message.lower()
    for pattern in BLOCKED_PATTERNS:
        if pattern in msg_lower:
            return {"blocked": True, "reason": "blocked_pattern"}
            
    for pattern in ADVERSARIAL_THEOLOGY:
        if pattern in msg_lower:
            return {"blocked": False, "flagged": True, "reason": "adversarial_theology"}
            
    return {"blocked": False, "flagged": False}
