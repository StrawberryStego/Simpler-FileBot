from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton


class ErrorPopupWidget(QDialog):
    """QDialog Widget that displays an error message for the user."""

    def __init__(self, error_msg: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Simpler FileBot Error")

        error_popup_layout = QVBoxLayout(self)

        error_msg_label = QLabel(error_msg)

        confirmation_button = QPushButton("Confirm")
        confirmation_button.clicked.connect(self.close)

        error_popup_layout.addWidget(error_msg_label)
        error_popup_layout.addWidget(confirmation_button)
