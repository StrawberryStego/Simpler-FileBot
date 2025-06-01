import pytest

from backend import formats_backend
from backend.formats_backend import (retrieve_movies_format_from_formats_file, save_new_movies_format_to_formats_file,
                                     retrieve_series_format_from_formats_file, save_new_series_format_to_formats_file)
from backend.json_config import JSONConfig


# pylint: disable=unused-argument, redefined-outer-name
@pytest.fixture
def redirect_formats_file_path_to_temp_file(tmp_path, monkeypatch):
    """Redirect 'formats_json_config' to a test one, then put it back afterward."""
    fake_path = tmp_path / "formats.json"

    test_json_config = JSONConfig(
        "formats.json",
        {"movie_format": "{movie_name} ({year})",
         "series_format": "S{season_number}E{episode_number} - {episode_title}"}
    )
    test_json_config.path = fake_path
    test_json_config.delete_and_recreate_file()

    # Set formats_json_config to test_json_config... monkeypatch will restore it automatically.
    monkeypatch.setattr(formats_backend, "formats_json_config", test_json_config)

    yield fake_path


def test_retrieve_movies_format_successful(redirect_formats_file_path_to_temp_file):
    retrieved_movie_format = retrieve_movies_format_from_formats_file()

    assert retrieved_movie_format == "{movie_name} ({year})"


def test_save_new_movies_format_to_formats_file_successful(redirect_formats_file_path_to_temp_file):
    new_movie_format = "Movie Year ({year})"

    save_new_movies_format_to_formats_file(new_movie_format)

    assert retrieve_movies_format_from_formats_file() == new_movie_format


def test_retrieve_series_format_successful(redirect_formats_file_path_to_temp_file):
    retrieved_series_format = retrieve_series_format_from_formats_file()

    assert retrieved_series_format == "S{season_number}E{episode_number} - {episode_title}"


def test_save_new_series_format_to_formats_file_successful(redirect_formats_file_path_to_temp_file):
    new_series_format = "E{episode_number}"

    save_new_series_format_to_formats_file(new_series_format)

    assert retrieve_series_format_from_formats_file() == new_series_format
