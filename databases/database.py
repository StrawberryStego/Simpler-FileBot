from abc import ABC, abstractmethod

from backend.media_record import MediaRecord


class Database(ABC):
    """Abstract class to interact with a database and return data."""

    def __init__(self, media_records: list[MediaRecord], is_tv_series: bool = False):
        self.media_records = media_records
        self.is_tv_series = is_tv_series

    @abstractmethod
    def retrieve_media_titles_from_db(self) -> list[str | None]:
        """
        Retrieves a list of movie titles or episode titles from the database, depending on whether
        self.media_records is a list of movies or episodes. Each matched title corresponds to
        the record at the same index. If a title is missing, the value is None.

        :return: A list where each element is a database-matched title or None if not available.
        :rtype: list[str | None]
        """

    @abstractmethod
    def retrieve_media_years_from_db(self) -> list[int | None]:
        """
        Retrieves a list of media release years corresponding to self.media_records.
        Each element in the returned list aligns with the record at the same index in self.media_records.
        The list may contain an integer representing the release year or None if the year is unavailable.

        :return: A list where each element is an integer year or None if not available.
        :rtype: list[int | None]
        """
