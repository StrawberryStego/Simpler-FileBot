import os.path

from PySide6.QtCore import Qt, Slot, QTimer
from PySide6.QtGui import QColor, QCursor
from PySide6.QtWidgets import QListWidget, QMainWindow, QHBoxLayout, QVBoxLayout, QLabel, QWidget, QPushButton, \
    QDialog, QLineEdit, QBoxLayout, QListWidgetItem, QApplication, QFileDialog

from backend.core_backend import (match_titles_using_db_and_format, get_invalid_file_names_and_fixes,
                                  perform_file_renaming)
from backend.drag_and_drop_files_widget import DragAndDropFilesWidget
from backend.media_record import MediaRecord
from databases.database import Database
from databases.file_name_match_db import FileNameMatchDB


class CoreRenamerWidget(QWidget):
    """Specifically contains the input box, output box, match button, rename button, and undo button."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("core")

        # Used to undo a rename function. Should be cleared on a new match or an undo operation.
        # (renamed_total_file_path: str, old_total_file_path: str)
        self.last_renames: list[tuple[str, str]] = []

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
        self.match_button = QPushButton("Match\n🗃")
        self.rename_button = QPushButton("Rename\n🖋")
        self.undo_button = QPushButton("Undo\n↩")
        buttons_layout.addWidget(self.match_button)
        buttons_layout.addWidget(self.rename_button)
        buttons_layout.addWidget(self.undo_button)

        # Disable rename and undo buttons until files are matched/renamed.
        self.rename_button.setEnabled(False)
        self.undo_button.setEnabled(False)

        # Right output box layout: Title + Box.
        right_box_layout = QVBoxLayout()
        self.right_box = QListWidget()
        right_box_label = QLabel("Output Filenames")
        right_box_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_box_layout.addWidget(right_box_label)
        right_box_layout.addWidget(self.right_box)

        # Synchronize row-selection for the left and right boxes.
        self.left_box.currentRowChanged.connect(self.right_box.setCurrentRow)
        self.right_box.currentRowChanged.connect(self.left_box.setCurrentRow)

        # Opens a QDialog widget for user option selection when match button is clicked.
        self.match_button.clicked.connect(self.open_match_options_widget)
        # Rename files once files have been matched using a database and rename button has been clicked.
        self.rename_button.clicked.connect(self.rename_files_if_allowed)
        # Undo a rename operation using cached filenames from self.last_rename on button click.
        self.undo_button.clicked.connect(self.undo_last_rename_operation)

        # Combine the core renamer components and add to CoreRenamerWidget.
        files_ui_layout.addLayout(left_box_layout)
        files_ui_layout.addLayout(buttons_layout)
        files_ui_layout.addLayout(right_box_layout)

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
                                              (QApplication.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor)),
                                               MediaRecord.update_title_for_all_records(input_box.text(),
                                                                                        media_records),
                                               QTimer.singleShot(300, QApplication.restoreOverrideCursor)))
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

        def create_database_selection_layout(self) -> QWidget:
            widget = QWidget()

            layout = QHBoxLayout(widget)

            ani_db_button = QPushButton("AniDB")
            the_tv_db_button = QPushButton("TheTVDB")
            the_movie_db_button = QPushButton("TheMovieDB")
            tv_maze_db_button = QPushButton("TVMaze")
            file_name_match_db_button = QPushButton("Attempt to match by filename only")
            file_name_match_db_button.clicked.connect(lambda: self.match_records_and_populate_output_box(
                FileNameMatchDB(self.media_records, self.is_tv_series), self.output_box))
            layout.addWidget(ani_db_button)
            layout.addWidget(the_tv_db_button)
            layout.addWidget(the_movie_db_button)
            layout.addWidget(tv_maze_db_button)
            layout.addWidget(file_name_match_db_button)

            return widget

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

    @Slot()
    def open_match_options_widget(self):
        """
        Opens a MatchOptionsWidget if there are input files and passes instance of CoreRenamerWidget
        in as parent for sizing/positioning as well as the left input box (QListWidget).
        """

        if self.left_box.count() > 0:
            match_options_widget = CoreRenamerWidget.MatchOptionsWidget(self.left_box, self.right_box)
            match_options_widget.exec()

            # Enable the rename button once files are matched.
            self.rename_button.setEnabled(True)
            # Remove any old cached last_renamed files from previous renames.
            self.last_renames.clear()

    @Slot()
    def rename_files_if_allowed(self):
        """Rename files from input box to names in output box if they're valid."""
        if not self.is_rename_allowed():
            return

        QApplication.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))

        output_file_names: list[str] = []
        for i in range(self.right_box.count()):
            output_file_names.append(self.right_box.item(i).text())

        invalid_file_names_and_fixes = get_invalid_file_names_and_fixes(output_file_names)

        if len(invalid_file_names_and_fixes) > 0:
            # Implement confirmation here.
            QApplication.restoreOverrideCursor()

        self.rename_files()
        QTimer.singleShot(1000, QApplication.restoreOverrideCursor)

        QTimer.singleShot(800, lambda: (self.left_box.clear(), self.right_box.clear()))

        # Disable the rename button and enable the undo button once files are renamed.
        self.rename_button.setEnabled(False)
        self.undo_button.setEnabled(True)

    @Slot()
    def undo_last_rename_operation(self):
        QApplication.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))

        renamed_file_names, old_file_names = map(list, zip(*self.last_renames))
        perform_file_renaming(renamed_file_names, old_file_names)
        self.last_renames.clear()

        QTimer.singleShot(1000, QApplication.restoreOverrideCursor)
        self.undo_button.setEnabled(False)

    def is_rename_allowed(self) -> bool:
        """Each record in the input box must have a matching title to rename to."""
        return self.left_box.count() == self.right_box.count()

    def rename_files(self):
        old_file_names = []
        new_file_names = []

        for i in range(self.left_box.count()):
            # Retrieve the full file path from the left box.
            full_old_file_path = self.left_box.item(i).data(Qt.ItemDataRole.UserRole).full_file_path
            old_file_names.append(full_old_file_path)

            # Retrieve the 'file name' from the right box (Does not contain the folder, just the file name).
            output_file_name = self.right_box.item(i).text()
            # Prefix the folder to the output file name.
            full_new_path = os.path.join(os.path.dirname(full_old_file_path), output_file_name)

            new_file_names.append(full_new_path)

        perform_file_renaming(old_file_names, new_file_names)

        # Store filenames for undo operation.
        if len(old_file_names) != len(new_file_names):
            print(f"Fatal renaming error. Had {len(old_file_names)} but renamed {len(new_file_names)}. ?")
            return

        self.last_renames = list(zip(new_file_names, old_file_names))


class CoreToolBar(QWidget):
    """Contains the toolbar helper elements (buttons) residing below CoreRenamerWidget."""
    BUTTON_SPACING: int = 15

    def __init__(self, input_box: DragAndDropFilesWidget, output_box: QListWidget, parent=None):
        super().__init__(parent)
        self.input_box = input_box
        self.output_box = output_box

        core_tool_bar_layout = QHBoxLayout(self)

        browse_files_button = QPushButton(" 📁 Browse Files . . .  ")
        browse_files_button.clicked.connect(self.open_files)
        remove_file_button = QPushButton(" 🚫 Remove File  ")
        remove_file_button.clicked.connect(self.remove_file)
        remove_all_files_button = QPushButton(" ❌ Remove All Files  ")
        remove_all_files_button.clicked.connect(self.remove_all_files)

        core_tool_bar_layout.addWidget(browse_files_button)
        core_tool_bar_layout.addSpacing(self.BUTTON_SPACING)
        core_tool_bar_layout.addWidget(remove_file_button)
        core_tool_bar_layout.addSpacing(self.BUTTON_SPACING)
        core_tool_bar_layout.addWidget(remove_all_files_button)
        # Adding a stretch at the end, left-aligns all buttons and sizes them correctly.
        core_tool_bar_layout.addStretch()

    @Slot()
    def open_files(self):
        file_paths, _ = QFileDialog.getOpenFileNames(None, "Select Media Files")
        for file_path in file_paths:
            self.input_box.add_file_to_list(file_path)

    @Slot()
    def remove_file(self):
        row = self.input_box.currentRow()

        if row != -1:
            removed_item = self.input_box.takeItem(row)
            del removed_item

        if row < self.output_box.count():
            removed_item = self.output_box.takeItem(row)
            del removed_item

    @Slot()
    def remove_all_files(self):
        self.input_box.clear()
        self.output_box.clear()


class CorePage(QMainWindow):
    """Main 'Rename' page for Simpler FileBot which houses the key functional components."""

    def __init__(self, parent=None):
        super().__init__(parent)
        renamer_widget = CoreRenamerWidget()
        toolbar_widget = CoreToolBar(renamer_widget.left_box, renamer_widget.right_box)

        # Combine all CorePage components into one QWidget().
        central_widget = QWidget()
        central_widget_layout = QVBoxLayout(central_widget)
        central_widget_layout.addWidget(renamer_widget)
        central_widget_layout.addWidget(toolbar_widget)
        self.setCentralWidget(central_widget)
