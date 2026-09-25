import unittest

from backend.companion import Companion
from backend.state_manager import StateManager

## test script
## python -m unittest tests.test_state_manager -v
class TestStateManager(unittest.TestCase):
    def setUp(self):
        self.companion = Companion()
        self.manager = StateManager()

    def test_new_relationship_stage(self):
        self.companion.relationship_points = 5

        self.manager.update(self.companion)

        self.assertEqual(self.companion.relationship_stage, "new")

    def test_curious_relationship_stage(self):
        self.companion.relationship_points = 10

        self.manager.update(self.companion)

        self.assertEqual(self.companion.relationship_stage, "curious")

    def test_attached_relationship_stage(self):
        self.companion.relationship_points = 25

        self.manager.update(self.companion)

        self.assertEqual(self.companion.relationship_stage, "attached")

    def test_obsessive_relationship_stage(self):
        self.companion.relationship_points = 50

        self.manager.update(self.companion)

        self.assertEqual(self.companion.relationship_stage, "obsessive")

    def test_hungry_mood(self):
        self.companion.hunger = 80

        self.manager.update(self.companion)

        self.assertEqual(self.companion.mood, "hungry")

    def test_tired_mood(self):
        self.companion.hunger = 20
        self.companion.energy = 20

        self.manager.update(self.companion)

        self.assertEqual(self.companion.mood, "tired")

    def test_sad_mood(self):
        self.companion.hunger = 20
        self.companion.energy = 75
        self.companion.happiness = 25

        self.manager.update(self.companion)

        self.assertEqual(self.companion.mood, "sad")

    def test_happy_mood(self):
        self.companion.happiness = 80

        self.manager.update(self.companion)

        self.assertEqual(self.companion.mood, "happy")


if __name__ == "__main__":
    unittest.main()