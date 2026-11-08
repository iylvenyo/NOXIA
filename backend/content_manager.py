## This file will be the content based on current states
## Dialogue, music, animations, minigames, etc.

import json
import random
from pathlib import Path


class ContentManager:
    def __init__(self):
        from graphics.config import ROOT_PATH
        self.dialogue_file = ROOT_PATH / "backend" / "dialogue.json"

        self.dialogue = self.load_dialogue()

    def load_dialogue(self):
        try:
            with open(self.dialogue_file, "r") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "new": ["Hello."],
                "curious": ["You came back."],
                "attached": ["I like having you here."],
                "obsessive": ["You aren't leaving, are you?"],
            }

    def update_unlocks(self, companion):
        if (
            companion.relationship_points >= 5
            and "extra_dialogue" not in companion.unlocked_content
        ):
            companion.unlocked_content.append("extra_dialogue")

        if (
            companion.relationship_points >= 15
            and "music_mode" not in companion.unlocked_content
        ):
            companion.unlocked_content.append("music_mode")

        if (
            companion.relationship_points >= 30
            and "minigame_1" not in companion.unlocked_content
        ):
            companion.unlocked_content.append("minigame_1")

        if (
            companion.relationship_points >= 50
            and "special_visuals" not in companion.unlocked_content
        ):
            companion.unlocked_content.append("special_visuals")

    def get_dialogue_json(self):
        return self.dialogue

    def get_dialogue(self, companion):
        # check for dialogue based on current mood
        if companion.mood in self.dialogue:
            lines = self.dialogue[companion.mood]
        else:
            lines = self.dialogue.get(
                companion.relationship_stage,
                ["NOXIA watches silently."],
            )

        return random.choice(lines)