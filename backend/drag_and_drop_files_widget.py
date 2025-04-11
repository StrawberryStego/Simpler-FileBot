from PySide6.QtCore import Qt
from PySide6.QtWidgets import QListWidget, QListWidgetItem

from backend.media_record import MediaRecord


class DragAndDropFilesWidget(QListWidget):
    """
    QListWidget subclass to allow for drag-and-drop files functionality.
    dragEnterEvent(), dragMoveEvent(), and dropEvent() need to be overridden for that to work.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                media_record = MediaRecord(file_path)

                # Set the displayed text for the file and tie the corresponding MediaRecord to that list entry.
                list_item = QListWidgetItem(media_record.file_name)
                list_item.setData(Qt.ItemDataRole.UserRole, media_record)
                self.addItem(list_item)
            event.acceptProposedAction()
