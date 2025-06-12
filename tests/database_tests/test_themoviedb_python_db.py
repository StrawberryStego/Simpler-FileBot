from unittest.mock import patch

from backend.media_record import MediaRecord
from databases.themoviedb_python_db import TheMovieDBPythonDB


def _simple_hit(title, date):
    return {"title": title, "release_date": date}


def _fake_season_payload(title, episode_number):
    return {"episodes": [{"episode_number": episode_number, "name": title}]}


@patch("databases.themoviedb_python_db.retrieve_the_movie_db_key", return_value="DUMMY_KEY")
@patch("tmdbsimple.Search")
def test_movie_title_happy_path(mock_search_cls, _fake_key):
    # Mock Search.movie() → { "results": [...] }.
    mock_search = mock_search_cls.return_value
    mock_search.movie.side_effect = [
        {"results": [_simple_hit("Oppenheimer", "2023-07-21")]},
        {"results": [_simple_hit("Interstellar", "2014-10-26")]},
    ]

    recs = [MediaRecord("Oppenheimer.2023.mkv"), MediaRecord("Interstellar.mkv")]
    db = TheMovieDBPythonDB(recs, is_tv_series=False)

    assert db.retrieve_media_titles_from_db() == ["Oppenheimer", "Interstellar"]


@patch("databases.themoviedb_python_db.retrieve_the_movie_db_key", return_value="DUMMY_KEY")
@patch("tmdbsimple.TV_Seasons")
@patch("tmdbsimple.Search")
def test_tv_episode_lookup_successful(mock_search_cls, mock_tv_episodes_cls, _fake_key):
    # Mock Search.tv() to give a single series hit.
    mock_search = mock_search_cls.return_value
    mock_search.tv.return_value = {
        "results": [{"id": 42, "first_air_date": "2010-04-17"}]
    }

    # Mock TV_Episodes(...).info() → {"name": ...}
    mock_tv_episodes_cls.return_value.info.return_value = _fake_season_payload("Winter Is Coming", 1)

    rec = MediaRecord("Game.of.Thrones.2011.S01E01.mkv")
    db = TheMovieDBPythonDB([rec], is_tv_series=True)

    assert db.retrieve_media_titles_from_db() == ["Winter Is Coming"]
