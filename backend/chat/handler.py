import os
import google.generativeai as genai
from backend.rag.retriever import BibleRetriever
from backend.chat.prompts import build_system_prompt
from backend.chat.denomination import get_denomination_context
from backend.memory.session_store import memory_store

# We'll load the 3 keys from the env (which we populated earlier)
API_KEYS = [
    os.getenv("GEMINI_API_KEY_1"),
    os.getenv("GEMINI_API_KEY_2"),
    os.getenv("GEMINI_API_KEY_3")
]

# We filter out any None keys
API_KEYS = [k for k in API_KEYS if k]

# Models in the requested fallback order, incorporating correct API names and robust Flash tier alternatives to handle quota/preview limits on free keys
MODELS = [
    "gemini-2.5-pro",         # User's requested 2.5 Pro
    "gemini-2.5-flash",       # 2.5 Flash (fully functional on free tier)
    "gemini-3.5-flash",       # 3.5 Flash (fully functional on free tier)
    "gemini-3.1-pro-preview", # User's requested 3.0 Pro
    "gemini-3-pro-preview",   # User's requested 3.0 Pro
    "gemini-2.0-flash",       # User's requested 2.0
    "gemini-pro-latest",      # User's requested 1.5 Pro
    "gemini-flash-latest"     # 1.5 Flash (fully functional on free tier)
]

retriever = BibleRetriever()

def attempt_generation_with_fallbacks(system_prompt: str, history: list) -> str:
    # Format history for Gemini (roles: 'user' and 'model')
    gemini_messages = []
    for turn in history:
        # Map our roles to Gemini roles
        role = "user" if turn["role"] == "user" else "model"
        gemini_messages.append({"role": role, "parts": [turn["content"]]})
        
    for key in API_KEYS:
        genai.configure(api_key=key)
        for model_name in MODELS:
            try:
                model = genai.GenerativeModel(
                    model_name=model_name,
                    system_instruction=system_prompt
                )
                
                # Start chat with history
                chat = model.start_chat(history=gemini_messages)
                
                # Since we already appended the current message to our custom history, 
                # we don't need to send a new message. We can just send the last message
                # from history and remove it from the chat history we pass.
                # Actually, Google's API expects us to pass previous history, then `send_message`.
                
                # Let's rebuild history minus the very last user message
                past_history = gemini_messages[:-1]
                last_user_msg = gemini_messages[-1]["parts"][0]
                
                chat = model.start_chat(history=past_history)
                response = chat.send_message(last_user_msg)
                
                return response.text
            except Exception as e:
                print(f"Failed with key {key[:5]}... and model {model_name}. Error: {e}")
                continue # Try next model
                
    # If we exhaust all keys and models, return a fallback message
    return "(Fallback) I'm sorry, but all available models and API keys failed to generate a response at this time."

def handle_chat_message(session_id: str, message: str) -> str:
    # 1. Retrieve relevant verses
    verses = retriever.search(message, top_k=3)
    
    verse_text = ""
    for v in verses:
        verse_text += f"[{v['metadata']['book']} {v['metadata']['chapter']}:{v['metadata']['verse']} ({v['metadata']['translation']})] {v['text']}\n"
        
    if not verse_text:
        verse_text = "No relevant verses found."
        
    # 2. Get denomination context
    denom = memory_store.get_denomination(session_id)
    denom_context = get_denomination_context(denom)
    
    # 3. Build system prompt
    system_prompt = build_system_prompt(denom_context, verse_text)
    
    # 4. Add to memory
    memory_store.add_turn(session_id, "user", message)
    history = memory_store.get_context(session_id)
    
    # 5. Call LLM with Fallbacks
    if API_KEYS:
        assistant_reply = attempt_generation_with_fallbacks(system_prompt, history)
    else:
        # Mock response if no API keys are set at all
        assistant_reply = f"(Mock Mode) Based on verses:\n{verse_text}\nResponse to: {message}"
        
    # 6. Add assistant reply to memory
    memory_store.add_turn(session_id, "assistant", assistant_reply)
    
    return assistant_reply
