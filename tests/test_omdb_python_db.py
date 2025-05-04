from unittest.mock import patch

from backend.media_record import MediaRecord
from databases.omdb_python_db import OMDBPythonDB


@patch("databases.omdb_python_db.retrieve_omdb_key", return_value="DUMMY_KEY")
@patch("databases.omdb_python_db.OMDBClient")
def test_movie_title_happy_path(mock_client_cls, _fake_key):
    mock_client = mock_client_cls.return_value
    mock_client.get.side_effect = [
        {"title": "Iron Man"},
        {"title": "Thunderbolts*"},
    ]

    database = OMDBPythonDB([MediaRecord("Iron Man (2008).mkv"), MediaRecord("Thunderbolts* (2025).mkv")], False)

    assert database.retrieve_media_titles_from_db() == ["Iron Man", "Thunderbolts*"]


@patch("databases.omdb_python_db.retrieve_omdb_key", return_value="DUMMY_KEY")
@patch("databases.omdb_python_db.OMDBClient")
def test_tv_episode_lookup_successful(mock_client_cls, _fake_key):
    mock_client = mock_client_cls.return_value
    mock_client.get.return_value = {"episodes": [
            {"episode": 1, "title": "Pilot"},
            {"episode": 2, "title": "Post Hoc, Ergo Propter Hoc"}
        ]}

    database = OMDBPythonDB([
        MediaRecord("The.West.Wing.S01E01.mkv"),
        MediaRecord("The.West.Wing.S01E02.mkv")],
        True)

    assert database.retrieve_media_titles_from_db() == ["Pilot", "Post Hoc, Ergo Propter Hoc"]


@patch("databases.omdb_python_db.retrieve_omdb_key", return_value="DUMMY_KEY")
@patch("databases.omdb_python_db.OMDBClient")
def test_movie_year_lookup_successful(mock_client_cls, _fake_key):
    mock_client = mock_client_cls.return_value
    mock_client.get.return_value = {"year": 2008}

    database = OMDBPythonDB([MediaRecord("Iron Man.mkv")], False)

    assert database.retrieve_media_years_from_db() == [2008]


@patch("databases.omdb_python_db.retrieve_omdb_key", return_value="DUMMY_KEY")
@patch("databases.omdb_python_db.OMDBClient")
def test_series_year_lookup_successful(mock_client_cls, _fake_key):
    mock_client = mock_client_cls.return_value
    mock_client.get.return_value = {"year": "1999-2006"}

    database = OMDBPythonDB([MediaRecord("The.West.Wing.S01E01.mkv")], True)

    assert database.retrieve_media_years_from_db() == [1999]
