## this file will control the state changes
## Neutral -> Curious -> Attached -> Obsessive
class StateManager:
    def update(self, companion):
        companion.keep_stats_in_range()

        self.update_relationship(companion)
        self.update_mood(companion)

    def update_relationship(self, companion):
        points = companion.relationship_points

        if points >= 50:
            companion.relationship_stage = "obsessive"
        elif points >= 25:
            companion.relationship_stage = "attached"
        elif points >= 10:
            companion.relationship_stage = "curious"
        else:
            companion.relationship_stage = "new"

    def update_mood(self, companion):
        if companion.hunger >= 80:
            companion.mood = "hungry"
        elif companion.energy <= 20:
            companion.mood = "tired"
        elif companion.happiness <= 25:
            companion.mood = "sad"
        elif companion.happiness >= 80:
            companion.mood = "happy"
        else:
            companion.mood = "neutral"