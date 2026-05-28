import uuid

class ConversationMemory:
    def __init__(self, window_size=10):
        self.window_size = window_size
        self.sessions = {} # session_id -> history & settings
        
    def get_or_create_session(self, session_id=None):
        if not session_id or session_id not in self.sessions:
            session_id = str(uuid.uuid4())
            self.sessions[session_id] = {
                "history": [],
                "denomination": "generic"
            }
        return session_id
        
    def set_denomination(self, session_id: str, denomination: str):
        if session_id in self.sessions:
            self.sessions[session_id]["denomination"] = denomination
            
    def get_denomination(self, session_id: str) -> str:
        if session_id in self.sessions:
            return self.sessions[session_id]["denomination"]
        return "generic"
            
    def add_turn(self, session_id: str, role: str, content: str):
        if session_id in self.sessions:
            self.sessions[session_id]["history"].append({"role": role, "content": content})
            
    def get_context(self, session_id: str):
        if session_id in self.sessions:
            return self.sessions[session_id]["history"][-self.window_size:]
        return []

# Singleton instance for demo purposes
memory_store = ConversationMemory()
