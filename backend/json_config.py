import json
from json import JSONDecodeError
from pathlib import Path

from platformdirs import user_data_dir


class JSONConfig:
    """Handle one JSON config file with local override support."""

    def __init__(self, filename: str, defaults: dict):
        local_dir = Path.cwd()
        portable_flag = local_dir / ".portable"

        if portable_flag.exists():
            # Use the local folder if .portable exists
            self.path = local_dir / filename
        else:
            # Otherwise use the standard system path
            self.path = Path(user_data_dir(appauthor=False, appname="Simpler FileBot")) / filename

        self.defaults = defaults
        self._ensure_exists()

    def get(self, key: str, default_value=None):
        self._ensure_exists()

        return self._read_from_json().get(key, default_value)

    def set(self, key: str, value):
        self._ensure_exists()

        data = self._read_from_json()
        data[key] = value
        self._write_to_json(data)

    def add(self, key, data_to_add):
        """Allows config to add values to a list in a JSON."""
        data = self._read_from_json()
        field: list = data.get(key, [])
        field.append(data_to_add)
        data[key] = sorted(field)

        self._write_to_json(data)

    def remove(self, key, data_to_remove):
        data = self._read_from_json()
        field: list = data.get(key, [])

        if data_to_remove in field:
            field.remove(data_to_remove)
            data[key] = field
            self._write_to_json(data)

    def delete_and_recreate_file(self):
        self.path.unlink(missing_ok=True)
        self._ensure_exists()

    def _ensure_exists(self):
        """Ensures that a JSON file exists before operations are executed."""

        # Create the parent directories of a json file if missing.
        self.path.parent.mkdir(parents=True, exist_ok=True)

        # Fixes issue #58. Python installations from the Microsoft Store does some funky directory changes that
        # moves the installation to a different local cache *silently*. Using resolve() sets self.path to the
        # actual location that Microsoft Store's Python puts our installations.
        self.path = self.path.resolve(strict=False)

        # Create the json file if missing with default values.
        if not self.path.is_file():
            with self.path.open("w", encoding="utf-8") as file:
                json.dump(self.defaults, file, indent=4)

    def _read_from_json(self) -> dict:
        try:
            with self.path.open("r", encoding="utf-8") as file:
                return json.load(file)
        except JSONDecodeError:
            self.delete_and_recreate_file()
            return self._read_from_json()

    def _write_to_json(self, data: dict):
        with self.path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
