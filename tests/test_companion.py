import unittest

from backend.companion import Companion


class TestCompanion(unittest.TestCase):
    def test_default_values(self):
        companion = Companion()

        self.assertEqual(companion.name, "NOXIA")
        self.assertEqual(companion.relationship_points, 0)
        self.assertEqual(companion.hunger, 20)
        self.assertEqual(companion.energy, 100)
        self.assertEqual(companion.happiness, 70)
        self.assertEqual(companion.mood, "neutral")

    def test_stats_cannot_go_over_100(self):
        companion = Companion()

        companion.hunger = 150
        companion.energy = 120
        companion.happiness = 200

        companion.keep_stats_in_range()

        self.assertEqual(companion.hunger, 100)
        self.assertEqual(companion.energy, 100)
        self.assertEqual(companion.happiness, 100)

    def test_stats_cannot_go_below_zero(self):
        companion = Companion()

        companion.hunger = -10
        companion.energy = -20
        companion.happiness = -30

        companion.keep_stats_in_range()

        self.assertEqual(companion.hunger, 0)
        self.assertEqual(companion.energy, 0)
        self.assertEqual(companion.happiness, 0)

    def test_companion_can_be_converted_to_dictionary(self):
        companion = Companion()
        companion.relationship_points = 12

        data = companion.to_dict()

        self.assertEqual(data["name"], "NOXIA")
        self.assertEqual(data["relationship_points"], 12)


if __name__ == "__main__":
    unittest.main()