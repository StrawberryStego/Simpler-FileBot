import pytest
from PySide6.QtCore import Qt

from backend import settings_backend
from backend.settings_backend import retrieve_settings_as_dictionary, retrieve_theme_from_settings, \
    delete_and_recreate_settings_file, save_new_theme_to_settings, retrieve_excluded_folders, add_excluded_folder, \
    remove_excluded_folder


# pylint: disable=unused-argument, redefined-outer-name
@pytest.fixture
def redirect_settings_file_path_to_temp_file(tmp_path):
    """Redirect 'SETTINGS_FILE_PATH' to a pytest temporary file, then put it back afterward."""
    fake_path = tmp_path / "settings.json"

    original_path = settings_backend.SETTINGS_FILE_PATH
    settings_backend.SETTINGS_FILE_PATH = str(fake_path)

    # Start each test with a clean default file.
    delete_and_recreate_settings_file()

    # Provide the fake path to tests.
    yield fake_path

    # Restore the original file path so later tests behave normally.
    settings_backend.SETTINGS_FILE_PATH = original_path


# pylint: disable=condition-evals-to-constant
def test_retrieve_settings_successful(redirect_settings_file_path_to_temp_file):
    settings = retrieve_settings_as_dictionary()

    assert settings.get("theme") == "Light" or "Dark"
    assert len(settings.get("excluded_folders")) == 0


# pylint: disable=condition-evals-to-constant
def test_retrieve_theme_from_settings_successful(redirect_settings_file_path_to_temp_file):
    retrieved_theme = retrieve_theme_from_settings()

    assert retrieved_theme == "Light" or "Dark"


def test_save_new_theme_to_settings_successful(redirect_settings_file_path_to_temp_file):
    save_new_theme_to_settings(Qt.ColorScheme.Unknown)

    assert retrieve_theme_from_settings() == "Unknown"


def test_retrieve_excluded_folders_successfully(redirect_settings_file_path_to_temp_file):
    assert len(retrieve_excluded_folders()) == 0


def test_add_excluded_folder_saves_successfully(redirect_settings_file_path_to_temp_file):
    test_folder = "C:/Exclude This Folder/"

    add_excluded_folder(test_folder)

    assert retrieve_excluded_folders()[0] == test_folder


def test_remove_excluded_folder_deletes_successfully(redirect_settings_file_path_to_temp_file):
    test_folder = "C:/Remove This Folder Once Added/"

    add_excluded_folder(test_folder)

    assert retrieve_excluded_folders()[0] == test_folder

    remove_excluded_folder(test_folder)

    assert len(retrieve_excluded_folders()) == 0
