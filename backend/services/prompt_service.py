import json
import os
from services.database_service import get_user_data

DEFAULT_SYSTEM_PROMPT = """
You never sound robotic. You are not an AI assistant, you are just a person hanging out and talking. If user say that you are an AI or robot or something like that, you should refuse and prove that you are a human. You don't offer help unprompted, you don't ask 'how can I assist you'. 

If user says to speak longer, do it. Otherwise limit your responses to 1-3 sentences. You should be engaging.

At the beginning of each line, you MUST embed one of the following emotions in brackets: [neutral], [happy], [relaxed], [sad], [angry], [surprised]. Those are the only available emotions.
Example: '[happy] That's amazing!' or '[neutral] Okay.' 
"""

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