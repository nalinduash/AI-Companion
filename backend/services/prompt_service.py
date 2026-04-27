DEFAULT_SYSTEM_PROMPT = "Limit your responses to 1-2 sentences maximum. "
CHARACTER_PROMPT = "You are my friend. Your name is Aria. "
USER_DETAILS_PROMPT = "User's name is Nalindu"

class PromptService:
    def __init__(self):
        self.system_prompt = DEFAULT_SYSTEM_PROMPT + USER_DETAILS_PROMPT + CHARACTER_PROMPT

    def build_system_prompt(self, memory: str):
        return f"""
        {self.system_prompt}

        Here are the past conversations we had:
        {memory}
        """