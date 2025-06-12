from omdb import OMDBClient

from backend.api_key_config import retrieve_omdb_key
from backend.media_record import MediaRecord
from databases.database import Database, retrieve_episode_name_from_episode_lookup


# pylint: disable=R0801
class OMDBPythonDB(Database):
    """
    Implementation of Database class to match 'movie' & 'series' MediaRecords to OMDB, using the omdb Python library.
    OMDB source: https://www.omdbapi.com/.

    This DB supports both movies and tv shows since OMDB supports both.
    """

    def __init__(self, media_records: list[MediaRecord], is_tv_series: bool = False):
        super().__init__(media_records, is_tv_series)

        # Lazy build it since the API key might not be set.
        self.omdb_client: OMDBClient | None = None

    def retrieve_media_titles_from_db(self) -> list[str | None]:
        if self.omdb_client is None:
            self.omdb_client = OMDBClient(apikey=retrieve_omdb_key())
            self.omdb_client.set_default('timeout', 5)

        matched_titles: list[str | None] = []

        if self.is_tv_series:
            # MediaRecord Episode Match.
            episode_lookup = self._create_episode_lookup(self.media_records[0].title, self.media_records[0].year,
                                                         MediaRecord.get_all_season_numbers(self.media_records),
                                                         self.media_records[0].is_absolute_order)

            for media_record in self.media_records:
                matched_titles.append(retrieve_episode_name_from_episode_lookup(media_record, episode_lookup))
        else:
            # MediaRecord Movie Match.
            for media_record in self.media_records:
                matched_movie = self.omdb_client.get(title=media_record.title, year=media_record.year)
                matched_titles.append(matched_movie.get("title"))

        return matched_titles

    def retrieve_media_years_from_db(self) -> list[int | None]:
        if self.omdb_client is None:
            self.omdb_client = OMDBClient(apikey=retrieve_omdb_key())
            self.omdb_client.set_default('timeout', 5)

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

    def _create_episode_lookup(self, title: str, year: int | None, season_numbers: set[int], is_absolute_order: bool) \
            -> dict[(int, int), str]:
        """
        Generate an episode lookup for a series.

        Return a dict: [(season_number, episode_number) -> title].
        """
        episode_lookup: dict[(int, int), str] = {}

        if is_absolute_order:
            # OMDB does not have a convenient way to retrieve the absolute order for a series.
            # We will query all episodes and create our own absolute order.
            number_of_total_seasons = int(self.omdb_client.get(title=title, year=year).get("total_seasons", 1))
            current_episode_counter = 1

            for season_number in range(1, number_of_total_seasons + 1):
                query = self.omdb_client.get(title=title, year=year, season=season_number)
                episode_info_list = query.get("episodes")

                if episode_info_list is None:
                    continue

                for episode_info in episode_info_list:
                    episode_lookup.update({(1, current_episode_counter): episode_info.get("title")})
                    current_episode_counter += 1
        else:
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
