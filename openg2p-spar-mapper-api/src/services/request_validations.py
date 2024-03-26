from openg2p_fastapi_common.service import BaseService
from openg2p_g2pconnect_common_lib.common.schemas import (
    SyncResponseStatusReasonCodeEnum,
)

from .exceptions import RequestValidationException


class RequestValidation(BaseService):
    @staticmethod
    def validate_link_request_header(request) -> None:
        if request.header.action != "link":
            raise RequestValidationException(
                code=SyncResponseStatusReasonCodeEnum.rjct_action_not_supported,
                message=SyncResponseStatusReasonCodeEnum.rjct_action_not_supported,
            )
        return None
    @staticmethod
    def validate_update_request_header(request) -> None:
        if request.header.action != "update":
            raise RequestValidationException(
                code=SyncResponseStatusReasonCodeEnum.rjct_action_not_supported,
                message=SyncResponseStatusReasonCodeEnum.rjct_action_not_supported,
            )
        return None
    @staticmethod
    def validate_resolve_request_header(request) -> None:
        if request.header.action != "resolve":
            raise RequestValidationException(
                code=SyncResponseStatusReasonCodeEnum.rjct_action_not_supported,
                message=SyncResponseStatusReasonCodeEnum.rjct_action_not_supported,
            )
        return None
    @staticmethod
    def validate_request(request) -> None:
        # TODO: Validate the request
        return None
