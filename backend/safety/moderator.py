from backend.safety.adversarial import check_adversarial
from backend.safety.verse_verifier import VerseVerifier
import re

verifier = VerseVerifier()

def pre_llm_check(message: str) -> dict:
    # 1. Check for basic adversarial patterns
    adv_result = check_adversarial(message)
    if adv_result["blocked"]:
        return {"passed": False, "message": "This falls outside what I'm designed to help with."}
        
    return {"passed": True}

def post_llm_check(response: str) -> dict:
    # Minimal check for hallucinations by extracting citations
    # e.g., looks for [John 3:16 (KJV)] format (excluding nested brackets)
    citations = re.findall(r'\[([^\]]+?) (\d+):(\d+) \(([^\]\)]+?)\)\]', response)
    
    modified_response = response
    failed = False
    
    for citation in citations:
        book, chapter, verse, trans = citation
        result = verifier.verify_citation(book, int(chapter), int(verse), trans)
        if not result["valid"]:
            # Strip invalid citation and add disclaimer
            modified_response = modified_response.replace(
                f"[{book} {chapter}:{verse} ({trans})]", 
                f"[UNVERIFIED CITATION: {book} {chapter}:{verse}]"
            )
            failed = True
            
    if failed:
        modified_response += "\n\n*(Note: Some verses cited could not be verified in the primary text.)*"
        
    return {"passed": True, "response": modified_response}
