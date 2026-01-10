from pathlib import Path

from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QMenu, QDialog, QVBoxLayout, QLabel

from backend.media_record import MediaRecord
from backend.utils import resource_path


class DragAndDropFilesWidget(QListWidget):
    """
    QListWidget subclass to allow for drag-and-drop files functionality.
    dragEnterEvent(), dragMoveEvent(), and dropEvent() need to be overridden for that to work.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

        # Allow the user to right-click a QListWidgetItem to show information about the MediaRecord.
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu_on_right_click)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                self.add_path(url.toLocalFile())

            event.acceptProposedAction()

    def add_path(self, file_path: str):
        """
        Add a single file or file(s) in a directory to QListWidget.
        TODO: Rename these variables. I hate Python and it is unclear which variable is a Path or String object.
        """
        path = Path(file_path)

        if path.is_file():
            self.add_file_to_list(file_path)

        if path.is_dir():
            # Iterate through a folder recursively and add all files to the QListWidget.
            for file in path.rglob("*"):
                # Do not add the folder as a file.
                if file.is_file():
                    self.add_file_to_list(str(file))

    def add_file_to_list(self, file_path: str):
        """Create a MediaRecord from a file path and insert the record into the widget list."""
        media_record = MediaRecord(file_path)

        # Set the displayed text for the file and tie the corresponding MediaRecord to that list entry.
        list_item = QListWidgetItem(media_record.file_name)
        list_item.setData(Qt.ItemDataRole.UserRole, media_record)
        self.addItem(list_item)

    def show_context_menu_on_right_click(self, position: QPoint):
        """Show a context menu when a user right-clicks on a QListWidgetItem."""
        item = self.itemAt(position)
        if item is None:
            return

        # Recover the MediaRecord data from the QListWidgetItem.
        media_record: MediaRecord = item.data(Qt.ItemDataRole.UserRole)

        context_menu = QMenu(self)
        metadata_choice = context_menu.addAction("Show metadata")
        action = context_menu.exec(self.viewport().mapToGlobal(position))

        if action == metadata_choice:
            self.__show_metadata_dialog(media_record)

    @staticmethod
    def __show_metadata_dialog(media_record: MediaRecord):
        metadata_dialog = QDialog()
        metadata_dialog.setWindowIcon(QIcon(QPixmap(resource_path("resources/Alternative App Logo.png"))))
        metadata_dialog.setWindowTitle(media_record.file_name)

        metadata_dialog_layout = QVBoxLayout(metadata_dialog)

        for key, value in media_record.metadata.items():
            metadata_dialog_layout.addWidget(QLabel(f"{key}: {value}"))

        metadata_dialog.exec()
