import tempfile
import unittest
from pathlib import Path

from backend.companion import Companion
from backend.persistence import PersistenceService


class TestPersistenceService(unittest.TestCase):
    def test_save_and_load(self):
        with tempfile.TemporaryDirectory() as temporary_folder:
            service = PersistenceService()

            service.save_file = (
                Path(temporary_folder) / "test_save.json"
            )

            companion = Companion()
            companion.relationship_points = 25
            companion.relationship_stage = "attached"
            companion.hunger = 60
            companion.energy = 75
            companion.happiness = 85
            companion.unlocked_content = ["extra_dialogue"]

            service.save(companion)
            loaded_companion = service.load()

            self.assertEqual(
                loaded_companion.relationship_points,
                25,
            )
            self.assertEqual(
                loaded_companion.relationship_stage,
                "attached",
            )
            self.assertEqual(loaded_companion.hunger, 60)
            self.assertEqual(loaded_companion.energy, 75)
            self.assertEqual(loaded_companion.happiness, 85)
            self.assertIn(
                "extra_dialogue",
                loaded_companion.unlocked_content,
            )

    def test_missing_save_file_creates_new_companion(self):
        with tempfile.TemporaryDirectory() as temporary_folder:
            service = PersistenceService()

            service.save_file = (
                Path(temporary_folder) / "missing.json"
            )

            companion = service.load()

            self.assertEqual(companion.name, "NOXIA")
            self.assertEqual(companion.relationship_points, 0)


if __name__ == "__main__":
    unittest.main()