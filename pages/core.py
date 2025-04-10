from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QListWidget, QMainWindow, QHBoxLayout, QVBoxLayout, QLabel, QWidget, QPushButton, \
    QDialog, QListWidgetItem, QLineEdit, QBoxLayout

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
        self.right_box = QListWidget()
        right_box_label = QLabel("Output Filenames")
        right_box_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_box_layout.addWidget(right_box_label)
        right_box_layout.addWidget(self.right_box)

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
            self.files_widget = files_widget

            layout = QVBoxLayout(self)

            # Retrieve media records from files_widget.
            media_records = []
            for index in range(self.files_widget.count()):
                list_element = self.files_widget.item(index)
                media_record = list_element.data(Qt.ItemDataRole.UserRole)
                media_records.append(media_record)

            self.populate_layout(layout, media_records)

        def populate_layout(self, layout: QBoxLayout, media_records: list):
            """Populates the layout with UI components based on MediaRecords."""

            # Contains a mix of movies and shows.
            if MediaRecord.has_movies(media_records) and MediaRecord.has_episodes(media_records):
                error_label = QLabel("Cannot rename both movies and tv series at the same time!")
                layout.addWidget(error_label)

            # Contains only episodes but there seems to be multiple tv shows.
            elif not MediaRecord.has_movies(media_records) and len(MediaRecord.get_unique_titles(media_records)) > 1:
                error_label = QLabel("Cannot rename multiple tv series at the same time!")
                layout.addWidget(error_label)

            # Contains only episodes.
            elif not MediaRecord.has_movies(media_records) and len(MediaRecord.get_unique_titles(media_records)) <= 1:
                unique_titles = MediaRecord.get_unique_titles(media_records)
                series_title = unique_titles.pop() if unique_titles else "Could not match title!"

                # Add UI and logic to set a custom series name in case guessit retrieved an incorrect show name.
                title_label = QLabel("Series Title:")
                input_update_container = QWidget()
                input_update_container_layout = QHBoxLayout(input_update_container)
                input_box = QLineEdit()
                input_box.setText(series_title)
                update_button = QPushButton("Update")
                update_button.clicked.connect(lambda:
                                              MediaRecord.update_title_for_all_records(input_box.text(), media_records))
                input_update_container_layout.addWidget(input_box)
                input_update_container_layout.addWidget(update_button)

                database_buttons_widget = self.create_database_selection_layout()

                layout.addWidget(title_label)
                layout.addWidget(input_update_container)
                layout.addWidget(database_buttons_widget)

            # Contains only movies.
            elif not MediaRecord.has_episodes(media_records):
                label = QLabel(f"Got {len(media_records)} movie files!")

                database_buttons_widget = self.create_database_selection_layout()

                layout.addWidget(label)
                layout.addWidget(database_buttons_widget)

        @staticmethod
        def create_database_selection_layout() -> QWidget:
            widget = QWidget()

            layout = QHBoxLayout(widget)

            ani_db_button = QPushButton("AniDB")
            the_tv_db_button = QPushButton("TheTVDB")
            the_movie_db_button = QPushButton("TheMovieDB")
            tv_maze_db_button = QPushButton("TVMaze")
            guessit_button = QPushButton("Attempt to match by filename only")
            layout.addWidget(ani_db_button)
            layout.addWidget(the_tv_db_button)
            layout.addWidget(the_movie_db_button)
            layout.addWidget(tv_maze_db_button)
            layout.addWidget(guessit_button)

            return widget

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
