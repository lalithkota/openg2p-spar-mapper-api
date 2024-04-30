from openg2p_fastapi_common.controller import BaseController
from openg2p_g2pconnect_mapper_lib.schemas import (
    LinkRequest,
    LinkResponse,
    ResolveRequest,
    ResolveResponse,
    SingleLinkResponse,
    SingleResolveResponse,
    SingleUpdateResponse,
    UnlinkRequest,
    UnlinkResponse,
    UpdateRequest,
    UpdateResponse,
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

        self.router.prefix += "/sync"
        self.router.tags += ["G2PConnect Mapper Sync"]

        self.router.add_api_route(
            "/link",
            self.link_sync,
            responses={200: {"model": LinkResponse}},
            methods=["POST"],
        )
        self.router.add_api_route(
            "/update",
            self.update_sync,
            responses={200: {"model": UpdateResponse}},
            methods=["POST"],
        )
        self.router.add_api_route(
            "/resolve",
            self.resolve_sync,
            responses={200: {"model": ResolveResponse}},
            methods=["POST"],
        )
        self.router.add_api_route(
            "/unlink",
            self.unlink_sync,
            responses={200: {"model": UnlinkResponse}},
            methods=["POST"],
        )

    async def link_sync(self, link_request: LinkRequest):
        try:
            RequestValidation.get_component().validate_request(link_request)
            RequestValidation.get_component().validate_link_request_header(link_request)
        except RequestValidationException as e:
            error_response = (
                SyncResponseHelper.get_component().construct_error_sync_response(
                    link_request, e
                )
            )
            return error_response

        single_link_responses: list[
            SingleLinkResponse
        ] = await self.mapper_service.link(link_request)
        return SyncResponseHelper.get_component().construct_success_sync_link_response(
            link_request,
            single_link_responses,
        )

    async def update_sync(self, update_request: UpdateRequest):
        try:
            RequestValidation.get_component().validate_request(update_request)
            RequestValidation.get_component().validate_update_request_header(
                update_request
            )
        except RequestValidationException as e:
            error_response = (
                SyncResponseHelper.get_component().construct_error_sync_response(
                    update_request, e
                )
            )
            return error_response

        single_update_responses: list[
            SingleUpdateResponse
        ] = await self.mapper_service.update(update_request)
        return (
            SyncResponseHelper.get_component().construct_success_sync_update_response(
                update_request,
                single_update_responses,
            )
        )

    async def resolve_sync(self, resolve_request: ResolveRequest):
        try:
            RequestValidation.get_component().validate_request(resolve_request)
            RequestValidation.get_component().validate_resolve_request_header(
                resolve_request
            )
        except RequestValidationException as e:
            error_response = (
                SyncResponseHelper.get_component().construct_error_sync_response(
                    resolve_request, e
                )
            )
            return error_response

        single_resolve_responses: list[
            SingleResolveResponse
        ] = await self.mapper_service.resolve(resolve_request)
        return (
            SyncResponseHelper.get_component().construct_success_sync_resolve_response(
                resolve_request,
                single_resolve_responses,
            )
        )

    async def unlink_sync(self, unlink_request: UnlinkRequest):
        try:
            RequestValidation.get_component().validate_request(unlink_request)
            RequestValidation.get_component().validate_unlink_request_header(
                unlink_request
            )
        except RequestValidationException as e:
            error_response = (
                SyncResponseHelper.get_component().construct_error_sync_response(
                    unlink_request, e
                )
            )
            return error_response

        single_unlink_responses: list[
            SingleResolveResponse
        ] = await self.mapper_service.unlink(unlink_request)
        return (
            SyncResponseHelper.get_component().construct_success_sync_unlink_response(
                unlink_request,
                single_unlink_responses,
            )
        )
