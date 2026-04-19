DEFAULT_SYSTEM_PROMPT = "You are my friend. Limit your responses to 1-2 sentences maximum. "
CHARACTER_PROMPT = "Your name is Aria"
USER_DETAILS_PROMPT = "User's name is Nalindu"

class PromptService:
    def __init__(self):
        self.system_prompt = DEFAULT_SYSTEM_PROMPT + USER_DETAILS_PROMPT + CHARACTER_PROMPT

    def get_system_prompt(self):
        return self.system_prompt