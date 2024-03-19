from openg2p_fastapi_common.config import Settings
from pydantic_settings import SettingsConfigDict


class Settings(Settings):
    model_config = SettingsConfigDict(env_prefix="openg2p_spar_mapper_api", env_file=".env", extra="allow")
