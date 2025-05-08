from backend.media_record import MediaRecord


def test_create_movie_record_successfully():
    media_record = MediaRecord("C:/Iron Man (2008).mkv")
    assert media_record.file_name == "Iron Man (2008).mkv"
    assert media_record.full_file_path == "C:/Iron Man (2008).mkv"
    assert media_record.title == "Iron Man"
    assert media_record.media_type == "movie"
    assert media_record.year == 2008


def test_create_episode_record_successfully():
    media_record = MediaRecord("X:/Hiya/TV Shows/The.Wire.S01E01.BluRay.1080p.DD.5.1.x264-MyGroup.mkv")
    assert media_record.file_name == "The.Wire.S01E01.BluRay.1080p.DD.5.1.x264-MyGroup.mkv"
    assert media_record.full_file_path == "X:/Hiya/TV Shows/The.Wire.S01E01.BluRay.1080p.DD.5.1.x264-MyGroup.mkv"
    assert media_record.title == "The Wire"
    assert media_record.media_type == "episode"
    assert media_record.year is None


def test_create_episode_without_series_name_in_file_name_successfully():
    media_record = MediaRecord("D:/Stuff/TV Shows/The West Wing/Season 2/S02E02 - Episode Name.mkv")
    assert media_record.title == "The West Wing"


def test_no_filename_sole_metadata_is_type():
    media_record = MediaRecord("")
    assert len(media_record.metadata) == 1


def test_media_record_str_function():
    media_record = MediaRecord("C:/My Folder/Hello There.mkv")
    assert str(media_record) == "Hello There.mkv"


def test_media_record_repr_function():
    media_record = MediaRecord("C:/AAA/MyFile.mkv")
    assert repr(media_record) == "C:/AAA/MyFile.mkv"


def test_list_has_movies():
    media_records = [MediaRecord("Interstellar (2014)"), MediaRecord("Iron Man (2008)")]
    assert MediaRecord.has_movies(media_records)


def test_list_has_no_movies():
    media_records = [MediaRecord("The.West.Wing.Ep01.mkv"), MediaRecord("The.Wire.Ep05.mkv")]
    assert not MediaRecord.has_movies(media_records)


def test_list_has_episodes():
    media_records = [MediaRecord("Fairy Tail S01E05.mp4"), MediaRecord("S05E11 - Pilot Program")]
    assert MediaRecord.has_episodes(media_records)


def test_list_has_no_episodes():
    media_records = [MediaRecord("Kung Fu Panda.mkv"), MediaRecord("Thunderbolts*(2025)"), MediaRecord("")]
    assert not MediaRecord.has_episodes(media_records)


def test_get_unique_titles_from_empty_record_list_retrieve_nothing():
    media_records = [MediaRecord(".mkv"), MediaRecord("")]
    assert len(MediaRecord.get_unique_titles(media_records)) == 0


def test_get_unique_titles_from_record_list_with_one_show_retrieve_one_title():
    media_records = [MediaRecord("Andor.S01E01.mkv"), MediaRecord("Andor.S01E05.mkv")]
    assert len(MediaRecord.get_unique_titles(media_records)) == 1


def test_get_unique_titles_from_record_list_with_two_shows_retrieve_two_titles():
    media_records = [MediaRecord("The.West.Wing.S01E05.Title.mkv"), MediaRecord("Game.Of.Thrones.S02E05.mkv")]
    assert len(MediaRecord.get_unique_titles(media_records)) == 2


def test_is_tv_series_from_tv_series_list_returns_true():
    media_records = [MediaRecord("The.Punisher.S01E01.mkv"), MediaRecord("The Punisher.S01E02.mkv")]
    assert MediaRecord.is_tv_series(media_records)


def test_is_tv_series_from_movies_list_returns_false():
    media_records = [MediaRecord("Thunderbolts.mkv"), MediaRecord("Mickey 17.mkv")]
    assert not MediaRecord.is_tv_series(media_records)


def test_update_title_for_all_records_success():
    media_records = [MediaRecord("The.West.Wing.S01E01.mkv"), MediaRecord("The.West.Wing.S01E02.mkv")]

    MediaRecord.update_title_for_all_records("Some Other Name", media_records)

    for media_record in media_records:
        assert media_record.title == "Some Other Name"


def test_update_year_for_all_records_success():
    media_records = [MediaRecord("Doctor.Who.S01E01.mkv")]

    MediaRecord.update_year_for_all_records("2005", media_records)

    assert media_records[0].year == 2005


def test_get_all_season_numbers_success():
    media_records = [MediaRecord("The.West.Wing.S01E01.mkv"), MediaRecord("The.West.Wing.S03E08.mkv")]

    season_numbers = MediaRecord.get_all_season_numbers(media_records)

    assert 1 in season_numbers
    assert 3 in season_numbers


def test_season_number_missing_episode_number_still_recognized():
    media_record = MediaRecord("Chainsaw.Man.2022.S01.TrueHD.5.1/Chainsaw Man - 01 - Dog & Chainsaw.mkv")

    assert media_record.metadata["episode"] == 1
