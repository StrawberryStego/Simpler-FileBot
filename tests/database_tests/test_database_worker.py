from PySide6.QtCore import QThreadPool
from _pytest.monkeypatch import MonkeyPatch
from pytestqt.qtbot import QtBot

from backend.database_worker import DatabaseWorker
from databases.database import Database


# pylint: disable=missing-class-docstring
class MockDatabase(Database):
    def retrieve_media_titles_from_db(self) -> list[str | None]:
        pass

    def retrieve_media_years_from_db(self) -> list[int | None]:
        pass


def test_finished_signal_emits_successfully(qtbot: QtBot, monkeypatch: MonkeyPatch):
    monkeypatch.setattr("backend.database_worker.match_titles_using_db_and_format",
                        lambda db: ["Iron Man (2008).mkv", "Doctor Strange (2016).mkv"])

    database_worker = DatabaseWorker(MockDatabase([]))
    with qtbot.waitSignal(database_worker.finished) as payload:
        QThreadPool.globalInstance().start(database_worker)

    assert payload.args == [["Iron Man (2008).mkv", "Doctor Strange (2016).mkv"]]


def test_error_signal_emits_on_exception(qtbot: QtBot, monkeypatch: MonkeyPatch):
    def _boom(_):
        raise RuntimeError("")
    monkeypatch.setattr("backend.database_worker.match_titles_using_db_and_format",
                        _boom)
    database_worker = DatabaseWorker(MockDatabase([]))

    # Verify that the finished signal is not emitted.
    with qtbot.assertNotEmitted(database_worker.finished):
        # Verify that the error signal is emitted.
        with qtbot.waitSignal(database_worker.error):
            QThreadPool.globalInstance().start(database_worker)
