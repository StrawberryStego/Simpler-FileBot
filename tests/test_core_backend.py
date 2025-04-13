from backend.core_backend import match_titles_using_db_and_format, get_invalid_file_names_and_fixes
from backend.media_record import MediaRecord
from databases.file_name_match_db import FileNameMatchDB


def test_match_titles_using_db_and_format_using_episodes_list_success():
    media_records = [MediaRecord("The.West.Wing.S01E01.Pilot.mkv"), MediaRecord("The.West.Wing.S01E08.Enemies.mkv")]
    database = FileNameMatchDB(media_records, True)

    matched_titles = match_titles_using_db_and_format(database)

    assert matched_titles[0] == "S01E01 - Pilot.mkv"
    assert matched_titles[1] == "S01E08 - Enemies.mkv"


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
