from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QDialog, QListWidget, QVBoxLayout, QBoxLayout, QLabel, QWidget, QHBoxLayout, QLineEdit, \
    QPushButton, QListWidgetItem

from backend.core_backend import match_titles_using_db_and_format
from backend.media_record import MediaRecord
from pages.core.drag_and_drop_files_widget import DragAndDropFilesWidget
from databases.database import Database
from databases.file_name_match_db import FileNameMatchDB
from databases.tvmaze_python_db import TVMazePythonDB


# pylint: disable=too-many-locals
class MatchOptionsWidget(QDialog):
    """
    Popup to allow users to see matched information about their files.
    Users can update any data mismatches and choose a DB to match from.
    """

    def __init__(self, files_widget: DragAndDropFilesWidget, output_box: QListWidget, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Match Options")
        self.files_widget = files_widget
        self.output_box = output_box

        layout = QVBoxLayout(self)

        # Retrieve media records from files_widget.
        self.media_records = []
        for index in range(self.files_widget.count()):
            list_element = self.files_widget.item(index)
            media_record = list_element.data(Qt.ItemDataRole.UserRole)
            self.media_records.append(media_record)

        self.is_tv_series = MediaRecord.is_tv_series(self.media_records)

        self.populate_match_options_layout(layout, self.media_records)

    def populate_match_options_layout(self, layout: QBoxLayout, media_records: list[MediaRecord]):
        """Populates the layout with UI components based on MediaRecords."""
        database_specs = self.retrieve_dictionary_of_db_buttons_with_mappings()

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
            input_box.textEdited.connect(lambda:
                                         MediaRecord.update_title_for_all_records(
                                             input_box.text(), media_records))
            input_update_container_layout.addWidget(input_box)

            database_buttons_widget = QWidget()
            database_buttons_layout = QHBoxLayout(database_buttons_widget)
            for button, supported_media_type in database_specs.items():
                if supported_media_type.count("show") == 1:
                    database_buttons_layout.addWidget(button)

            layout.addWidget(title_label)
            layout.addWidget(input_update_container)
            layout.addWidget(database_buttons_widget)

        # Contains only movies.
        elif not MediaRecord.has_episodes(media_records):
            label = QLabel(f"Got {len(media_records)} movie files!")

            database_buttons_widget = QWidget()
            database_buttons_layout = QHBoxLayout(database_buttons_widget)
            for button, supported_media_type in database_specs.items():
                if supported_media_type.count("movie") == 1:
                    database_buttons_layout.addWidget(button)

            layout.addWidget(label)
            layout.addWidget(database_buttons_widget)

    def retrieve_dictionary_of_db_buttons_with_mappings(self) -> dict[QPushButton, list[str]]:
        """Returns a dictionary of (QPushButton, Whether the database button supports movies and/or shows)"""
        the_movie_db_button = QPushButton("TheMovieDB")

        the_tv_db_button = QPushButton("TheTVDB")

        tv_maze_db_button = QPushButton("TVMaze")
        tv_maze_db_button.clicked.connect(lambda: self.match_records_and_populate_output_box(
            TVMazePythonDB(self.media_records, self.is_tv_series), self.output_box))

        file_name_match_db_button = QPushButton("Attempt to match by filename only")
        file_name_match_db_button.clicked.connect(lambda: self.match_records_and_populate_output_box(
            FileNameMatchDB(self.media_records, self.is_tv_series), self.output_box))

        result: dict[QPushButton, list[str]] = {}

        result.update({the_movie_db_button: ["movie"]})
        result.update({the_tv_db_button: ["show"]})
        result.update({tv_maze_db_button: ["show"]})
        result.update({file_name_match_db_button: ["movie", "show"]})

        return result

    def match_records_and_populate_output_box(self, database: Database, right_box: QListWidget):
        # Clear output box before populating it.
        right_box.clear()

        matched_media_titles = match_titles_using_db_and_format(database)
        for title in matched_media_titles:
            list_item = QListWidgetItem()

            # If any element (title, year, etc.) could not be found, highlight (light-red) the bad matched name.
            if "{None}" in title:
                title = title.replace("{None}", "")
                list_item.setBackground(QColor(255, 80, 80))

            list_item.setText(title)
            right_box.addItem(list_item)

        self.close()
