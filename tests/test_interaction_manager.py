import unittest

from backend.companion import Companion
from backend.interaction_manager import InteractionManager


class TestInteractionManager(unittest.TestCase):
    def setUp(self):
        self.companion = Companion()
        self.manager = InteractionManager(self.companion)

    def test_pet_increases_relationship(self):
        self.manager.pet()

        self.assertEqual(self.companion.relationship_points, 1)
        self.assertEqual(self.companion.interaction_count, 1)
        self.assertEqual(self.companion.happiness, 73)
        self.assertEqual(self.companion.energy, 99)

    def test_feeding_reduces_hunger(self):
        self.companion.hunger = 50

        self.manager.feed()

        self.assertEqual(self.companion.hunger, 25)
        self.assertEqual(self.companion.relationship_points, 1)

    def test_playing_changes_stats(self):
        self.manager.play()

        self.assertEqual(self.companion.relationship_points, 2)
        self.assertEqual(self.companion.happiness, 82)
        self.assertEqual(self.companion.energy, 90)
        self.assertEqual(self.companion.hunger, 25)

    def test_resting_increases_energy(self):
        self.companion.energy = 50

        self.manager.rest()

        self.assertEqual(self.companion.energy, 75)

    def test_needs_change_over_time(self):
        self.manager.update_needs()

        self.assertEqual(self.companion.hunger, 21)
        self.assertEqual(self.companion.energy, 99)
        self.assertEqual(self.companion.happiness, 69)


if __name__ == "__main__":
    unittest.main()