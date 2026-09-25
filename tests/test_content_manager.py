import unittest

from backend.companion import Companion
from backend.content_manager import ContentManager

class TestContentManager(unittest.TestCase):
    def setUp(self):
        self.companion = Companion()
        self.manager = ContentManager()
    def test_nothing_is_unlocked_at_start(self):
        self.manager.update_unlocks(self.companion)

        self.assertEqual(self.companion.unlocked_content, [])

    def test_extra_dialogue_unlocks(self):
        self.companion.relationship_points = 5

        self.manager.update_unlocks(self.companion)

        self.assertIn(
            "extra_dialogue",
            self.companion.unlocked_content,
        )

    def test_music_unlocks(self):
        self.companion.relationship_points = 15

        self.manager.update_unlocks(self.companion)

        self.assertIn(
            "music_mode",
            self.companion.unlocked_content,
        )

    def test_minigame_unlocks(self):
        self.companion.relationship_points = 30

        self.manager.update_unlocks(self.companion)

        self.assertIn(
            "minigame_1",
            self.companion.unlocked_content,
        )

    def test_special_visuals_unlock(self):
        self.companion.relationship_points = 50

        self.manager.update_unlocks(self.companion)

        self.assertIn(
            "special_visuals",
            self.companion.unlocked_content,
        )

    def test_unlock_is_not_added_twice(self):
        self.companion.relationship_points = 5

        self.manager.update_unlocks(self.companion)
        self.manager.update_unlocks(self.companion)

        number_of_unlocks = self.companion.unlocked_content.count(
            "extra_dialogue"
        )

        self.assertEqual(number_of_unlocks, 1)


if __name__ == "__main__":
    unittest.main()