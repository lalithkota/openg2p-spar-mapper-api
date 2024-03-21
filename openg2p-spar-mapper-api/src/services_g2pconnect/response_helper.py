from datetime import datetime

from openg2p_fastapi_common.service import BaseService
from openg2p_g2pconnect_common_lib.common.schemas import (
    SyncRequest,
    SyncResponse,
    SyncResponseHeader,
    StatusEnum,
)
from openg2p_g2pconnect_common_lib.spar.schemas.link import (
    LinkResponse,
    LinkRequest,
    SingleLinkResponse,
)

from .exceptions import RequestValidationException


class SyncResponseHelper(BaseService):

    def construct_success_sync_response(
        self,
        request: SyncRequest,
        single_link_responses: list[SingleLinkResponse],
    ) -> SyncResponse:
        linkRequest: LinkRequest = LinkRequest.model_validate(request.message)
        linkResponse: LinkResponse = LinkResponse(
            transaction_id=linkRequest.transaction_id,
            correlation_id=None,
            link_response=single_link_responses,
        )
        total_count = len(linkResponse.link_response)
        completed_count = len(
            [
                link
                for link in linkResponse.link_response
                if link.status == StatusEnum.succ
            ]
        )

        return SyncResponse(
            header=SyncResponseHeader(
                version="1.0.0",
                message_id=request.header.message_id,
                message_ts=datetime.now().isoformat(),
                action=request.header.action,
                status=StatusEnum.succ,
                status_reason_code=None,
                status_reason_message=None,
                total_count=total_count,
                completed_count=completed_count,
                sender_id=request.header.sender_id,
                receiver_id=request.header.receiver_id,
                is_msg_encrypted=False,
                meta={},
            ),
            message=linkResponse,
        )

    def construct_error_sync_response(
        self,
        request: SyncRequest, exception: RequestValidationException
    ) -> SyncResponse:
        return SyncResponse(
            signature=None,
            header=SyncResponseHeader(
                version="1.0.0",
                message_id=request.header.message_id,
                message_ts=datetime.now().isoformat(),
                action=request.header.action,
                status=StatusEnum.rjct,
                status_reason_code=exception.code,
                status_reason_message=exception.message,
            ),
            message={},
        )
