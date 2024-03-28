import asyncio
import uuid
import httpx
import logging

from openg2p_fastapi_common.controller import BaseController
from openg2p_g2pconnect_common_lib.common.schemas import (
    Request,
    AsyncResponse,
    AsyncCallbackRequest,
)
from openg2p_g2pconnect_common_lib.mapper.schemas.link import (
    SingleLinkResponse,
)
from src.openg2p_spar_mapper_api.config import Settings
from src.openg2p_spar_mapper_api.services import (
    RequestValidation,
    AsyncResponseHelper,
    MapperService,
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

        self.router.prefix += "/g2pconnect/mapper/async"
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

    async def link_async(self, request: Request):

        correlation_id = str(uuid.uuid4())
        await asyncio.create_task(
            self.handle_service_and_callback(request, correlation_id, "link")
        )
        return AsyncResponseHelper.get_component().construct_success_async_response(
            request,
            correlation_id,
        )

    async def update_async(self, request: Request):

        correlation_id = str(uuid.uuid4())
        await asyncio.create_task(
            self.handle_service_and_callback(request, correlation_id, "update")
        )
        return AsyncResponseHelper.get_component().construct_success_async_response(
            request,
            correlation_id,
        )

    async def resolve_async(self, request: Request):

        correlation_id = str(uuid.uuid4())
        await asyncio.create_task(
            self.handle_service_and_callback(request, correlation_id, "resolve")
        )
        return AsyncResponseHelper.get_component().construct_success_async_response(
            request,
            correlation_id,
        )

    async def unlink_async(self, request: Request):

        correlation_id = str(uuid.uuid4())
        await asyncio.create_task(
            self.handle_service_and_callback(request, correlation_id, "unlink")
        )
        return AsyncResponseHelper.get_component().construct_success_async_response(
            request,
            correlation_id,
        )

    async def handle_service_and_callback(
        self, request: Request, correlation_id: str, action: str
    ):
        try:
            RequestValidation.validate_request(request)
            RequestValidation.validate_link_request_header(request)
            single_link_responses: list[SingleLinkResponse] = (
                await self.action_to_method[action](request)
            )
            async_call_back_request: (
                AsyncCallbackRequest
            ) = AsyncResponseHelper.get_component().construct_success_async_callback_request(
                request, correlation_id, single_link_responses
            )
            await self.make_callback(
                async_call_back_request,
                url=request.header.sender_uri,
                url_suffix=f"/on-{action}",
            )
        except RequestValidationException as e:
            _logger.error(f"Error in handle_service_and_callback: {e}")
            error_response = AsyncResponseHelper.get_component().construct_error_async_callback_request(
                request, correlation_id, e
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
