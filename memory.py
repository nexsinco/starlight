import json
import os

FILE = "memory.json"

class MemoryManager:
    def __init__(self):
        self.storage = self._load_all()
        # In-memory short-term memory session
        self.short_term_context = [] 

    def _load_all(self):
        default_structure = {"users": {}, "history": []}
        if not os.path.exists(FILE):
            return default_structure
        try:
            with open(FILE, "r") as f:
                return json.load(f)
        except Exception:
            return default_structure

    def save_all(self):
        with open(FILE, "w") as f:
            json.dump(self.storage, f, indent=4)

    def remember_profile_fact(self, user, key, value):
        if user not in self.storage["users"]:
            self.storage["users"][user] = {"attributes": {}, "meta": {}}
        
        self.storage["users"][user]["attributes"][key.lower().strip()] = value.strip()
        self.save_all()

    def get_profile_fact(self, user, key):
        user_data = self.storage["users"].get(user, {})
        return user_data.get("attributes", {}).get(key.lower().strip(), None)

    def add_to_history(self, user_msg, bot_msg):
        turn = {"user": user_msg, "bot": bot_msg}
        self.storage["history"].append(turn)
        self.short_term_context.append(turn)
        
        # Keep short term memory capped at last 3 turns
        if len(self.short_term_context) > 3:
            self.short_term_context.pop(0)
            
        self.save_all()

    def get_short_term_string(self):
        """Converts recent context into a single string for structural awareness."""
        context_str = ""
        for turn in self.short_term_context:
            context_str += f"User: {turn['user']} | Bot: {turn['bot']} -> "
        return context_str
