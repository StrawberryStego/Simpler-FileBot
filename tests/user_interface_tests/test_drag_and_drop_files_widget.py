from pathlib import Path

from PySide6.QtCore import QMimeData, QUrl, QPoint
from PySide6.QtGui import QDropEvent, Qt
from pytestqt.qtbot import QtBot

from backend.media_record import MediaRecord
from pages.core.drag_and_drop_files_widget import DragAndDropFilesWidget


def test_drag_and_drop_event_stores_file_name(qtbot: QtBot, tmp_path: Path):
    """Simulates an OS-style drop into the widget"""
    drag_and_drop_widget = DragAndDropFilesWidget()
    qtbot.addWidget(drag_and_drop_widget)
    temp_file_path = tmp_path / "The.West.Wing.S01E01.mkv"
    # Create the payload that'll be used in the QDropEvent.
    test_payload = QMimeData()
    test_payload.setUrls([QUrl.fromLocalFile(temp_file_path)])
    # Create a QDropEvent with our test payload.
    drop_event = QDropEvent(
        QPoint(0, 0),
        Qt.DropAction.CopyAction,
        test_payload,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier
    )

    drag_and_drop_widget.dropEvent(drop_event)

    assert drag_and_drop_widget.count() == 1
    assert drag_and_drop_widget.item(0).text() == "The.West.Wing.S01E01.mkv"


def test_add_file_to_list_stores_media_record(qtbot: QtBot, tmp_path: Path):
    drag_and_drop_widget = DragAndDropFilesWidget()
    qtbot.addWidget(drag_and_drop_widget)
    temp_file_path = tmp_path / "Andor.S02E09.mkv"

    drag_and_drop_widget.add_file_to_list(str(temp_file_path))

    list_item = drag_and_drop_widget.item(0)
    data = list_item.data(Qt.ItemDataRole.UserRole)
    assert list_item.text() == "Andor.S02E09.mkv"
    assert isinstance(data, MediaRecord)
    assert data.full_file_path == str(temp_file_path)
