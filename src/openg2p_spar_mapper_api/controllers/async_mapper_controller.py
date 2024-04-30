import asyncio
import logging
import uuid

import httpx
from openg2p_fastapi_common.controller import BaseController
from openg2p_g2pconnect_common_lib.schemas import (
    AsyncCallbackRequest,
    AsyncResponse,
    Request,
)
from openg2p_g2pconnect_mapper_lib.schemas import (
    LinkRequest,
    ResolveRequest,
    SingleLinkResponse,
    SingleResolveResponse,
    SingleUnlinkResponse,
    SingleUpdateResponse,
    UnlinkRequest,
    UpdateRequest,
)

from ..config import Settings
from ..services import (
    AsyncResponseHelper,
    MapperService,
    RequestValidation,
    RequestValidationException,
)

_config = Settings.get_config()
_logger = logging.getLogger(_config.logging_default_logger_name)


async def _callback(
    async_call_back_request: AsyncCallbackRequest, url, url_suffix=None
):
    try:
        res = httpx.post(
            f"{url.rstrip('/')}{url_suffix}",
            headers={"content-type": "application/json"},
            content=async_call_back_request.model_dump_json(),
            timeout=_config.default_callback_timeout,
        )

        res.raise_for_status()
    except Exception as e:
        _logger.error(f"Error during callback: {e}")


class AsyncMapperController(BaseController):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.mapper_service = MapperService.get_component()

        self.router.prefix += "/async"
        self.router.tags += ["G2PConnect Mapper Async"]

        self.action_to_method = {
            "link": self.mapper_service.link,
            "update": self.mapper_service.update,
            "resolve": self.mapper_service.resolve,
            "unlink": self.mapper_service.unlink,
        }

        self.router.add_api_route(
            "/link",
            self.link_async,
            responses={200: {"model": AsyncResponse}},
            methods=["POST"],
        )
        self.router.add_api_route(
            "/update",
            self.update_async,
            responses={200: {"model": AsyncResponse}},
            methods=["POST"],
        )
        self.router.add_api_route(
            "/resolve",
            self.resolve_async,
            responses={200: {"model": AsyncResponse}},
            methods=["POST"],
        )
        self.router.add_api_route(
            "/unlink",
            self.unlink_async,
            responses={200: {"model": AsyncResponse}},
            methods=["POST"],
        )

    async def link_async(self, link_request: LinkRequest):
        correlation_id = str(uuid.uuid4())
        await asyncio.create_task(
            self.handle_service_and_link_callback(link_request, correlation_id, "link")
        )
        return AsyncResponseHelper.get_component().construct_success_async_response(
            link_request,
            correlation_id,
        )

    async def update_async(self, update_request: UpdateRequest):
        correlation_id = str(uuid.uuid4())
        await asyncio.create_task(
            self.handle_service_and_update_callback(
                update_request, correlation_id, "update"
            )
        )
        return AsyncResponseHelper.get_component().construct_success_async_response(
            update_request,
            correlation_id,
        )

    async def resolve_async(self, resolve_request: ResolveRequest):
        correlation_id = str(uuid.uuid4())
        await asyncio.create_task(
            self.handle_service_and_resolve_callback(
                resolve_request, correlation_id, "resolve"
            )
        )
        return AsyncResponseHelper.get_component().construct_success_async_response(
            resolve_request,
            correlation_id,
        )

    async def unlink_async(self, unlink_request: UnlinkRequest):
        correlation_id = str(uuid.uuid4())
        try:
            RequestValidation.get_component().validate_request(unlink_request)
            RequestValidation.get_component().validate_unlink_async_request_header(
                unlink_request
            )
        except RequestValidationException as e:
            error_response = (
                AsyncResponseHelper.get_component().construct_error_async_response(
                    unlink_request, e
                )
            )
            return error_response
        await asyncio.create_task(
            self.handle_service_and_resolve_callback(
                unlink_request, correlation_id, "unlink"
            )
        )
        return AsyncResponseHelper.get_component().construct_success_async_response(
            unlink_request,
            correlation_id,
        )

    async def handle_service_and_link_callback(
        self, link_request: LinkRequest, correlation_id: str, action: str
    ):
        try:
            RequestValidation.get_component().validate_async_request(link_request)
            RequestValidation.get_component().validate_link_async_request_header(
                link_request
            )
            single_link_responses: list[
                SingleLinkResponse
            ] = await self.action_to_method[action](link_request)

            async_call_back_request: (
                AsyncCallbackRequest
            ) = AsyncResponseHelper.get_component().construct_success_async_callback_link_request(
                link_request, correlation_id, single_link_responses
            )
            await self.make_callback(
                async_call_back_request,
                url=link_request.header.sender_uri,
                url_suffix=f"/on-{action}",
            )
        except RequestValidationException as e:
            _logger.error(f"Error in handle_service_and_callback: {e}")
            error_response = AsyncResponseHelper.get_component().construct_error_async_callback_request(
                link_request, e
            )
            await self.make_callback(
                error_response,
                url=link_request.header.sender_uri,
                url_suffix=f"/on-{action}",
            )

    async def handle_service_and_update_callback(
        self, request: Request, correlation_id: str, action: str
    ):
        try:
            RequestValidation.get_component().validate_async_request(request)
            RequestValidation.get_component().validate_update_async_request_header(
                request
            )
            single_update_responses: list[
                SingleUpdateResponse
            ] = await self.action_to_method[action](request)
            async_call_back_request: (
                AsyncCallbackRequest
            ) = AsyncResponseHelper.get_component().construct_success_async_callback_update_request(
                request, correlation_id, single_update_responses
            )
            await self.make_callback(
                async_call_back_request,
                url=request.header.sender_uri,
                url_suffix=f"/on-{action}",
            )
        except RequestValidationException as e:
            _logger.error(f"Error in handle_service_and_callback: {e}")
            error_response = AsyncResponseHelper.get_component().construct_error_async_callback_request(
                request, e
            )
            await self.make_callback(
                error_response,
                url=request.header.sender_uri,
                url_suffix=f"/on-{action}",
            )

    async def handle_service_and_resolve_callback(
        self, request: Request, correlation_id: str, action: str
    ):
        try:
            RequestValidation.get_component().validate_async_request(request)
            RequestValidation.get_component().validate_resolve_async_request_header(
                request
            )
            single_resolve_responses: list[
                SingleResolveResponse
            ] = await self.action_to_method[action](request)
            async_call_back_request: (
                AsyncCallbackRequest
            ) = AsyncResponseHelper.get_component().construct_success_async_callback_resolve_request(
                request, correlation_id, single_resolve_responses
            )
            await self.make_callback(
                async_call_back_request,
                url=request.header.sender_uri,
                url_suffix=f"/on-{action}",
            )
        except RequestValidationException as e:
            _logger.error(f"Error in handle_service_and_callback: {e}")
            error_response = AsyncResponseHelper.get_component().construct_error_async_callback_request(
                request, e
            )
            await self.make_callback(
                error_response,
                url=request.header.sender_uri,
                url_suffix=f"/on-{action}",
            )

    async def handle_service_and_unlink_callback(
        self, request: Request, correlation_id: str, action: str
    ):
        try:
            RequestValidation.get_component().validate_async_request(request)
            RequestValidation.get_component().validate_unlink_async_request_header(
                request
            )
            single_unlink_responses: list[
                SingleUnlinkResponse
            ] = await self.action_to_method[action](request)
            async_call_back_request: (
                AsyncCallbackRequest
            ) = AsyncResponseHelper.get_component().construct_success_async_callback_unlink_request(
                request, correlation_id, single_unlink_responses
            )
            await self.make_callback(
                async_call_back_request,
                url=request.header.sender_uri,
                url_suffix=f"/on-{action}",
            )
        except RequestValidationException as e:
            _logger.error(f"Error in handle_service_and_callback: {e}")
            error_response = AsyncResponseHelper.get_component().construct_error_async_callback_request(
                request, e
            )
            await self.make_callback(
                error_response,
                url=request.header.sender_uri,
                url_suffix=f"/on-{action}",
            )

    @staticmethod
    async def make_callback(
        async_call_back_request: AsyncCallbackRequest, url=None, url_suffix=None
    ):
        if not (url or _config.default_callback_url):
            return
        elif not url:
            url = _config.default_callback_url

        asyncio.ensure_future(
            _callback(async_call_back_request, url=url, url_suffix=url_suffix)
        )
