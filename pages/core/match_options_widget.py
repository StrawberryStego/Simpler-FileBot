from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QColor, QIcon, QPixmap
from PySide6.QtWidgets import QDialog, QListWidget, QVBoxLayout, QBoxLayout, QLabel, QWidget, QHBoxLayout, QLineEdit, \
    QPushButton, QListWidgetItem

from backend.api_key_config import api_key_config
from backend.core_backend import match_titles_using_db_and_format
from backend.media_record import MediaRecord
from databases.database import Database
from databases.file_name_match_db import FileNameMatchDB
from databases.omdb_python_db import OMDBPythonDB
from databases.themoviedb_python_db import TheMovieDBPythonDB
from databases.tvmaze_python_db import TVMazePythonDB
from pages.core.api_key_prompt_widget import ApiKeyPromptWidget
from pages.core.drag_and_drop_files_widget import DragAndDropFilesWidget


# pylint: disable=too-many-locals
class MatchOptionsWidget(QDialog):
    """
    Popup to allow users to choose a movie or series database to match to.
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
            title_update_container = QWidget()
            title_update_container_layout = QHBoxLayout(title_update_container)
            title_input_box = QLineEdit()
            title_input_box.setText(series_title)
            title_input_box.textEdited.connect(lambda:
                                               MediaRecord.update_title_for_all_records(
                                                   title_input_box.text(), media_records))
            title_update_container_layout.addWidget(title_input_box)

            # Add UI and logic to set a custom year for a series.
            year_label = QLabel("Year:")
            year_update_container = QWidget()
            year_update_container_layout = QHBoxLayout(year_update_container)
            year_input_box = QLineEdit()
            year_input_box.setPlaceholderText("[auto]")
            if media_records[0].year is not None:
                year_input_box.setText(str(media_records[0].year))
            year_input_box.textEdited.connect(lambda:
                                              MediaRecord.update_year_for_all_records(
                                                  year_input_box.text(), media_records))
            year_update_container_layout.addWidget(year_input_box)

            database_buttons_widget = QWidget()
            database_buttons_layout = QHBoxLayout(database_buttons_widget)
            for button, supported_media_type in database_specs.items():
                if supported_media_type.count("show") == 1:
                    database_buttons_layout.addWidget(button)

            layout.addWidget(title_label)
            layout.addWidget(title_update_container)
            layout.addWidget(year_label)
            layout.addWidget(year_update_container)
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
        the_movie_db_button = QPushButton(" TheMovieDB ")
        the_movie_db_button.clicked.connect(lambda: self.match_with_database_that_requires_api_key(
            TheMovieDBPythonDB(self.media_records, self.is_tv_series), "the_movie_db"
        ))
        the_movie_db_button.setIcon(QIcon(QPixmap("resources/TheMovieDB Logo.svg")))
        the_movie_db_button.setObjectName("dbBtn")

        omdb_db_button = QPushButton(" OMDB ")
        omdb_db_button.clicked.connect(lambda: self.match_with_database_that_requires_api_key(
            OMDBPythonDB(self.media_records, self.is_tv_series), "omdb"
        ))
        omdb_db_button.setIcon(QIcon(QPixmap("resources/OMDB Logo.png")))
        omdb_db_button.setObjectName("dbBtn")

        tv_maze_db_button = QPushButton(" TVMaze ")
        tv_maze_db_button.clicked.connect(lambda: self.match_records_and_populate_output_box(
            TVMazePythonDB(self.media_records, self.is_tv_series), self.output_box))
        tv_maze_db_button.setIcon(QIcon(QPixmap("resources/TVMaze Logo.png")))
        tv_maze_db_button.setObjectName("dbBtn")

        file_name_match_db_button = QPushButton(" Attempt to match by filename only ")
        file_name_match_db_button.clicked.connect(lambda: self.match_records_and_populate_output_box(
            FileNameMatchDB(self.media_records, self.is_tv_series), self.output_box))

        result: dict[QPushButton, list[str]] = {}

        result.update({the_movie_db_button: ["movie", "show"]})
        result.update({omdb_db_button: ["movie", "show"]})
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

        self.accept()

    @Slot()
    def match_with_database_that_requires_api_key(self, database: Database, json_key: str) -> None:
        response = check_if_api_key_exists_otherwise_prompt_user(json_key)

        if response:
            self.match_records_and_populate_output_box(database, self.output_box)


def check_if_api_key_exists_otherwise_prompt_user(json_key: str) -> bool:
    """Check if a value for 'json_key' exists in api_keys.json. Prompt the user to enter an api_key if missing."""
    if api_key_config.get(json_key) == "":
        response = ApiKeyPromptWidget(json_key, "")
        if response.exec() == QDialog.DialogCode.Accepted:
            return True

    if api_key_config.get(json_key) is not None:
        return True

    return False
