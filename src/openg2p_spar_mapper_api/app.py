# ruff: noqa: E402
import asyncio

from openg2p_fastapi_common.app import Initializer as BaseInitializer

from .config import Settings
from .controllers import (
    AsyncMapperController,
    SyncMapperController,
)
from .models import IdFaMapping
from .services import (
    AsyncRequestHelper,
    AsyncResponseHelper,
    IdFaMappingValidations,
    MapperService,
    RequestValidation,
    SyncRequestHelper,
    SyncResponseHelper,
)

_config = Settings.get_config()


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
