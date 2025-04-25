import json
import os
from functools import wraps
from json import JSONDecodeError
from pathlib import Path

from PySide6.QtGui import QGuiApplication, Qt
from platformdirs import user_data_dir

SETTINGS_FILE_PATH = os.path.join(user_data_dir(appauthor=False, appname="Simpler FileBot"), "settings.json")


def ensure_settings_file(func):
    """Decorator to ensure that the settings page exists first."""

    # @wraps retains the original function's name and docstring... useful for debugging.
    @wraps(func)
    def wrapper(*args, **kwargs):
        initialize_settings_file_if_missing()
        return func(*args, **kwargs)

    return wrapper


def initialize_settings_file_if_missing():
    """Initializes a settings.json file if it does not exist."""
    default_settings = {
        # 'Dark' or 'Light'... defaults to Dark theme if color scheme could not be found.
        "theme": (Qt.ColorScheme.Dark.name
                  if QGuiApplication.styleHints().colorScheme() == Qt.ColorScheme.Unknown
                  else QGuiApplication.styleHints().colorScheme().name),
        "excluded_folders": []
    }

    path = Path(SETTINGS_FILE_PATH)

    # Create the parent directories of settings.json if missing.
    path.parent.mkdir(parents=True, exist_ok=True)

    # Create settings file with defaults if missing.
    if not path.is_file():
        with path.open("w", encoding="utf-8") as file:
            json.dump(default_settings, file, indent=4)


def delete_and_recreate_settings_file():
    Path(SETTINGS_FILE_PATH).unlink(missing_ok=True)
    initialize_settings_file_if_missing()


@ensure_settings_file
def retrieve_settings_as_dictionary() -> dict:
    """Retrieves settings.json in the form of a Python dictionary."""
    path = Path(SETTINGS_FILE_PATH)

    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except JSONDecodeError:
        # Remove the bad settings file and reinitialize with default settings.
        path.unlink(missing_ok=True)
        initialize_settings_file_if_missing()

        # Return the newly created, default settings file as a dictionary.
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)


@ensure_settings_file
def get_theme_from_settings() -> str:
    """Returns the theme from settings.json. Defaults to 'Dark' if settings are erroneous."""
    return retrieve_settings_as_dictionary().get("theme", "Dark")


@ensure_settings_file
def save_new_theme_to_settings(scheme: Qt.ColorScheme):
    """Update the “theme” key in settings.json to either 'Light' or 'Dark'."""
    path = Path(SETTINGS_FILE_PATH)

    # Load existing settings.
    settings = retrieve_settings_as_dictionary()
    settings["theme"] = scheme.name

    # Write settings back to settings.json
    with path.open("w", encoding="utf-8") as file:
        json.dump(settings, file, indent=4)


@ensure_settings_file
def add_excluded_folder(folder_path: str):
    """Add a folder to the 'excluded_folders' list in settings.json."""
    path = Path(SETTINGS_FILE_PATH)

    settings = retrieve_settings_as_dictionary()
    # Use a set to prevent duplicates.
    excluded_folders: set = set(settings.get("excluded_folders", []))
    excluded_folders.add(folder_path)

    settings["excluded_folders"] = sorted(excluded_folders)

    with path.open("w", encoding="utf-8") as file:
        json.dump(settings, file, indent=4)


@ensure_settings_file
def get_excluded_folders() -> list[str]:
    return retrieve_settings_as_dictionary().get("excluded_folders", [])
