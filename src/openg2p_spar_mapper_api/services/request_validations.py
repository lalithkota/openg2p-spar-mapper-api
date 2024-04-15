from openg2p_fastapi_common.service import BaseService
from openg2p_g2pconnect_common_lib.schemas import (
    SyncResponseStatusReasonCodeEnum,
)
from openg2p_g2pconnect_common_lib.schemas.async_schemas import (
    AsyncResponseStatusReasonCodeEnum,
)

from .exceptions import RequestValidationException


class RequestValidation(BaseService):
    def validate_link_request_header(self, request) -> None:
        if request.header.action != "link":
            raise RequestValidationException(
                code=SyncResponseStatusReasonCodeEnum.rjct_action_not_supported,
                message=SyncResponseStatusReasonCodeEnum.rjct_action_not_supported,
            )
        return None

    def validate_update_request_header(self, request) -> None:
        if request.header.action != "update":
            raise RequestValidationException(
                code=SyncResponseStatusReasonCodeEnum.rjct_action_not_supported,
                message=SyncResponseStatusReasonCodeEnum.rjct_action_not_supported,
            )
        return None

    def validate_resolve_request_header(self, request) -> None:
        if request.header.action != "resolve":
            raise RequestValidationException(
                code=SyncResponseStatusReasonCodeEnum.rjct_action_not_supported,
                message=SyncResponseStatusReasonCodeEnum.rjct_action_not_supported,
            )
        return None

    def validate_unlink_request_header(self, request) -> None:
        if request.header.action != "unlink":
            raise RequestValidationException(
                code=SyncResponseStatusReasonCodeEnum.rjct_action_not_supported,
                message=SyncResponseStatusReasonCodeEnum.rjct_action_not_supported,
            )
        return None

    def validate_request(self, request) -> None:
        # TODO: Validate the request
        return None

    def validate_link_async_request_header(self, request) -> None:
        if request.header.action != "link":
            raise RequestValidationException(
                code=AsyncResponseStatusReasonCodeEnum.rjct_action_not_supported,
                message=AsyncResponseStatusReasonCodeEnum.rjct_action_not_supported,
            )
        return None

    def validate_update_async_request_header(self, request) -> None:
        if request.header.action != "update":
            raise RequestValidationException(
                code=AsyncResponseStatusReasonCodeEnum.rjct_action_not_supported,
                message=AsyncResponseStatusReasonCodeEnum.rjct_action_not_supported,
            )
        return None

    def validate_resolve_async_request_header(self, request) -> None:
        if request.header.action != "resolve":
            raise RequestValidationException(
                code=AsyncResponseStatusReasonCodeEnum.rjct_action_not_supported,
                message=AsyncResponseStatusReasonCodeEnum.rjct_action_not_supported,
            )
        return None

    def validate_unlink_async_request_header(self, request) -> None:
        if request.header.action != "unlink":
            raise RequestValidationException(
                code=AsyncResponseStatusReasonCodeEnum.rjct_action_not_supported,
                message=AsyncResponseStatusReasonCodeEnum.rjct_action_not_supported,
            )
        return None

    def validate_async_request(self, request) -> None:
        # TODO: Validate the request
        return None
