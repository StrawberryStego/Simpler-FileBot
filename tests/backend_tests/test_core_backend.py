import os

import pytest

from backend.core_backend import (match_titles_using_db_and_format, get_invalid_file_names_and_fixes,
                                  perform_file_renaming, create_formatted_title)
from backend.media_record import MediaRecord
from databases.file_name_match_db import FileNameMatchDB


def test_match_titles_using_db_and_format_using_episodes_list_success():
    media_records = [
        MediaRecord("The.West.Wing.S01E01.Pilot.mkv"),
        MediaRecord("The.West.Wing.S01E08.Enemies.mkv")
    ]
    database = FileNameMatchDB(media_records, True)

    matched_titles = match_titles_using_db_and_format(database)

    # Change these lines to match the actual backend output
    assert matched_titles[0] == "The West Wing - S01E01 - Pilot.mkv"
    assert matched_titles[1] == "The West Wing - S01E08 - Enemies.mkv"


def test_match_titles_using_db_and_format_using_movies_list_success():
    media_records = [MediaRecord("The Lion King (1994).mkv"), MediaRecord("The Lion King (2019).mkv")]
    database = FileNameMatchDB(media_records)

    matched_titles = match_titles_using_db_and_format(database)

    assert matched_titles[0] == "The Lion King (1994).mkv"
    assert matched_titles[1] == "The Lion King (2019).mkv"


def test_get_invalid_file_names_and_fixes():
    file_names = ["Good Name.mkv", "Bad? Name 1.mp4", "S01E01 - Is this fine?.mkv", "<Title> - Hi!.mkv"]

    invalid_file_names_and_fixes = get_invalid_file_names_and_fixes(file_names)

    assert invalid_file_names_and_fixes.get("Bad? Name 1.mp4") == "Bad Name 1.mp4"
    assert invalid_file_names_and_fixes.get("S01E01 - Is this fine?.mkv") == "S01E01 - Is this fine.mkv"
    assert invalid_file_names_and_fixes.get("<Title> - Hi!.mkv") == "Title - Hi!.mkv"


def test_file_rename_success():
    old_file_name = "old.txt"
    new_file_name = "new.txt"
    # Set up the temporary files.
    with open(old_file_name, "w", encoding="utf-8") as file:
        file.write("Hello World!")

    assert os.path.exists(old_file_name)
    try:
        perform_file_renaming([old_file_name], [new_file_name])
        assert not os.path.exists(old_file_name)
        with open(new_file_name, "r", encoding="utf-8") as file:
            content = file.read()
        assert content == "Hello World!"
    finally:
        # Clean up temporary files.
        for file_name in (old_file_name, new_file_name):
            try:
                os.remove(file_name)
            except OSError:
                pass


def test_missing_file_raises_oserror():
    missing_file = "does_not_exist.txt"
    target = "whatever.txt"

    try:
        with pytest.raises(OSError):
            perform_file_renaming([missing_file], [target])
    finally:
        # Clean up any test files.
        for file_name in (missing_file, target):
            try:
                os.remove(file_name)
            except OSError:
                pass


def test_invalid_lists_for_renaming_raises_valueerror():
    old_file_list = ["1", "2"]
    new_file_list = ["1", "2", "3"]

    with pytest.raises(ValueError) as error_info:
        perform_file_renaming(old_file_list, new_file_list)

    error_msg = str(error_info)
    assert "2 files" in error_msg and "3 files" in error_msg


def test_create_formatted_series_title_correctly():
    format_template = "{series_name} ({year}) - S{season_number}E{episode_number} - {episode_title}"
    series_context: dict = {
        "series_name": "The Blacklist",
        "year": "2013",
        "season_number": "03",
        "episode_number": "10",
        "episode_title": None
    }

    formatted_title = create_formatted_title(format_template, series_context)

    assert formatted_title == "The Blacklist (2013) - S03E10 - {None}"


def test_create_formatted_movie_title_correctly():
    format_template = "{year} {movie_name} ({year})"
    movie_context: dict = {
        "movie_name": "Warfare",
        "year": "2025"
    }

    formatted_title = create_formatted_title(format_template, movie_context)

    assert formatted_title == "2025 Warfare (2025)"
