from PySide6.QtCore import Signal, Slot, QRunnable, QObject

from backend.core_backend import match_titles_using_db_and_format
from databases.database import Database


class DatabaseWorker(QObject, QRunnable):
    """Used to perform a database match in a thread... so the UI won't stall during slow database calls."""
    finished = Signal(list)

    def __init__(self, database: Database):
        QObject.__init__(self)
        QRunnable.__init__(self)
        self.database = database

    @Slot()
    def run(self):
        titles = match_titles_using_db_and_format(self.database)
        self.finished.emit(titles)
