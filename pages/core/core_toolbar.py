from PySide6.QtCore import Slot
from PySide6.QtWidgets import QWidget, QListWidget, QHBoxLayout, QPushButton, QCheckBox, QFileDialog
from PySide6.QtGui import QShortcut, QKeySequence

from backend.settings_backend import retrieve_filename_analysis_only_flag, set_filename_analysis_only_flag
from pages.core.drag_and_drop_files_widget import DragAndDropFilesWidget


class CoreToolBar(QWidget):
    """Contains the toolbar helper elements (buttons) residing below CoreRenamerWidget."""
    BUTTON_SPACING: int = 15

    def __init__(self, input_box: DragAndDropFilesWidget, output_box: QListWidget, parent=None):
        super().__init__(parent)
        self.input_box = input_box
        self.output_box = output_box

        # Allow deleting files from the input box using the Delete key.
        self.delete_shortcut = QShortcut(QKeySequence.Delete, self.input_box)
        self.delete_shortcut.activated.connect(self.remove_file)

        core_tool_bar_layout = QHBoxLayout(self)

        browse_files_button = QPushButton(" 📁 Browse Files . . .  ")
        browse_files_button.clicked.connect(self.open_files)
        remove_file_button = QPushButton(" 🚫 Remove File  ")
        remove_file_button.clicked.connect(self.remove_file)
        remove_all_files_button = QPushButton(" ❌ Remove All Files  ")
        remove_all_files_button.clicked.connect(self.remove_all_files)

        filename_only_checkbox = QCheckBox("Use only the file's name for metadata analysis")
        filename_only_checkbox.setChecked(retrieve_filename_analysis_only_flag())
        filename_only_checkbox.toggled.connect(set_filename_analysis_only_flag)

        core_tool_bar_layout.addWidget(browse_files_button)
        core_tool_bar_layout.addSpacing(self.BUTTON_SPACING)
        core_tool_bar_layout.addWidget(remove_file_button)
        core_tool_bar_layout.addSpacing(self.BUTTON_SPACING)
        core_tool_bar_layout.addWidget(remove_all_files_button)
        core_tool_bar_layout.addSpacing(self.BUTTON_SPACING)
        core_tool_bar_layout.addWidget(filename_only_checkbox)
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
