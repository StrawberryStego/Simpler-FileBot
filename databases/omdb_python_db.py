from omdb import OMDBClient

from backend.api_key_config import retrieve_omdb_key
from backend.media_record import MediaRecord
from databases.database import Database


# pylint: disable=R0801
class OMDBPythonDB(Database):
    """
    Implementation of Database class to match 'movie' & 'series' MediaRecords to OMDB, using the omdb Python library.
    OMDB source: https://www.omdbapi.com/.

    This DB supports both movies and tv shows since OMDB supports both.
    """

    def __init__(self, media_records: list[MediaRecord], is_tv_series: bool = False):
        super().__init__(media_records, is_tv_series)

        omdb_api_key = retrieve_omdb_key()
        self.omdb_client = OMDBClient(apikey=omdb_api_key)
        # Timeout requests after 5 seconds.
        self.omdb_client.set_default('timeout', 5)

    def retrieve_media_titles_from_db(self) -> list[str | None]:
        matched_titles: list[str | None] = []

        if self.is_tv_series:
            # MediaRecord Episode Match.
            episode_lookup = self._create_episode_lookup(self.media_records[0].title, self.media_records[0].year,
                                                         MediaRecord.get_all_season_numbers(self.media_records))

            for media_record in self.media_records:
                # Default to season 1 if there is no season attribute for the MediaRecord.
                media_record_season_number: int = media_record.metadata.get("season", 1)
                media_record_episode_values = media_record.metadata.get("episode", -1)

                # media_record_episode_values could contain multiple episode numbers. Pick the 1st one.
                media_record_episode_number = media_record_episode_values[0] \
                    if isinstance(media_record_episode_values, list) else media_record_episode_values

                match = episode_lookup.get((media_record_season_number, media_record_episode_number))
                matched_titles.append(match if match else None)
        else:
            # MediaRecord Movie Match.
            for media_record in self.media_records:
                matched_movie = self.omdb_client.get(title=media_record.title, year=media_record.year)
                matched_titles.append(matched_movie.get("title"))

        return matched_titles

    def retrieve_media_years_from_db(self) -> list[int | None]:
        if self.is_tv_series:
            # Simply return the year if it already exists for a series.
            if self.media_records[0].year is not None:
                return [self.media_records[0].year] * len(self.media_records)

            series_info = self.omdb_client.get(title=self.media_records[0].title)

            year_range = series_info.get("year")

            if year_range is not None:
                year = int(year_range[:4])
                return [year] * len(self.media_records)

            return [None] * len(self.media_records)

        # Return the 'movie' release year of each MediaRecord.
        release_years: list[int | None] = []

        for media_record in self.media_records:
            # Just use the year attached to the MediaRecord if it exists.
            if media_record.year is not None:
                release_years.append(media_record.year)
                continue

            movie_info = self.omdb_client.get(title=media_record.title)
            release_years.append(movie_info.get("year"))

        return release_years

    def _create_episode_lookup(self, title: str, year: int | None, season_numbers: set[int]) -> dict[(int, int), str]:
        """
        Generate an episode lookup for a series.

        Return a dict: [(season_number, episode_number) -> title].
        """
        episode_lookup: dict[(int, int), str] = {}

        # OMDB requires you to look up episodes one season at a time.
        for season_number in season_numbers:
            query = self.omdb_client.get(title=title, year=year, season=season_number)
            episode_info_list = query.get("episodes")

            if episode_info_list is None:
                continue

            for episode_info in episode_info_list:
                episode_lookup.update({
                    (season_number, int(episode_info.get("episode", -1))): episode_info.get("title")
                })

        return episode_lookup
