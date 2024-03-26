# ruff: noqa: E402
import asyncio

from .config import Settings

_config = Settings.get_config()

from openg2p_fastapi_common.app import Initializer as BaseInitializer
from .controllers.g2pconnect import (
    SyncMapperController,
    AsyncMapperController,
)

from .models import IdFaMapping
from .services import (
    MapperService,
    SyncRequestHelper,
    RequestValidation,
    SyncResponseHelper,
    IdFaMappingValidations,
    AsyncRequestHelper,
    AsyncResponseHelper,
)


class Initializer(BaseInitializer):
    def initialize(self, **kwargs):
        super().initialize()

        MapperService()
        IdFaMappingValidations()
        SyncRequestHelper()
        AsyncRequestHelper()
        RequestValidation()
        SyncResponseHelper()
        AsyncResponseHelper()
        SyncMapperController().post_init()
        AsyncMapperController().post_init()

    def migrate_database(self, args):
        super().migrate_database(args)

        async def migrate():
            print("Migrating database")
            await IdFaMapping.create_migrate()

        asyncio.run(migrate())
