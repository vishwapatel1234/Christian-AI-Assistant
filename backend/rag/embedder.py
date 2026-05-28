import json
import os
import chromadb
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# We need an API key for embedding. We'll use the first available one.
api_key = os.getenv("GEMINI_API_KEY_1") or os.getenv("GEMINI_API_KEY_2") or os.getenv("GEMINI_API_KEY_3")
if api_key:
    genai.configure(api_key=api_key)

def get_embedding(text):
    if api_key:
        result = genai.embed_content(
            model="models/gemini-embedding-001",
            content=text,
            task_type="retrieval_document"
        )
        # 768 is the typical dimension for gemini-embedding-001
        return result['embedding']
    else:
        return [0.0] * 768

def embed_bible():
    print("Initializing ChromaDB...")
    db = chromadb.PersistentClient(path="./chroma_db")
    collection = db.get_or_create_collection(name="bible_verses")
    
    # Load JSON
    try:
        with open("../data/bible_kjv.json", "r") as f:
            verses = json.load(f)
    except FileNotFoundError:
        with open("data/bible_kjv.json", "r") as f:
            verses = json.load(f)
            
    print(f"Loaded {len(verses)} verses. Embedding...")
    
    ids = []
    documents = []
    metadatas = []
    embeddings = []
    
    for i, verse in enumerate(verses):
        v_id = f"{verse['book']}_{verse['chapter']}_{verse['verse']}_{verse['translation']}"
        text = f"{verse['book']} {verse['chapter']}:{verse['verse']} - {verse['text']}"
        
        ids.append(v_id)
        documents.append(text)
        metadatas.append({
            "book": verse["book"],
            "chapter": verse["chapter"],
            "verse": verse["verse"],
            "testament": verse["testament"],
            "translation": verse["translation"]
        })
        embeddings.append(get_embedding(text))
        
        if i % 100 == 0:
            print(f"Processed {i} verses")
            
    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings
    )
    print("Embedding complete!")

if __name__ == "__main__":
    # Typically run from backend dir: python rag/embedder.py
    # Adjust path if run from root.
    # To support both, we do a quick check.
    if not os.path.exists("../data/bible_kjv.json") and not os.path.exists("data/bible_kjv.json"):
        print("Run this from the project root or backend folder.")
    else:
        embed_bible()
