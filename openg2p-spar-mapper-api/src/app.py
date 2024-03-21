# ruff: noqa: E402
import asyncio

from .config import Settings

_config = Settings.get_config()

from openg2p_fastapi_common.app import Initializer as BaseInitializer
from .controllers.g2pconnect.sync_mapper_controller import SyncMapperController
from .models.orm.id_fa_mapping import IdFaMapping
from .services_g2pconnect import (
    MapperService,
    SyncRequestHelper,
    RequestValidation,
    SyncResponseHelper,
    IdFaMappingValidations,
)


class Initializer(BaseInitializer):
    def initialize(self, **kwargs):
        super().initialize()

        MapperService()
        IdFaMappingValidations()
        SyncRequestHelper()
        RequestValidation()
        SyncResponseHelper()
        SyncMapperController().post_init()

    def migrate_database(self, args):
        super().migrate_database(args)

        async def migrate():
            print("Migrating database")
            await IdFaMapping.create_migrate()

        asyncio.run(migrate())
