from pathlib import Path

from PySide6.QtCore import QMimeData, QUrl, QPoint
from PySide6.QtGui import QDropEvent, Qt
from pytestqt.qtbot import QtBot

from backend.media_record import MediaRecord
from pages.core.drag_and_drop_files_widget import DragAndDropFilesWidget


def _make_folder_with_files_and_subfolders(tmp_path: Path):
    """Add files and folders with files to a given folder and return a list of all files."""
    file1 = tmp_path / "a.txt"
    file1.touch()

    file2 = tmp_path / "Example Movie.mkv"
    file2.touch()

    subfolder1 = tmp_path / "subfolder1"
    subfolder1.mkdir()

    file3 = subfolder1 / "Iron Man (2008).mkv"
    file3.touch()

    subfolder2 = subfolder1 / "subfolder2"
    subfolder2.mkdir()

    file4 = subfolder2 / "Thunderbolts (2025).mkv"
    file4.touch()

    (tmp_path / "empty").mkdir()
    return file1.name, file2.name, file3.name, file4.name


def test_drop_directory_adds_all_files_recursively(qtbot: QtBot, tmp_path: Path):
    drag_and_drop_widget = DragAndDropFilesWidget()
    qtbot.addWidget(drag_and_drop_widget)
    files = _make_folder_with_files_and_subfolders(tmp_path)

    # Tests the DragAndDropFilesWidget with folders and files in tmp_path.
    test_payload = QMimeData()
    test_payload.setUrls([QUrl.fromLocalFile(str(tmp_path))])
    drop_event = QDropEvent(
        QPoint(0, 0),
        Qt.DropAction.CopyAction,
        test_payload,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier
    )

    drag_and_drop_widget.dropEvent(drop_event)

    file_names_in_widget = sorted(drag_and_drop_widget.item(i).text() for i in range(drag_and_drop_widget.count()))
    file_names_from_tmp_folder = sorted(file_name for file_name in files)
    assert file_names_in_widget == file_names_from_tmp_folder


def test_drag_and_drop_event_stores_file_name(qtbot: QtBot, tmp_path: Path):
    """Simulates an OS-style drop into the widget"""
    drag_and_drop_widget = DragAndDropFilesWidget()
    qtbot.addWidget(drag_and_drop_widget)
    temp_file = tmp_path / "The.West.Wing.S01E01.mkv"
    temp_file.touch()
    # Create the payload that'll be used in the QDropEvent.
    test_payload = QMimeData()
    test_payload.setUrls([QUrl.fromLocalFile(str(temp_file))])
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
