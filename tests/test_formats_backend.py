import pytest

from backend import formats_backend
from backend.formats_backend import retrieve_formats_as_dictionary, delete_and_recreate_formats_file, \
    retrieve_movies_format_from_formats_file, save_new_movies_format_to_formats_file, \
    retrieve_series_format_from_formats_file, save_new_series_format_to_formats_file


# pylint: disable=unused-argument, redefined-outer-name
@pytest.fixture
def redirect_formats_file_path_to_temp_file(tmp_path):
    """Redirect 'FORMATS_FILE_PATH' to a pytest temporary file, then put it back afterward."""
    fake_path = tmp_path / "formats.json"

    original_path = formats_backend.FORMATS_FILE_PATH
    formats_backend.FORMATS_FILE_PATH = str(fake_path)

    # Start each test with a clean default file.
    delete_and_recreate_formats_file()

    # Provide the fake path to tests.
    yield fake_path

    # Restore the original file path so later tests behave normally.
    formats_backend.FORMATS_FILE_PATH = original_path


def test_retrieve_formats_successful(redirect_formats_file_path_to_temp_file):
    formats = retrieve_formats_as_dictionary()

    assert formats.get("movie_format") == "{movie_name} ({year})"
    assert formats.get("series_format") == "S{season_number}E{episode_number} - {episode_title}"


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
