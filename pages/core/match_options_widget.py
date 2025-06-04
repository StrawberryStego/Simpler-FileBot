from PySide6.QtCore import Qt, Slot, QThreadPool
from PySide6.QtGui import QColor, QIcon, QPixmap, QCursor
from PySide6.QtWidgets import QDialog, QListWidget, QVBoxLayout, QBoxLayout, QLabel, QWidget, QHBoxLayout, QLineEdit, \
    QPushButton, QListWidgetItem, QApplication

from backend.api_key_config import api_key_config
from backend.database_worker import DatabaseWorker
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
    Handles database matching and populating the output box with matched file names.
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

        # Used to disable closing this window when database calls are happening.
        self._busy = False

    def closeEvent(self, event):
        """
        Disallow closing the MatchOptionsWidget with the X button, Alt-F4, or the window manager
        if the application is busy doing a database query.
        """
        if self._busy:
            event.ignore()
        else:
            super().closeEvent(event)

    def reject(self):
        """
        Disallow closing the MatchOptionsWidget with the escape key or programmatically
        if the application is busy doing a database query.
        """
        if not self._busy:
            super().reject()

    def populate_match_options_layout(self, layout: QBoxLayout, media_records: list[MediaRecord]):
        """Populates the layout with UI components based on MediaRecords."""
        # Display an error if the input contains a mix of movie and TV show files.
        if MediaRecord.has_movies(media_records) and MediaRecord.has_episodes(media_records):
            layout.addWidget(QLabel("Cannot rename both movies and tv series at the same time!"))
            return

        # Display an error if there are multiple TV series for an input list of episodes.
        if not MediaRecord.has_movies(media_records) and len(MediaRecord.get_unique_titles(media_records)) > 1:
            layout.addWidget(QLabel("Cannot rename multiple tv series at the same time!"))
            return

        # Contains only episodes.
        if not MediaRecord.has_movies(media_records):
            layout.addLayout(self.create_layout_for_episode_matching(media_records))
        # Contains only movies.
        elif not MediaRecord.has_episodes(media_records):
            layout.addLayout(self.create_layout_for_movie_matching(media_records))

    def create_layout_for_episode_matching(self, media_records: list[MediaRecord]) -> QVBoxLayout:
        # Mapping of database buttons to the type of media they support.
        database_specs = self.retrieve_dictionary_of_db_buttons_with_mappings()

        episode_matching_layout = QVBoxLayout()

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
            if "show" in supported_media_type:
                database_buttons_layout.addWidget(button)

        episode_matching_layout.addWidget(title_label)
        episode_matching_layout.addWidget(title_update_container)
        episode_matching_layout.addWidget(year_label)
        episode_matching_layout.addWidget(year_update_container)
        episode_matching_layout.addWidget(database_buttons_widget)

        return episode_matching_layout

    def create_layout_for_movie_matching(self, media_records: list[MediaRecord]) -> QVBoxLayout:
        # Mapping of database buttons to the type of media they support.
        database_specs = self.retrieve_dictionary_of_db_buttons_with_mappings()

        movie_matching_layout = QVBoxLayout()

        label = QLabel(f"Got {len(media_records)} movie files!")

        database_buttons_widget = QWidget()
        database_buttons_layout = QHBoxLayout(database_buttons_widget)
        for button, supported_media_type in database_specs.items():
            if "movie" in supported_media_type:
                database_buttons_layout.addWidget(button)

        movie_matching_layout.addWidget(label)
        movie_matching_layout.addWidget(database_buttons_widget)

        return movie_matching_layout

    def retrieve_dictionary_of_db_buttons_with_mappings(self) -> dict[QPushButton, list[str]]:
        """Returns a dictionary of (QPushButton, Whether the database button supports movies and/or shows)"""
        the_movie_db_button = QPushButton(" TheMovieDB ")
        the_movie_db_button.clicked.connect(lambda: self.start_match(
            TheMovieDBPythonDB(self.media_records, self.is_tv_series), "the_movie_db"
        ))
        the_movie_db_button.setIcon(QIcon(QPixmap("resources/TheMovieDB Logo.svg")))
        the_movie_db_button.setObjectName("dbBtn")

        omdb_db_button = QPushButton(" OMDB ")
        omdb_db_button.clicked.connect(lambda: self.start_match(
            OMDBPythonDB(self.media_records, self.is_tv_series), "omdb"
        ))
        omdb_db_button.setIcon(QIcon(QPixmap("resources/OMDB Logo.png")))
        omdb_db_button.setObjectName("dbBtn")

        tv_maze_db_button = QPushButton(" TVMaze ")
        tv_maze_db_button.clicked.connect(lambda: self.start_match(
            TVMazePythonDB(self.media_records, self.is_tv_series)))
        tv_maze_db_button.setIcon(QIcon(QPixmap("resources/TVMaze Logo.png")))
        tv_maze_db_button.setObjectName("dbBtn")

        file_name_match_db_button = QPushButton(" Attempt to match by filename only ")
        file_name_match_db_button.clicked.connect(lambda: self.start_match(
            FileNameMatchDB(self.media_records, self.is_tv_series)))

        result: dict[QPushButton, list[str]] = {}

        result.update({the_movie_db_button: ["movie", "show"]})
        result.update({omdb_db_button: ["movie", "show"]})
        result.update({tv_maze_db_button: ["show"]})
        result.update({file_name_match_db_button: ["movie", "show"]})

        return result

    def start_match(self, database: Database, json_key: str = None):
        """
        Starts a non-blocking database query to match our MediaRecords.

        :param Database database: Database class implementation.
        :param str json_key: (Optional) Name of the database key (See api_key_config.py).
        """
        # If a json_key is not none, that means that the database requires an API key. We should handle that.
        if json_key is not None:
            response = check_if_api_key_exists_otherwise_prompt_user(json_key)

            # Return if the API key prompt was not completed.
            if not response:
                return

        # Block UI clicks while the database call is running.
        self.setEnabled(False)
        # Change the cursor to a waiting cursor and restore it when the output box receives the matched titles.
        QApplication.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))

        # Clear output box before populating it.
        self.output_box.clear()

        # Start the database matching.
        database_worker = DatabaseWorker(database)
        database_worker.finished.connect(self.populate_output_box)
        database_worker.error.connect(self.handle_database_query_error)
        self._busy = True
        QThreadPool.globalInstance().start(database_worker)

    @Slot(list)
    def populate_output_box(self, matched_media_titles: list[str]):
        for title in matched_media_titles:
            list_item = QListWidgetItem()

            # If any element (title, year, etc.) could not be found, highlight (light-red) the bad matched name.
            if "{None}" in title:
                title = title.replace("{None}", "")
                list_item.setBackground(QColor(255, 80, 80))

            list_item.setText(title)
            self.output_box.addItem(list_item)

        # Return the UI state to normal and close the MatchOptionsWidget window with an accept code.
        self.setEnabled(True)
        QApplication.restoreOverrideCursor()
        self._busy = False
        self.accept()

    @Slot()
    def handle_database_query_error(self):
        # Return the UI state to normal and close the MatchOptionsWidget window.
        self.setEnabled(True)
        QApplication.restoreOverrideCursor()
        self._busy = False
        self.close()


def check_if_api_key_exists_otherwise_prompt_user(json_key: str) -> bool:
    """Check if a value for 'json_key' exists in api_keys.json. Prompt the user to enter an api_key if missing."""
    if api_key_config.get(json_key) == "":
        response = ApiKeyPromptWidget(json_key, "").exec()
        if response == QDialog.DialogCode.Accepted:
            return True
    elif api_key_config.get(json_key) is not None:
        # Return true if the key is not blank.
        return True

    return False
