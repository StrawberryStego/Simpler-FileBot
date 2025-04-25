import json
import os
import tempfile

from backend.formats_backend import initialize_formats_file, read_formats_file, write_formats_file, update_format
from backend import formats_backend


def test_initialize_formats_file():
    # Create a temporary directory for testing
    temp_dir = tempfile.mkdtemp()
    test_formats_path = os.path.join(temp_dir, "test_formats.json")

    # Save original path and set temporary path
    original_path = formats_backend.formats_file_path
    formats_backend.formats_file_path = test_formats_path

    try:
        # Initialize the file
        initialize_formats_file()

        # Assert that the file exists
        assert os.path.exists(test_formats_path)

        # Assert that it has the correct default formats
        with open(test_formats_path, "r", encoding="utf-8") as file:
            formats = json.load(file)

        assert formats["movie_format"] == "{movie_name} ({year})"
        assert formats["series_format"] == "{series_name} - S{season_number}E{episode_number} - {episode_title}"

    finally:
        # Clean up and restore original path
        formats_backend.formats_file_path = original_path
        if os.path.exists(test_formats_path):
            os.remove(test_formats_path)
        os.rmdir(temp_dir)


def test_read_formats_file():
    # Create a temporary directory for testing
    temp_dir = tempfile.mkdtemp()
    test_formats_path = os.path.join(temp_dir, "test_formats.json")

    # Save original path and set temporary path
    original_path = formats_backend.formats_file_path
    formats_backend.formats_file_path = test_formats_path

    try:
        # Create a test formats file with known content
        test_formats = {
            "movie_format": "Test Movie Format",
            "series_format": "Test Series Format"
        }

        with open(test_formats_path, "w", encoding="utf-8") as file:
            json.dump(test_formats, file)

        # Read the formats file
        formats = read_formats_file()

        # Assert that the content matches
        assert formats["movie_format"] == "Test Movie Format"
        assert formats["series_format"] == "Test Series Format"

    finally:
        # Clean up and restore original path
        formats_backend.formats_file_path = original_path
        if os.path.exists(test_formats_path):
            os.remove(test_formats_path)
        os.rmdir(temp_dir)


def test_write_formats_file():
    # Create a temporary directory for testing
    temp_dir = tempfile.mkdtemp()
    test_formats_path = os.path.join(temp_dir, "test_formats.json")

    # Save original path and set temporary path
    original_path = formats_backend.formats_file_path
    formats_backend.formats_file_path = test_formats_path

    try:
        # Create test data
        test_formats = {
            "movie_format": "Custom Movie Format",
            "series_format": "Custom Series Format"
        }

        # Write to formats file
        write_formats_file(test_formats)

        # Assert file exists
        assert os.path.exists(test_formats_path)

        # Read the file and verify content
        with open(test_formats_path, "r", encoding="utf-8") as file:
            formats = json.load(file)

        assert formats["movie_format"] == "Custom Movie Format"
        assert formats["series_format"] == "Custom Series Format"

    finally:
        # Clean up and restore original path
        formats_backend.formats_file_path = original_path
        if os.path.exists(test_formats_path):
            os.remove(test_formats_path)
        os.rmdir(temp_dir)


def test_update_format():
    # Create a temporary directory for testing
    temp_dir = tempfile.mkdtemp()
    test_formats_path = os.path.join(temp_dir, "test_formats.json")

    # Save original path and set temporary path
    original_path = formats_backend.formats_file_path
    formats_backend.formats_file_path = test_formats_path

    try:
        # Initialize the file
        initialize_formats_file()

        # Update a format
        new_format = "Custom {movie_name} - {year}"
        update_format("movie_format", new_format)

        # Read formats and verify update
        with open(test_formats_path, "r", encoding="utf-8") as file:
            formats = json.load(file)

        assert formats["movie_format"] == new_format
        assert formats["series_format"] == "{series_name} - S{season_number}E{episode_number} - {episode_title}"

    finally:
        # Clean up and restore original path
        formats_backend.formats_file_path = original_path
        if os.path.exists(test_formats_path):
            os.remove(test_formats_path)
        os.rmdir(temp_dir)
