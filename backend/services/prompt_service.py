import json
import os

DEFAULT_SYSTEM_PROMPT = "Limit your responses to 1-2 sentences maximum. "
USER_DETAILS_PROMPT = "User's name is Nalindu. "

class PromptService:
    def __init__(self):
        config_path = os.path.join(os.path.dirname(__file__), "..", "configs", "characters.json")
        with open(config_path, "r") as f:
            self.characters_config = json.load(f)

    def build_system_prompt(self, memory: str, active_character: str):
        char_config = self.characters_config.get(active_character, {})
        personality = char_config.get("personality", "")
        system_prompt = DEFAULT_SYSTEM_PROMPT + USER_DETAILS_PROMPT + personality
        return f"""
        {system_prompt}

        Here are the past conversations we had:
        {memory}
        """