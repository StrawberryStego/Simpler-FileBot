import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QListWidget, QStackedWidget
from core import CorePage


class MainWindow(QMainWindow):
    """Container for different Widgets/Pages with a menu-style list for switching between pages."""
    def __init__(self):
        super().__init__()

        # MainWindow has a QWidget as its central widget which internally uses a QHBox for Widget placement.
        central_widget = QWidget()
        central_widget_layout = QHBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        # Widget (List) that displays clickable tabs that allows for switching pages.
        self.menu = QListWidget()
        self.menu.addItems(["Rename", "Formats", "Settings"])
        central_widget_layout.addWidget(self.menu)

        # QStackedWidget stores different pages/widgets that can be switched to/from.
        # See: https://doc.qt.io/qt-6/qstackedwidget.html.
        self.pages = QStackedWidget()
        self.pages.addWidget(CorePage())
        central_widget_layout.addWidget(self.pages)

        # Connects signal for when the user clicks on a menu tab to setCurrentIndex()'s slot to change pages.
        self.menu.currentRowChanged.connect(self.pages.setCurrentIndex)
        self.menu.setCurrentRow(0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    app.exec()
