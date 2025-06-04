from PySide6.QtWidgets import QListWidget, QLabel, QPushButton, QDialog
from _pytest.monkeypatch import MonkeyPatch
from pytestqt.qtbot import QtBot

from backend.api_key_config import api_key_config
from pages.core.drag_and_drop_files_widget import DragAndDropFilesWidget
from pages.core.match_options_widget import MatchOptionsWidget, check_if_api_key_exists_otherwise_prompt_user


# pylint: disable=unused-argument
def test_mixed_media_input_displays_error(qtbot: QtBot):
    drag_and_drop_files_widget = DragAndDropFilesWidget()
    drag_and_drop_files_widget.add_file_to_list("Iron Man (2008).mkv")
    drag_and_drop_files_widget.add_file_to_list("The.West.Wing.S01E01.mkv")

    match_options_widget = MatchOptionsWidget(drag_and_drop_files_widget, QListWidget())
    messages = match_options_widget.findChildren(QLabel)

    assert any("Cannot rename both movies and tv series at the same time!" in message.text()
               for message in messages)


def test_multiple_series_input_displays_error(qtbot: QtBot):
    drag_and_drop_files_widget = DragAndDropFilesWidget()
    drag_and_drop_files_widget.add_file_to_list("Andor.S01E02.mkv")
    drag_and_drop_files_widget.add_file_to_list("The.West.Wing.S01E01.mkv")

    match_options_widget = MatchOptionsWidget(drag_and_drop_files_widget, QListWidget())
    messages = match_options_widget.findChildren(QLabel)

    assert any("Cannot rename multiple tv series at the same time!" in message.text()
               for message in messages)


def test_movie_input_shows_correct_database_buttons(qtbot: QtBot):
    drag_and_drop_files_widget = DragAndDropFilesWidget()
    drag_and_drop_files_widget.add_file_to_list("Iron Man (2008).mkv")

    match_options_widget = MatchOptionsWidget(drag_and_drop_files_widget, QListWidget())
    buttons_text = [button.text().strip() for button in match_options_widget.findChildren(QPushButton)]

    assert "TheMovieDB" in buttons_text
    assert "OMDB" in buttons_text
    assert "Attempt to match by filename only" in buttons_text
    assert "TVMaze" not in buttons_text


def test_series_input_shows_correct_database_buttons(qtbot: QtBot):
    drag_and_drop_files_widget = DragAndDropFilesWidget()
    drag_and_drop_files_widget.add_file_to_list("The.West.Wing.S01E01.mkv")

    match_options_widget = MatchOptionsWidget(drag_and_drop_files_widget, QListWidget())
    buttons_text = [button.text().strip() for button in match_options_widget.findChildren(QPushButton)]

    assert "TheMovieDB" in buttons_text
    assert "OMDB" in buttons_text
    assert "Attempt to match by filename only" in buttons_text
    assert "TVMaze" in buttons_text


def test_api_key_check_with_canceled_prompt_returns_false(qtbot: QtBot, monkeypatch: MonkeyPatch):
    """Returns False when a user does not have an API and closes the prompt window."""
    # Make it so api_key_config.get() returns "".
    monkeypatch.setattr(api_key_config, "get", lambda key: "")

    # Simulates the user closing the API key prompt window.
    monkeypatch.setattr("pages.core.api_key_prompt_widget.ApiKeyPromptWidget.exec",
                        lambda self: QDialog.DialogCode.Rejected)

    assert not check_if_api_key_exists_otherwise_prompt_user("the_movie_db")


def test_api_key_is_entered_api_check_passes(qtbot: QtBot, monkeypatch: MonkeyPatch):
    monkeypatch.setattr(api_key_config, "get", lambda key: "")

    # Simulates the user entering an API key.
    monkeypatch.setattr("pages.core.api_key_prompt_widget.ApiKeyPromptWidget.exec",
                        lambda self: QDialog.DialogCode.Accepted)

    assert check_if_api_key_exists_otherwise_prompt_user("the_movie_db")


def test_api_key_check_with_existing_api_key_returns_true(qtbot: QtBot, monkeypatch: MonkeyPatch):
    monkeypatch.setattr(api_key_config, "get", lambda key: "Sample_key")

    assert check_if_api_key_exists_otherwise_prompt_user("tvmaze")
