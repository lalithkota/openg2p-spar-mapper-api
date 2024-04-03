from datetime import datetime

from openg2p_fastapi_common.service import BaseService
from openg2p_g2pconnect_common_lib.common.schemas import (
    AsyncAck,
    AsyncCallbackRequest,
    AsyncCallbackRequestHeader,
    AsyncResponse,
    AsyncResponseMessage,
    Request,
    StatusEnum,
    SyncResponse,
    SyncResponseHeader,
)
from openg2p_g2pconnect_common_lib.mapper.schemas import (
    LinkRequest,
    LinkResponse,
    ResolveRequest,
    ResolveResponse,
    SingleLinkResponse,
    SingleResolveResponse,
    SingleUnlinkResponse,
    SingleUpdateResponse,
    UnlinkRequest,
    UnlinkResponse,
    UpdateRequest,
    UpdateResponse,
)

from .exceptions import (
    RequestValidationException,
)


class SyncResponseHelper(BaseService):
    @staticmethod
    def construct_success_sync_link_response(
        request: Request,
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
        # if completed_count == 0:
        #     raise LinkValidationException(
        #         message="All requests in transaction failed.",
        #         status=StatusEnum.rjct,
        #         validation_error_type=LinkStatusReasonCode.rjct_errors_too_many,
        #     )

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

    @staticmethod
    def construct_success_sync_update_response(
        request: Request,
        single_update_responses: list[SingleUpdateResponse],
    ) -> SyncResponse:
        updateRequest: UpdateRequest = UpdateRequest.model_validate(request.message)
        updateResponse: UpdateResponse = UpdateResponse(
            transaction_id=updateRequest.transaction_id,
            correlation_id=None,
            update_response=single_update_responses,
        )
        total_count = len(updateResponse.update_response)
        completed_count = len(
            [
                update
                for update in updateResponse.update_response
                if update.status == StatusEnum.succ
            ]
        )
        # if completed_count == 0:
        #     raise UpdateValidationException(
        #         message="All requests in transaction failed.",
        #         status=StatusEnum.rjct,
        #         validation_error_type=UpdateStatusReasonCode.rjct_errors_too_many,
        #     )
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
            message=updateResponse,
        )

    @staticmethod
    def construct_success_sync_resolve_response(
        request: Request,
        single_resolve_responses: list[SingleResolveResponse],
    ) -> SyncResponse:
        resolveRequest: ResolveRequest = ResolveRequest.model_validate(request.message)
        resolveResponse: ResolveResponse = ResolveResponse(
            transaction_id=resolveRequest.transaction_id,
            correlation_id=None,
            resolve_response=single_resolve_responses,
        )
        total_count = len(resolveResponse.resolve_response)
        completed_count = len(
            [
                resolve
                for resolve in resolveResponse.resolve_response
                if resolve.status == StatusEnum.succ
            ]
        )
        # if completed_count == 0:
        #     raise ResolveValidationException(
        #         message="All requests in transaction failed.",
        #         status=StatusEnum.rjct,
        #         validation_error_type=ResolveStatusReasonCode.rjct_errors_too_many,
        #     )
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
            message=resolveResponse,
        )

    @staticmethod
    def construct_success_sync_unlink_response(
        request: Request,
        single_unlink_responses: list[SingleUnlinkResponse],
    ) -> SyncResponse:
        unlinkRequest: UnlinkRequest = UnlinkRequest.model_validate(request.message)
        unlinkResponse: UnlinkResponse = UnlinkResponse(
            transaction_id=unlinkRequest.transaction_id,
            correlation_id=None,
            unlink_response=single_unlink_responses,
        )
        total_count = len(unlinkResponse.unlink_response)
        completed_count = len(
            [
                unlink
                for unlink in unlinkResponse.unlink_response
                if unlink.status == StatusEnum.succ
            ]
        )
        # if completed_count == 0:
        #     raise UnlinkValidationException(
        #         message="All requests in transaction failed.",
        #         status=StatusEnum.rjct,
        #         validation_error_type=ResolveStatusReasonCode.rjct_errors_too_many,
        #     )
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
            message=unlinkResponse,
        )

    @staticmethod
    def construct_error_sync_response(
        request: Request, exception: RequestValidationException
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


class AsyncResponseHelper(BaseService):
    def construct_success_async_response(
        self,
        request: Request,
        correlation_id: str,
    ) -> AsyncResponse:
        return AsyncResponse(
            message=AsyncResponseMessage(
                ack_status=AsyncAck.ACK,
                correlation_id=correlation_id,
                timestamp=datetime.utcnow(),
            )
        )

    def construct_error_async_response(
        self,
        request: Request,
        correlation_id: str,
        exception: RequestValidationException,
    ) -> AsyncResponse:
        return AsyncResponse(
            message=AsyncResponseMessage(
                ack_status=AsyncAck.NACK,
                correlation_id=correlation_id,
                timestamp=datetime.utcnow(),
                error={
                    "code": exception.code,
                    "message": exception.message,
                },
            )
        )

    def construct_success_async_callback_link_request(
        self,
        request: Request,
        correlation_id: str,
        single_link_responses: list[SingleLinkResponse],
    ) -> AsyncCallbackRequest:
        total_count = len(single_link_responses)
        completed_count = len(
            [link for link in single_link_responses if link.status == StatusEnum.succ]
        )
        linkRequest: LinkRequest = LinkRequest.model_validate(request.message)

        linkResponse: LinkResponse = LinkResponse(
            transaction_id=linkRequest.transaction_id,
            correlation_id=None,
            link_response=single_link_responses,
        )
        return AsyncCallbackRequest(
            signature=None,
            header=AsyncCallbackRequestHeader(
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

    def construct_success_async_callback_update_request(
        self,
        request: Request,
        correlation_id: str,
        single_update_responses: list[SingleUpdateResponse],
    ) -> AsyncCallbackRequest:
        total_count = len(single_update_responses)
        completed_count = len(
            [
                update
                for update in single_update_responses
                if update.status == StatusEnum.succ
            ]
        )
        updateRequest: UpdateRequest = UpdateRequest.model_validate(request.message)
        updateResponse: UpdateResponse = UpdateResponse(
            transaction_id=updateRequest.transaction_id,
            correlation_id=None,
            update_response=single_update_responses,
        )
        return AsyncCallbackRequest(
            signature=None,
            header=AsyncCallbackRequestHeader(
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
            message=updateResponse,
        )

    def construct_success_async_callback_resolve_request(
        self,
        request: Request,
        correlation_id: str,
        single_resolve_responses: list[SingleResolveResponse],
    ) -> AsyncCallbackRequest:
        total_count = len(single_resolve_responses)
        completed_count = len(
            [
                resolve
                for resolve in single_resolve_responses
                if resolve.status == StatusEnum.succ
            ]
        )
        resolveRequest: ResolveRequest = ResolveRequest.model_validate(request.message)
        resolveResponse: ResolveResponse = ResolveResponse(
            transaction_id=resolveRequest.transaction_id,
            correlation_id=None,
            resolve_response=single_resolve_responses,
        )
        return AsyncCallbackRequest(
            signature=None,
            header=AsyncCallbackRequestHeader(
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
            message=resolveResponse,
        )

    def construct_success_async_callback_unlink_request(
        self,
        request: Request,
        correlation_id: str,
        single_unlink_responses: list[SingleUnlinkResponse],
    ) -> AsyncCallbackRequest:
        total_count = len(single_unlink_responses)
        completed_count = len(
            [
                unlink
                for unlink in single_unlink_responses
                if unlink.status == StatusEnum.succ
            ]
        )
        unlinkRequest: UnlinkRequest = UnlinkRequest.model_validate(request.message)
        unlinkResponse: UnlinkResponse = UnlinkResponse(
            transaction_id=unlinkRequest.transaction_id,
            correlation_id=None,
            unlink_response=single_unlink_responses,
        )
        return AsyncCallbackRequest(
            signature=None,
            header=AsyncCallbackRequestHeader(
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
            message=unlinkResponse,
        )

    def construct_error_async_callback_request(
        self,
        request: Request,
        correlation_id: str,
        exception: RequestValidationException,
    ) -> AsyncCallbackRequest:
        return AsyncCallbackRequest(
            signature=None,
            header=AsyncCallbackRequestHeader(
                version="1.0.0",
                message_id=request.header.message_id,
                message_ts=datetime.now().isoformat(),
                action=request.header.action,
                status=StatusEnum.rjct,
                status_reason_code=exception.code,
                status_reason_message=exception.message,
                total_count=0,
                completed_count=0,
                sender_id=request.header.sender_id,
                receiver_id=request.header.receiver_id,
                is_msg_encrypted=False,
                meta={},
            ),
            message={},
        )
