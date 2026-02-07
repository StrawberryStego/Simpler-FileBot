import os.path

from PySide6.QtCore import Qt, Slot, QTimer
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QListWidget, QHBoxLayout, QVBoxLayout, QLabel, QWidget, QPushButton, \
    QApplication, QDialog

from backend.core_backend import (get_invalid_file_names_and_fixes,
                                  perform_file_renaming)
from backend.error_popup_widget import ErrorPopupWidget
from pages.core.drag_and_drop_files_widget import DragAndDropFilesWidget
from pages.core.match_options_widget import MatchOptionsWidget


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

        # Synchronize scrolling for the left and right boxes.
        self.left_box.verticalScrollBar().valueChanged.connect(lambda position:
                                                               self.right_box.verticalScrollBar().setValue(position))
        self.right_box.verticalScrollBar().valueChanged.connect(lambda position:
                                                                self.left_box.verticalScrollBar().setValue(position))

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

    @Slot()
    def open_match_options_widget(self):
        """
        Opens a MatchOptionsWidget if there are input files and passes instance of CoreRenamerWidget
        in as parent for sizing/positioning as well as the left input box (QListWidget).
        """
        # Nothing to match... return.
        if self.left_box.count() == 0:
            return

        # Open a MatchOptionsWidget to allow users to select a database option.
        return_code = MatchOptionsWidget(self.left_box, self.right_box).exec()

        if return_code == QDialog.DialogCode.Accepted:
            # Enable the rename button once files are matched.
            self.rename_button.setEnabled(True)
            # Remove any old cached last_renamed files from previous renames.
            self.last_renames.clear()

    @Slot()
    def rename_files_if_allowed(self):
        """Rename files from input box to names in output box if they're valid."""
        if not self.is_rename_allowed():
            self.rename_button.setEnabled(False)
            self.undo_button.setEnabled(False)
            return

        QApplication.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))

        # 1. Build complete target paths using helper method
        full_output_paths = self._get_full_output_paths()

        # 2. Path validation
        invalid_file_names_and_fixes = get_invalid_file_names_and_fixes(
            full_output_paths
        )

        if invalid_file_names_and_fixes:
            self._handle_invalid_paths(full_output_paths, invalid_file_names_and_fixes)
            QApplication.restoreOverrideCursor()
            return

        # 3. Execution of the renaming process
        self._execute_rename_cycle()

    def _get_full_output_paths(self) -> list[str]:
        """Helper to construct normalized absolute paths from the UI boxes."""
        paths = []
        for i in range(self.right_box.count()):
            old_path = self.left_box.item(i).data(Qt.ItemDataRole.UserRole).full_file_path
            new_text = os.path.expandvars(self.right_box.item(i).text())

            if ":" in new_text or new_text.startswith(("\\", "/")):
                paths.append(os.path.normpath(new_text))
            else:
                combined = os.path.join(os.path.dirname(old_path), new_text)
                paths.append(os.path.normpath(combined))
        return paths

    def _handle_invalid_paths(self, full_output_paths, fixes):
        """Updates UI with fixed names and shows error popup."""
        error_msg = "Invalid filenames or paths detected. Suggested fixes:\n\n"

        for i, current_full_path in enumerate(full_output_paths):
            fix = fixes.get(current_full_path)
            if not fix:
                continue

            # Update the UI text
            is_full_path_display = ":" in self.right_box.item(i).text()
            display_fix = fix if is_full_path_display else os.path.basename(fix)
            self.right_box.item(i).setText(display_fix)

            # Build error message
            if is_full_path_display or os.path.dirname(current_full_path) != os.path.dirname(fix):
                error_msg += f"PATH ERROR: {current_full_path}\nFIX: {fix}\n\n"
            else:
                error_msg += f"{os.path.basename(current_full_path)} → {os.path.basename(fix)}\n"

        if "PATH ERROR" in error_msg:
            error_msg += "Click Rename one more time if you agree with the new PATH\n"

        ErrorPopupWidget(error_msg).exec()

    def _execute_rename_cycle(self):
        """Final execution wrapper with cleanup."""
        success = False
        try:
            self.rename_files()
            success = True
        except (ValueError, OSError) as e:
            ErrorPopupWidget(str(e)).exec()
        finally:
            QApplication.restoreOverrideCursor()
            if success:
                self.rename_button.setEnabled(False)
                self.undo_button.setEnabled(True)
                QTimer.singleShot(800, lambda: (self.left_box.clear(), self.right_box.clear()))

    @Slot()
    def undo_last_rename_operation(self):
        QApplication.setOverrideCursor(QCursor(Qt.CursorShape.WaitCursor))

        renamed_file_names, old_file_names = map(list, zip(*self.last_renames))

        try:
            perform_file_renaming(renamed_file_names, old_file_names)
        except (ValueError, OSError):
            QApplication.restoreOverrideCursor()
            ErrorPopupWidget("Could not undo the rename operation! Perhaps files were moved?").exec()
            return
        finally:
            self.last_renames.clear()
            QTimer.singleShot(1000, QApplication.restoreOverrideCursor)
            self.undo_button.setEnabled(False)

    def is_rename_allowed(self) -> bool:
        """
        Each record in the input box must have a matching title to rename to.
        Moreover, there must actually be files to rename, i.e., input box actually has input.
        """
        return (
            self.left_box.count() == self.right_box.count()
            and self.left_box.count() > 0
        )

    def rename_files(self):
        """
        Attempts to rename or move files.
        If the pattern contains a path, it uses it. Otherwise, it renames in the original folder.
        """
        old_file_names = []
        new_file_names = []

        for i in range(self.left_box.count()):
            # Retrieve the full file path from the left box.
            full_old_file_path = self.left_box.item(i).data(Qt.ItemDataRole.UserRole).full_file_path
            old_file_names.append(full_old_file_path)

            # Text from the right box (could be "Matrix.mkv" or "C:\Kino\2024\Matrix.mkv")
            output_text = os.path.expandvars(self.right_box.item(i).text())

            # We check if it is a new path (contains a disk or starts with a slash)
            is_absolute = (
                ":" in output_text
                or output_text.startswith("\\")
                or output_text.startswith("/")
            )

            if is_absolute:
                full_new_path = output_text
            else:
                # If it's just a name, we'll link it to the original folder
                full_new_path = os.path.join(
                    os.path.dirname(full_old_file_path), output_text
                )

            new_file_names.append(full_new_path)

        # Performing the operation in the backend
        perform_file_renaming(old_file_names, new_file_names)

        # Save for Undo function
        self.last_renames = list(zip(new_file_names, old_file_names))
