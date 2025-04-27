import json
import os
from json import JSONDecodeError

from pathlib import Path
from functools import wraps
from platformdirs import user_data_dir

FORMATS_FILE_PATH = os.path.join(user_data_dir(appauthor=False, appname="Simpler FileBot"), "formats.json")


def ensure_formats_file(func):
    """Decorator to ensure formats file exists first."""

    # @wraps retains the original function's name and docstring... useful for debugging.
    @wraps(func)
    def wrapper(*args, **kwargs):
        initialize_formats_file_if_missing()
        return func(*args, **kwargs)

    return wrapper


def initialize_formats_file_if_missing():
    """Initializes a formats.json file if missing."""

    default_formats = {
        "movie_format": "{movie_name} ({year})",
        "series_format": "S{season_number}E{episode_number} - {episode_title}"
    }

    path = Path(FORMATS_FILE_PATH)

    # Create the parent directories of formats.json if missing.
    path.parent.mkdir(parents=True, exist_ok=True)

    # Create formats file with defaults if missing.
    if not path.is_file():
        with path.open("w", encoding="utf-8") as file:
            json.dump(default_formats, file, indent=4)


def delete_and_recreate_formats_file():
    Path(FORMATS_FILE_PATH).unlink(missing_ok=True)
    initialize_formats_file_if_missing()


@ensure_formats_file
def retrieve_formats_as_dictionary() -> dict:
    """Retrieves formats.json in the form of a Python dictionary."""
    path = Path(FORMATS_FILE_PATH)

    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except JSONDecodeError:
        delete_and_recreate_formats_file()

        # Return the newly created, default settings file as a dictionary.
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)


@ensure_formats_file
def retrieve_movies_format_from_formats_file():
    return retrieve_formats_as_dictionary().get("movie_format", "{movie_name} ({year})")


@ensure_formats_file
def save_new_movies_format_to_formats_file(new_movie_format: str):
    path = Path(FORMATS_FILE_PATH)

    # Load existing formats.
    formats: dict = retrieve_formats_as_dictionary()
    formats["movie_format"] = new_movie_format

    with path.open("w", encoding="utf-8") as file:
        json.dump(formats, file, indent=4)


@ensure_formats_file
def retrieve_series_format_from_formats_file():
    return retrieve_formats_as_dictionary().get("series_format", "S{season_number}E{episode_number} - {episode_title}")


@ensure_formats_file
def save_new_series_format_to_formats_file(new_series_format: str):
    path = Path(FORMATS_FILE_PATH)

    # Load existing formats.
    formats: dict = retrieve_formats_as_dictionary()
    formats["series_format"] = new_series_format

    with path.open("w", encoding="utf-8") as file:
        json.dump(formats, file, indent=4)
