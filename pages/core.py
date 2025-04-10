from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QListWidget, QMainWindow, QHBoxLayout, QVBoxLayout, QLabel, QWidget, QPushButton, \
    QDialog, QListWidgetItem

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


class CoreRenamerWidget(QWidget):
    """Specifically contains the input box, output box, match button, rename button, and undo button."""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Contains file input/output boxes and button components (Rename, Undo, etc.).
        files_ui_layout = QHBoxLayout(self)

        # Left input box layout: Title + Box.
        left_box_layout = QVBoxLayout()
        # We want a subclass of QListWidget for drag-and-drop capabilities for the input box.
        self.left_box = DragAndDropFilesWidget()
        left_box_label = QLabel("Input Filenames")
        left_box_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_box_layout.addWidget(left_box_label)
        left_box_layout.addWidget(self.left_box)

        # Utility Buttons contained within a VBox.
        buttons_layout = QVBoxLayout()
        match_button = QPushButton("Match")
        rename_button = QPushButton("Rename")
        undo_button = QPushButton("Undo")
        buttons_layout.addWidget(match_button)
        buttons_layout.addWidget(rename_button)
        buttons_layout.addWidget(undo_button)

        # Opens a QDialog widget for user option selection when match button is clicked.
        match_button.clicked.connect(self.open_match_options_widget)

        # Right output box layout: Title + Box.
        right_box_layout = QVBoxLayout()
        right_box = QListWidget()
        right_box_label = QLabel("Output Filenames")
        right_box_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_box_layout.addWidget(right_box_label)
        right_box_layout.addWidget(right_box)

        # Combine the core renamer components and add to CoreRenamerWidget.
        files_ui_layout.addLayout(left_box_layout)
        files_ui_layout.addLayout(buttons_layout)
        files_ui_layout.addLayout(right_box_layout)

    class MatchOptionsWidget(QDialog):
        """
        Popup to allow users to see matched information about their files.
        Users can update any data mismatches and choose a DB to match from.
        """

        def __init__(self, files_widget: DragAndDropFilesWidget, parent=None):
            super().__init__(parent)

            self.setWindowTitle("Match Options")
            self.resize(400, 300)
            self.files_widget = files_widget

            layout = QVBoxLayout(self)

            # Retrieve media records from files_widget.
            media_records = []
            for index in range(self.files_widget.count()):
                list_element = self.files_widget.item(index)
                media_record = list_element.data(Qt.ItemDataRole.UserRole)
                media_records.append(media_record)

            temp_label = QLabel(f"Got {len(media_records)} files.")

            layout.addWidget(temp_label)

    @Slot()
    def open_match_options_widget(self):
        """
        Opens a MatchOptionsWidget if there are input files and passes instance of CoreRenamerWidget
        in as parent for sizing/positioning as well as the left input box (QListWidget).
        """

        if self.left_box.count() > 0:
            match_options_widget = CoreRenamerWidget.MatchOptionsWidget(self.left_box)
            match_options_widget.exec()


class CorePage(QMainWindow):
    """Main 'Rename' page for Simpler FileBot which houses the key functional components."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.renamer_widget = CoreRenamerWidget()

        # Combine all CorePage components into one QWidget().
        central_widget = QWidget()
        central_widget_layout = QVBoxLayout(central_widget)
        central_widget_layout.addWidget(self.renamer_widget)
        self.setCentralWidget(central_widget)
