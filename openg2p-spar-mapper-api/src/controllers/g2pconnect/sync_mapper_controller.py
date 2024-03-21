import uuid

from openg2p_fastapi_common.controller import BaseController
from openg2p_fastapi_common.errors import BaseAppException
from openg2p_g2pconnect_common_lib.common.schemas import (
    SyncRequest,
    SyncResponse,
)
from openg2p_g2pconnect_common_lib.spar.schemas.link import (
    SingleLinkResponse,
)

from ...services_g2pconnect import RequestValidation, SyncResponseHelper, MapperService, RequestValidationException


class SyncMapperController(BaseController):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.mapper_service = MapperService.get_component()

        self.router.prefix += "/g2pconnect/mapper/sync"
        self.router.tags += ["G2PConnect Mapper Sync"]

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
        try:
            RequestValidation.validate_request(request)
            RequestValidation.validate_link_request_header(request)
        except RequestValidationException as e:
            error_response = SyncResponseHelper.get_component().construct_error_sync_response(
                request, e
            )
            return error_response

        single_link_responses: list[SingleLinkResponse] = (
            await self.mapper_service.link(request)
        )
        return SyncResponseHelper.get_component().construct_success_sync_response(
            request,
            single_link_responses,
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
