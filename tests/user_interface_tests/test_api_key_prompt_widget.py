import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton, QDialog
from _pytest.monkeypatch import MonkeyPatch
from pytestqt.qtbot import QtBot

from backend.api_key_config import api_key_config
from pages.core.api_key_prompt_widget import ApiKeyPromptWidget


# pylint: disable=redefined-outer-name
@pytest.fixture
def mock_api_key_config(monkeypatch: MonkeyPatch):
    """Replace api_key_config (Used in ApiKeyPromptWidget) with a stub/mock."""
    mock_api_config = {}

    def fake_set(key: str, value: str):
        mock_api_config[key] = value

    # Mock api_key_config's set() method with a test one.
    monkeypatch.setattr(api_key_config, "set", fake_set)
    return mock_api_config


def test_on_cancel_button_clicked_api_key_prompt_widget_closes_with_reject_code(qtbot: QtBot, mock_api_key_config):
    api_key_prompt_widget = ApiKeyPromptWidget("", "")
    qtbot.addWidget(api_key_prompt_widget)

    # Click the cancel button.
    qtbot.mouseClick(api_key_prompt_widget.findChild(QPushButton, "cancel_button"), Qt.MouseButton.LeftButton)

    qtbot.waitUntil(lambda: not api_key_prompt_widget.isVisible())
    assert api_key_prompt_widget.result() == QDialog.DialogCode.Rejected
    assert mock_api_key_config == {}


def test_empty_input_keeps_dialog_open(qtbot: QtBot, mock_api_key_config):
    api_key_prompt_widget = ApiKeyPromptWidget("", "")
    qtbot.addWidget(api_key_prompt_widget)
    api_key_prompt_widget.show()
    qtbot.waitExposed(api_key_prompt_widget)

    # Input blank spaces into the api key field.
    api_key_prompt_widget.edit.setText("   ")
    # Click the save button without any actual key inputted.
    qtbot.mouseClick(api_key_prompt_widget.findChild(QPushButton, "save_button"), Qt.MouseButton.LeftButton)

    assert api_key_prompt_widget.isVisible()
    assert mock_api_key_config == {}


def test_input_key_value_is_correctly_saved(qtbot: QtBot, mock_api_key_config):
    api_key_prompt_widget = ApiKeyPromptWidget("my_database", "")
    qtbot.addWidget(api_key_prompt_widget)

    # Add a sample api key and click the save button.
    api_key_prompt_widget.edit.setText("sample_api_key")
    qtbot.mouseClick(api_key_prompt_widget.findChild(QPushButton, "save_button"), Qt.MouseButton.LeftButton)

    assert ("my_database", "sample_api_key") in mock_api_key_config.items()
