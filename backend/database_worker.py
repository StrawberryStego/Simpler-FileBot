import sys

from PySide6.QtCore import Signal, Slot, QRunnable, QObject

from backend.core_backend import match_titles_using_db_and_format
from databases.database import Database


# pylint: disable=broad-exception-caught
class DatabaseWorker(QObject, QRunnable):
    """Used to perform a database match in a thread... so the UI won't stall during slow database calls."""
    finished = Signal(list)
    error = Signal()

    def __init__(self, database: Database):
        QObject.__init__(self)
        QRunnable.__init__(self)
        self.database = database

    @Slot()
    def run(self):
        try:
            titles = match_titles_using_db_and_format(self.database)
            self.finished.emit(titles)
        # Broad exception is caught here as database implementations throw different exceptions.
        # This is for the general case. Ideally, we should analyze and group all types of exceptions
        # into a DatabaseError. However, this should be fine for now.
        except Exception as e:
            print(e, file=sys.stderr)
            self.error.emit()
