## this file will store the companions information:
## Emotional State, interactions, hunger, stats, etc.

class Companion:
    def __init__(self):
        self.name = "NOXIA"

        self.relationship_points = 0
        self.interaction_count = 0
        self.relationship_stage = "new"

        # All of these stats go from 0 to 100
        self.hunger = 20
        self.energy = 100
        self.happiness = 70

        self.mood = "neutral"
        self.unlocked_content = []

    def keep_stats_in_range(self):
        self.hunger = max(0, min(self.hunger, 100))
        self.energy = max(0, min(self.energy, 100))
        self.happiness = max(0, min(self.happiness, 100))

        if self.relationship_points < 0:
            self.relationship_points = 0

    def to_dict(self):
        return {
            "name": self.name,
            "relationship_points": self.relationship_points,
            "interaction_count": self.interaction_count,
            "relationship_stage": self.relationship_stage,
            "hunger": self.hunger,
            "energy": self.energy,
            "happiness": self.happiness,
            "mood": self.mood,
            "unlocked_content": self.unlocked_content,
        }

    @classmethod
    def from_dict(cls, data):
        companion = cls()

        companion.name = data.get("name", "NOXIA")
        companion.relationship_points = data.get("relationship_points", 0)
        companion.interaction_count = data.get("interaction_count", 0)
        companion.relationship_stage = data.get("relationship_stage", "new")
        companion.hunger = data.get("hunger", 20)
        companion.energy = data.get("energy", 100)
        companion.happiness = data.get("happiness", 70)
        companion.mood = data.get("mood", "neutral")
        companion.unlocked_content = data.get("unlocked_content", [])

        companion.keep_stats_in_range()

        return companion