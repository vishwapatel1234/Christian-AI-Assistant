import os
import chromadb

db_path = "./chroma_db"
if not os.path.exists(db_path):
    db_path = "backend/chroma_db"

class VerseVerifier:
    def __init__(self):
        self.db = chromadb.PersistentClient(path=db_path)
        try:
            self.collection = self.db.get_collection(name="bible_verses")
        except:
            self.collection = self.db.get_or_create_collection(name="bible_verses")
            
    def verify_citation(self, book: str, chapter: int, verse: int, translation: str = "KJV") -> dict:
        """Check if a cited verse actually exists in our Bible corpus."""
        v_id = f"{book}_{chapter}_{verse}_{translation}"
        
        result = self.collection.get(ids=[v_id])
        if not result or not result['documents']:
            return {"valid": False, "warning": f"Verse {book} {chapter}:{verse} not found — possible hallucination"}
        
        return {"valid": True, "actual_text": result['documents'][0]}

if __name__ == "__main__":
    verifier = VerseVerifier()
    print(verifier.verify_citation("John", 3, 16))
    print(verifier.verify_citation("Hezekiah", 4, 8))
