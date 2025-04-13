from abc import ABC, abstractmethod

from backend.media_record import MediaRecord


class Database(ABC):
    """Abstract class to interact with a database and return data."""

    def __init__(self, media_records: list[MediaRecord], is_tv_series: bool = False):
        self.media_records = media_records
        self.is_tv_series = is_tv_series

    @abstractmethod
    def retrieve_media_titles_from_db(self) -> list:
        pass

    @abstractmethod
    def retrieve_media_years_from_db(self) -> list:
        pass
