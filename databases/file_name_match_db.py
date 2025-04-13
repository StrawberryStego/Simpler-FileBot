from backend.media_record import MediaRecord
from databases.database import Database


class FileNameMatchDB(Database):
    """
    Implementation of Database class to match MediaRecords using their file names only, effectively
    relying on MediaRecord's 'guessit' library for parsing. Can be volatile as guessit is prone to mistakes.
    """

    def __init__(self, media_records: list[MediaRecord], is_tv_series: bool = False):
        super().__init__(media_records, is_tv_series)

    def retrieve_media_titles_from_db(self) -> list:
        media_titles = []

        for media_record in self.media_records:
            if self.is_tv_series:
                media_titles.append(media_record.metadata.get("episode_title"))

            if not self.is_tv_series:
                media_titles.append(media_record.title)

        return media_titles

    def retrieve_media_years_from_db(self) -> list:
        media_years = []

        for media_record in self.media_records:
            media_years.append(media_record.year)

        return media_years
