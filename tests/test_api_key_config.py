import pytest

from backend import api_key_config
from backend.api_key_config import retrieve_the_movie_db_key, save_new_the_movie_db_key, retrieve_the_tv_db_key, \
    save_new_the_tv_db_key, retrieve_omdb_key, save_new_omdb_key
from backend.json_config import JSONConfig


# pylint: disable=unused-argument, redefined-outer-name
@pytest.fixture
def redirect_api_keys_file_path_to_temp_file(tmp_path, monkeypatch):
    """Redirect 'api_key_config' to a test one, then put it back afterward."""
    fake_path = tmp_path / "api_keys.json"

    test_api_key_config = JSONConfig(
        "api_keys.json",
        {
            "the_movie_db": "",
            "the_tv_db": "",
            "omdb": ""
        }
    )
    test_api_key_config.path = fake_path
    test_api_key_config.delete_and_recreate_file()

    # Set api_key_config to test_api_key_config... monkeypatch will restore it automatically.
    monkeypatch.setattr(api_key_config, "api_key_config", test_api_key_config)

    yield fake_path


def test_retrieve_the_movie_db_key_default_value_retrieved(redirect_api_keys_file_path_to_temp_file):
    default_api_key: str = retrieve_the_movie_db_key()

    assert default_api_key == ""


def test_save_new_the_movie_db_key_new_value_retrieved(redirect_api_keys_file_path_to_temp_file):
    save_new_the_movie_db_key("[This is my TheMovieDB key]")
    retrieved_api_key = retrieve_the_movie_db_key()

    assert retrieved_api_key == "[This is my TheMovieDB key]"


def test_retrieve_the_tv_db_key_default_value_retrieved(redirect_api_keys_file_path_to_temp_file):
    default_api_key: str = retrieve_the_tv_db_key()

    assert default_api_key == ""


def test_save_new_the_tv_db_key_new_value_retrieved(redirect_api_keys_file_path_to_temp_file):
    save_new_the_tv_db_key("[This is my TheTVDB key]")
    retrieved_api_key = retrieve_the_tv_db_key()

    assert retrieved_api_key == "[This is my TheTVDB key]"


def test_retrieve_omdb_key_default_value_retrieved(redirect_api_keys_file_path_to_temp_file):
    default_api_key: str = retrieve_omdb_key()

    assert default_api_key == ""


def test_save_new_omdb_key_new_value_retrieved(redirect_api_keys_file_path_to_temp_file):
    save_new_omdb_key("[This is my OMDB key]")
    retrieved_api_key = retrieve_omdb_key()

    assert retrieved_api_key == "[This is my OMDB key]"
