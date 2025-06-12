from backend.media_record import MediaRecord
from databases.database import retrieve_episode_name_from_episode_lookup


def test_lookup_returns_title_correctly():
    media_record = MediaRecord("The.West.Wing.S02E22.mkv")
    episode_lookup = {(2, 22): "Two Cathedrals"}

    assert retrieve_episode_name_from_episode_lookup(media_record, episode_lookup) == "Two Cathedrals"


def test_empty_episode_lookup_returns_none():
    media_record = MediaRecord("S01E01.mkv")
    episode_lookup = {}

    assert retrieve_episode_name_from_episode_lookup(media_record, episode_lookup) is None


def test_lookup_with_missing_media_record_season_number_defaults_to_1_successfully():
    media_record = MediaRecord("E03.mkv")
    episode_lookup = {(1, 3): "Episode 3"}

    assert retrieve_episode_name_from_episode_lookup(media_record, episode_lookup) == "Episode 3"
