from PySide6.QtCore import Slot
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QHBoxLayout

from backend.api_key_config import api_key_config


class ApiKeyPromptWidget(QDialog):
    """Prompt to ask user to input their API key for a specific json_key/database entry (api_keys.json)."""

    def __init__(self, json_key: str, message: str, parent=None):
        super().__init__(parent)
        self.json_key = json_key
        self.setWindowTitle(f"Set API key for {json_key}")

        prompt_layout = QVBoxLayout(self)

        self.edit = QLineEdit()
        self.edit.setPlaceholderText("[API Key]")

        button_layout = QHBoxLayout()

        cancel_button = QPushButton("Cancel")
        cancel_button.setObjectName("cancel_button")
        cancel_button.clicked.connect(self.reject)

        save_button = QPushButton("Save")
        save_button.setObjectName("save_button")
        save_button.clicked.connect(self.save_api_key_and_close)

        button_layout.addWidget(cancel_button)
        button_layout.addWidget(save_button)

        prompt_layout.addWidget(QLabel(message))
        prompt_layout.addWidget(QLabel(f"Enter the API key for {json_key}:"))
        prompt_layout.addWidget(self.edit)
        prompt_layout.addLayout(button_layout)

    @Slot()
    def save_api_key_and_close(self) -> None:
        input_key = self.edit.text().strip()

        if input_key != "":
            api_key_config.set(self.json_key, input_key)
            self.accept()
