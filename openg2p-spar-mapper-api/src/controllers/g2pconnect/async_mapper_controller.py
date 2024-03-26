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
from openg2p_g2pconnect_common_lib.spar.schemas.link import (
    SingleLinkResponse,
)
from ...config import Settings
from ...services import (
    RequestValidation,
    AsyncResponseHelper,
    MapperService,
    RequestValidationException,
)


_config = Settings.get_config()
_logger = logging.getLogger(_config.logging_default_logger_name)


class AsyncMapperController(BaseController):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.mapper_service = MapperService.get_component()

        self.router.prefix += "/g2pconnect/mapper/async"
        self.router.tags += ["G2PConnect Mapper Async"]

        self.action_to_method = {
            "link": self.mapper_service.link,
            # "update": self.update_async,
            # "resolve": self.resolve_async,
            # "unlink": self.unlink_async,
        }

        self.router.add_api_route(
            "/link",
            self.link_async,
            responses={200: {"model": AsyncResponse}},
            methods=["POST"],
        )
        # self.router.add_api_route(
        #     "/update",
        #     self.update,
        #     responses={200: {"model": AsyncResponse}},
        #     methods=["POST"],
        # )
        # self.router.add_api_route(
        #     "/resolve",
        #     self.resolve,
        #     responses={200: {"model": AsyncResponse}},
        #     methods=["POST"],
        # )
        # self.router.add_api_route(
        #     "/unlink",
        #     self.unlink,
        #     responses={200: {"model": AsyncResponse}},
        #     methods=["POST"],
        # )

    async def link_async(self, request: Request):

        correlation_id = str(uuid.uuid4())
        asyncio.create_task(
            self.handle_service_and_callback(request, correlation_id, "link")
        )
        return AsyncResponseHelper.get_component().construct_success_async_response(
            request,
            correlation_id,
        )

    # async def update(self, request: Request):
    #     if request.header.action != "update":
    #         raise BaseAppException(
    #             code="MPR-REQ-400",
    #             message="Received Invalid action in header for 'update'.",
    #             http_status_code=400,
    #         )
    #     # TODO: For now returning random correlation id.
    #     correlation_id = str(uuid.uuid4())
    #     # TODO: For now creating async task and forgetting
    #     asyncio.create_task(self.mapper_service.update(correlation_id, request))
    #
    #     return AsyncResponse(
    #         message=AsyncResponseMessage(
    #             ack_status=AsyncAck.ACK,
    #             correlation_id=correlation_id,
    #             timestamp=datetime.utcnow(),
    #         )
    #     )
    #
    # async def resolve(self, request: AsyncRequest):
    #     if request.header.action != "resolve":
    #         raise BaseAppException(
    #             code="MPR-REQ-400",
    #             message="Received Invalid action in header for 'resolve'.",
    #             http_status_code=400,
    #         )
    #     # TODO: For now returning random correlation id.
    #     correlation_id = str(uuid.uuid4())
    #     # TODO: For now creating async task and forgetting
    #     asyncio.create_task(self.mapper_service.resolve(correlation_id, request))
    #
    #     return AsyncResponse(
    #         message=AsyncResponseMessage(
    #             ack_status=AsyncAck.ACK,
    #             correlation_id=correlation_id,
    #             timestamp=datetime.utcnow(),
    #         )
    #     )

    async def unlink(self):
        raise NotImplementedError()

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

    async def make_callback(
        self, async_call_back_request: AsyncCallbackRequest, url=None, url_suffix=None
    ):
        if not (url or _config.default_callback_url):
            return
        elif not url:
            url = _config.default_callback_url

        asyncio.ensure_future(
            self._callback(async_call_back_request, url=url, url_suffix=url_suffix)
        )

    async def _callback(
        self, async_call_back_request: AsyncCallbackRequest, url, url_suffix=None
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
