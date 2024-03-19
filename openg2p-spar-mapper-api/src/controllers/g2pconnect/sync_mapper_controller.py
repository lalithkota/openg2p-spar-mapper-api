import uuid

from openg2p_g2pconnect_common_lib.schemas import SyncRequest, SyncResponse
from openg2p_fastapi_common.controller import BaseController
from openg2p_fastapi_common.errors import BaseAppException

from ..services.mapper_service import MapperService


class SyncMapperController(BaseController):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.mapper_service = MapperService.get_component()

        self.router.prefix += "/mapper/sync"
        self.router.tags += ["mapper-sync"]

        self.router.add_api_route(
            "/link",
            self.link_sync,
            responses={200: {"model": SyncResponse}},
            methods=["POST"],
        )
        self.router.add_api_route(
            "/update",
            self.update_sync,
            responses={200: {"model": SyncResponse}},
            methods=["POST"],
        )
        self.router.add_api_route(
            "/resolve",
            self.resolve_sync,
            responses={200: {"model": SyncResponse}},
            methods=["POST"],
        )
        self.router.add_api_route(
            "/unlink",
            self.unlink_sync,
            # TODO
            responses={200: {"model": SyncResponse}},
            methods=["POST"],
        )

    async def link_sync(self, request: SyncRequest):
        if request.header.action != "link":
            raise BaseAppException(
                code="MPR-REQ-400",
                message="Received Invalid action in header for 'link'.",
                http_status_code=400,
            )

        # TODO: For now returning random correlation id.
        correlation_id = str(uuid.uuid4())
        # TODO: For now creating async task and forgetting

        return await self.mapper_service.link(
            correlation_id, request, make_callback=False
        )

    async def update_sync(self, request: SyncRequest):
        if request.header.action != "update":
            raise BaseAppException(
                code="MPR-REQ-400",
                message="Received Invalid action in header for 'update'.",
                http_status_code=400,
            )
        # TODO: For now returning random correlation id.
        correlation_id = str(uuid.uuid4())
        # TODO: For now creating async task and forgetting
        return await self.mapper_service.update(
            correlation_id, request, make_callback=False
        )

    async def resolve_sync(self, request: SyncRequest):
        if request.header.action != "resolve":
            raise BaseAppException(
                code="MPR-REQ-400",
                message="Received Invalid action in header for 'resolve'.",
                http_status_code=400,
            )
        # TODO: For now returning random correlation id.
        correlation_id = str(uuid.uuid4())
        # TODO: For now creating async task and forgetting
        return await self.mapper_service.resolve(
            correlation_id, request, make_callback=False
        )

    async def unlink_sync(self):
        raise NotImplementedError()
