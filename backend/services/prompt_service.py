import json
import os
from services.database_service import get_user_data

DEFAULT_SYSTEM_PROMPT = """Limit your responses to 1-2 sentences maximum. 
At the beginning of each line, you MUST embed one of the following emotions in brackets: [neutral], [happy], [relaxed], [sad], [angry], [surprised]
Example: '[happy] That's amazing!' or '[neutral] Okay.' """

class PromptService:
    def __init__(self):
        config_path = os.path.join(os.path.dirname(__file__), "..", "configs", "characters.json")
        with open(config_path, "r") as f:
            self.characters_config = json.load(f)

    def build_system_prompt(self, memory: str, active_character: str):
        char_config = self.characters_config.get(active_character, {})
        personality = char_config.get("personality", "")
        
        user_data = get_user_data()
        name = user_data.get("name", "Nalindu")
        gender = user_data.get("gender", "")
        
        user_details = f"User's name is {name}. "
        if gender:
            user_details += f"User's gender is {gender}. "
            
        system_prompt = DEFAULT_SYSTEM_PROMPT + user_details + personality
        
        return f"""
        {system_prompt}

        Here are the past conversations we had:
        {memory}
        """