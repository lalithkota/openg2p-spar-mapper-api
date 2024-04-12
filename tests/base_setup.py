from openg2p_spar_mapper_api.config import Settings

_config = Settings.get_config()


def base_setup():
    _config.db_dbname = "openg2p_spar_test_db"
