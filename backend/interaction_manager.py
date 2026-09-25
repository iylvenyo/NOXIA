## this file will recieve actions from UI then update companion
from backend.state_manager import StateManager


class InteractionManager:
    def __init__(self, companion):
        self.companion = companion
        self.state_manager = StateManager()

        self.state_manager.update(self.companion)

    def pet(self):
        self.companion.interaction_count += 1
        self.companion.relationship_points += 1
        self.companion.happiness += 3
        self.companion.energy -= 1

        self.update_companion()

        return "NOXIA noticed your attention."

    def feed(self):
        self.companion.interaction_count += 1
        self.companion.relationship_points += 1
        self.companion.hunger -= 25
        self.companion.happiness += 2

        self.update_companion()

        return "You fed NOXIA."

    def play(self):
        self.companion.interaction_count += 1
        self.companion.relationship_points += 2
        self.companion.happiness += 12
        self.companion.energy -= 10
        self.companion.hunger += 5

        self.update_companion()

        return "You played with NOXIA."

    def rest(self):
        self.companion.interaction_count += 1
        self.companion.energy += 25
        self.companion.hunger += 3

        self.update_companion()

        return "NOXIA rested."

    def update_needs(self):
        self.companion.hunger += 1
        self.companion.energy -= 1
        self.companion.happiness -= 1

        self.update_companion()

    def update_companion(self):
        self.state_manager.update(self.companion)