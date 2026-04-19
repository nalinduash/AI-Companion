class ShortTermMemoryService:
    """Manages short-term memory (conversation history)."""
    def __init__(self):
        self.memory = []

    def add_to_memory(self, user_input, ai_response):
        self.memory.append({"user": user_input, "ai": ai_response})
        if len(self.memory) > 15:
            self.memory.pop(0)

    def get_memory(self):
        text = "\n".join([
            f"user: {m['user']}\n"
            f"AI: {m['ai']}"
            for m in self.memory
        ])
        return text