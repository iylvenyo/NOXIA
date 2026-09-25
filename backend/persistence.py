## this file saves and loads companions progress using JSON
import json
from pathlib import Path

from backend.companion import Companion


class PersistenceService:
    def __init__(self):
        project_folder = Path(__file__).resolve().parent.parent
        self.save_file = project_folder / "data" / "save_data.json"

    def save(self, companion):
        self.save_file.parent.mkdir(exist_ok=True)

        with open(self.save_file, "w", encoding="utf-8") as file:
            json.dump(companion.to_dict(), file, indent=4)

    def load(self):
        if not self.save_file.exists():
            return Companion()

        try:
            with open(self.save_file, "r", encoding="utf-8") as file:
                saved_data = json.load(file)

            return Companion.from_dict(saved_data)

        except (json.JSONDecodeError, OSError):
            print("The save file could not be loaded.")
            return Companion()