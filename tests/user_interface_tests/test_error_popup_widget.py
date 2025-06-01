from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QPushButton, QDialog
from pytestqt.qtbot import QtBot

from backend.error_popup_widget import ErrorPopupWidget


def test_error_popup_correctly_displays_error_text(qtbot: QtBot):
    error_popup = ErrorPopupWidget("[Error Message]")
    qtbot.addWidget(error_popup)

    # Ensure that the error message is set correctly. There is only one QLabel in ErrorPopupWidget.
    assert error_popup.findChild(QLabel).text() == "[Error Message]"


def test_on_confirmation_button_clicked_error_popup_closes(qtbot: QtBot):
    error_popup = ErrorPopupWidget("")
    qtbot.addWidget(error_popup)

    # Click the confirmation button.
    qtbot.mouseClick(error_popup.findChild(QPushButton), Qt.MouseButton.LeftButton)

    # Check to see if the popup closes.
    qtbot.waitUntil(lambda: not error_popup.isVisible())
    assert error_popup.result() in (QDialog.DialogCode.Accepted, QDialog.DialogCode.Rejected)
