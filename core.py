from PySide6.QtWidgets import QListWidget, QMainWindow, QHBoxLayout, QVBoxLayout, QLabel, QWidget, QPushButton
from PySide6.QtCore import Qt


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
                self.addItem(file_path)
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
        left_box = DragAndDropFilesWidget()
        left_box_label = QLabel("Input Filenames")
        left_box_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_box_layout.addWidget(left_box_label)
        left_box_layout.addWidget(left_box)

        # Utility Buttons contained within a VBox.
        buttons_layout = QVBoxLayout()
        match_button = QPushButton("Match")
        rename_button = QPushButton("Rename")
        undo_button = QPushButton("Undo")
        buttons_layout.addWidget(match_button)
        buttons_layout.addWidget(rename_button)
        buttons_layout.addWidget(undo_button)

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
