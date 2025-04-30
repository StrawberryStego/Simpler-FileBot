from backend.json_config import JSONConfig

api_key_config = JSONConfig(
    "api_keys.json",
    {
        "the_movie_db": "",
        "the_tv_db": "",
        "omdb": ""
    }
)


def delete_and_recreate_api_keys_file() -> None:
    api_key_config.delete_and_recreate_file()


def retrieve_the_movie_db_key() -> str:
    return api_key_config.get("the_movie_db", "")


def save_new_the_movie_db_key(api_key: str) -> None:
    api_key_config.set("the_movie_db", api_key)


def retrieve_the_tv_db_key() -> str:
    return api_key_config.get("the_tv_db", "")


def save_new_the_tv_db_key(api_key: str) -> None:
    api_key_config.set("the_tv_db", api_key)


def retrieve_omdb_key() -> str:
    return api_key_config.get("omdb", "")


def save_new_omdb_key(api_key: str) -> None:
    api_key_config.set("omdb", api_key)
