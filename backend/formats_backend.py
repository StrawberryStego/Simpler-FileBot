import json
import os

from platformdirs import user_data_dir

formats_file_path = os.path.join(user_data_dir(appauthor=False, appname="Simpler-FileBot"), "formats.json")

def initialize_formats_file():
    # Creates the formats.json file if it does not exist. Initializes it
    # with default formats for movies and TV episodes.

    try:
        os.makedirs(os.path.dirname(formats_file_path), exist_ok=True)
        if not os.path.isfile(formats_file_path):
            default_formats = {
                "movie_format": "{movie_name} ({year})",
                "series_format": "{series_name} - S{season_number}E{episode_number} - {episode_title}"
            }
            with open(formats_file_path, "w", encoding="utf-8") as file:
                json.dump(default_formats, file, indent=4)
    except (OSError, IOError) as e:
        print(f"File or directory error initializing formats.json: {e}")
    except json.JSONDecodeError as e:
        print(f"Unexpected JSON serialization error: {e}")


def read_formats_file():
    # Reads and returns the content of the formats.json file.

    try:
        with open(formats_file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print("Formats file not found. Initializing a new one...")
        initialize_formats_file()
        return read_formats_file()
    except json.JSONDecodeError as e:
        print(f"Error reading formats file: {e}")
        return {}


def write_formats_file(data):
    # Overwrites the formats.json file with the provided data.

    try:
        with open(formats_file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
    except (OSError, IOError) as e:
        print(f"Filesystem error writing formats.json: {e}")
    except TypeError as e:
        print(f"Invalid data passed to json.dump(): {e}")


def update_format(key, value):
    # Updates a single format entry (e.g., 'movie_format' or 'series_format') in formats.json.
    try:
        data = read_formats_file()
        if not isinstance(data, dict):
            raise ValueError("formats.json does not contain a valid dictionary")
        data[key] = value
        write_formats_file(data)
    except (OSError, IOError) as e:
        print(f"File access error during format update: {e}")
    except (json.JSONDecodeError, TypeError, ValueError) as e:
        print(f"Data error while updating format: {e}")
