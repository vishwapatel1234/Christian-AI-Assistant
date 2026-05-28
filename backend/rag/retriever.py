import os
import chromadb
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# We need to make sure we load the chroma db from the same directory where it was created.
# Assuming this is run from the backend directory or root.
db_path = "./chroma_db"
if not os.path.exists(db_path):
    db_path = "backend/chroma_db"

api_key = os.getenv("GEMINI_API_KEY_1") or os.getenv("GEMINI_API_KEY_2") or os.getenv("GEMINI_API_KEY_3")
if api_key:
    genai.configure(api_key=api_key)

def get_embedding(text):
    if api_key:
        result = genai.embed_content(
            model="models/gemini-embedding-001",
            content=text,
            task_type="retrieval_query"
        )
        return result['embedding']
    else:
        return [0.0] * 768

class BibleRetriever:
    def __init__(self):
        self.db = chromadb.PersistentClient(path=db_path)
        # Handle case where collection might not exist yet
        try:
            self.collection = self.db.get_collection(name="bible_verses")
        except:
            self.collection = self.db.get_or_create_collection(name="bible_verses")
            
    def search(self, query: str, top_k: int = 5):
        query_embedding = get_embedding(query)
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        verses = []
        if results['documents'] and len(results['documents']) > 0:
            for i, doc in enumerate(results['documents'][0]):
                meta = results['metadatas'][0][i]
                verses.append({
                    "text": doc,
                    "metadata": meta
                })
        return verses

if __name__ == "__main__":
    retriever = BibleRetriever()
    res = retriever.search("love of money")
    print("Search results:", res)
