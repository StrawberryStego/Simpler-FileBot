from backend.core_backend import match_titles_using_db_and_format
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
