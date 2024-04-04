from typing import Optional

from openg2p_fastapi_common.config import Settings as BaseSettings
from pydantic import AnyUrl
from pydantic_settings import SettingsConfigDict

from . import __version__


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="spar_mapper_", env_file=".env", extra="allow"
    )

    openapi_title: str = "OpenG2P SPAR Account Mapper"
    openapi_description: str = """
    This module maps the beneficiary ID to a Financial Address.

    ***********************************
    Further details goes here
    ***********************************
    """
    openapi_version: str = __version__

    db_dbname: str = "openg2p_spar_db"

    default_callback_url: Optional[AnyUrl] = None
    default_callback_timeout: int = 10
    callback_sender_id: str = "mapper.dev.openg2p.net"
