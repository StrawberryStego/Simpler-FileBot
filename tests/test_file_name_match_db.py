from backend.media_record import MediaRecord
from databases.file_name_match_db import FileNameMatchDB


def test_create_file_name_match_db_with_correct_inputs():
    media_records = [MediaRecord("The.West.Wing.S01E01.Pilot.mkv"), MediaRecord("The.West.Wing.S01E02.mkv")]
    database = FileNameMatchDB(media_records, True)

    assert len(database.media_records) == 2
    assert database.is_tv_series


def test_retrieve_media_titles_from_movies_success():
    media_records = [MediaRecord("Iron Man (2008).mkv"), MediaRecord("Oppenheimer (2023).mp4")]
    database = FileNameMatchDB(media_records)

    matched_titles = database.retrieve_media_titles_from_db()

    assert matched_titles[0] == "Iron Man"
    assert matched_titles[1] == "Oppenheimer"


def test_retrieve_media_titles_from_tv_show_success():
    media_records = [MediaRecord("The.West.Wing.S01E01.Pilot.mkv"), MediaRecord("The.West.Wing.S01E08.Enemies.mkv")]
    database = FileNameMatchDB(media_records, True)

    matched_titles = database.retrieve_media_titles_from_db()

    assert matched_titles[0] == "Pilot"
    assert matched_titles[1] == "Enemies"


def test_retrieve_media_titles_from_empty_list_returns_empty_list():
    movies_database = FileNameMatchDB([], True)
    tv_show_database = FileNameMatchDB([], False)

    assert len(movies_database.retrieve_media_titles_from_db()) == 0
    assert len(tv_show_database.retrieve_media_titles_from_db()) == 0


def test_retrieve_media_years_success():
    database = FileNameMatchDB([MediaRecord("The.West.Wing.1999.S01E10.mkv")], True)

    assert database.retrieve_media_years_from_db()[0] == 1999


def test_retrieve_media_years_from_files_without_years_returns_none():
    database = FileNameMatchDB([MediaRecord("Boston.Legal.S05E02.mkv")], True)

    assert database.retrieve_media_years_from_db()[0] is None
