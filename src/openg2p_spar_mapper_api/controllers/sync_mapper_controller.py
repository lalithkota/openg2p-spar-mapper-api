from openg2p_fastapi_common.controller import BaseController
from openg2p_g2pconnect_common_lib.common.schemas import (
    Request,
    SyncResponse,
)
from openg2p_g2pconnect_common_lib.mapper.schemas.link import (
    SingleLinkResponse,
)
from openg2p_g2pconnect_common_lib.mapper.schemas.resolve import (
    SingleResolveResponse,
)
from openg2p_g2pconnect_common_lib.mapper.schemas.update import (
    SingleUpdateResponse,
)

from ..services import (
    MapperService,
    RequestValidation,
    RequestValidationException,
    SyncResponseHelper,
)


class SyncMapperController(BaseController):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.mapper_service = MapperService.get_component()

        self.router.prefix += "/mapper/sync"
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
            responses={200: {"model": SyncResponse}},
            methods=["POST"],
        )

    async def link_sync(self, request: Request):
        try:
            RequestValidation.validate_request(request)
            RequestValidation.validate_link_request_header(request)
        except RequestValidationException as e:
            error_response = (
                SyncResponseHelper.get_component().construct_error_sync_response(
                    request, e
                )
            )
            return error_response

        single_link_responses: list[
            SingleLinkResponse
        ] = await self.mapper_service.link(request)
        return SyncResponseHelper.get_component().construct_success_sync_link_response(
            request,
            single_link_responses,
        )

    async def update_sync(self, request: Request):
        try:
            RequestValidation.validate_request(request)
            RequestValidation.validate_update_request_header(request)
        except RequestValidationException as e:
            error_response = (
                SyncResponseHelper.get_component().construct_error_sync_response(
                    request, e
                )
            )
            return error_response

        single_update_responses: list[
            SingleUpdateResponse
        ] = await self.mapper_service.update(request)
        return (
            SyncResponseHelper.get_component().construct_success_sync_update_response(
                request,
                single_update_responses,
            )
        )

    async def resolve_sync(self, request: Request):
        try:
            RequestValidation.validate_request(request)
            RequestValidation.validate_resolve_request_header(request)
        except RequestValidationException as e:
            error_response = (
                SyncResponseHelper.get_component().construct_error_sync_response(
                    request, e
                )
            )
            return error_response

        single_resolve_responses: list[
            SingleResolveResponse
        ] = await self.mapper_service.resolve(request)
        return (
            SyncResponseHelper.get_component().construct_success_sync_resolve_response(
                request,
                single_resolve_responses,
            )
        )

    async def unlink_sync(self, request: Request):
        try:
            RequestValidation.validate_request(request)
            RequestValidation.validate_unlink_request_header(request)
        except RequestValidationException as e:
            error_response = (
                SyncResponseHelper.get_component().construct_error_sync_response(
                    request, e
                )
            )
            return error_response

        single_unlink_responses: list[
            SingleResolveResponse
        ] = await self.mapper_service.unlink(request)
        return (
            SyncResponseHelper.get_component().construct_success_sync_unlink_response(
                request,
                single_unlink_responses,
            )
        )
