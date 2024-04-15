from datetime import datetime

from openg2p_fastapi_common.service import BaseService
from openg2p_g2pconnect_common_lib.schemas import (
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
from openg2p_g2pconnect_mapper_lib.schemas import (
    LinkRequest,
    LinkRequestMessage,
    LinkResponse,
    LinkResponseMessage,
    ResolveRequest,
    ResolveRequestMessage,
    ResolveResponse,
    ResolveResponseMessage,
    SingleLinkResponse,
    SingleResolveResponse,
    SingleUnlinkResponse,
    SingleUpdateResponse,
    UnlinkRequest,
    UnlinkRequestMessage,
    UnlinkResponse,
    UnlinkResponseMessage,
    UpdateRequest,
    UpdateRequestMessage,
    UpdateResponse,
    UpdateResponseMessage,
)

from .exceptions import (
    RequestValidationException,
)


class SyncResponseHelper(BaseService):
    def construct_success_sync_link_response(
        self,
        link_request: LinkRequest,
        single_link_responses: list[SingleLinkResponse],
    ) -> LinkResponse:
        link_request_message: LinkRequestMessage = link_request.message
        link_response_message: LinkResponseMessage = LinkResponseMessage(
            transaction_id=link_request_message.transaction_id,
            correlation_id=None,
            link_response=single_link_responses,
        )
        total_count = len(link_response_message.link_response)
        completed_count = len(
            [
                link
                for link in link_response_message.link_response
                if link.status == StatusEnum.succ
            ]
        )
        return LinkResponse(
            header=SyncResponseHeader(
                version="1.0.0",
                message_id=link_request.header.message_id,
                message_ts=datetime.now().isoformat(),
                action=link_request.header.action,
                status=StatusEnum.succ,
                status_reason_code=None,
                status_reason_message=None,
                total_count=total_count,
                completed_count=completed_count,
                sender_id=link_request.header.sender_id,
                receiver_id=link_request.header.receiver_id,
                is_msg_encrypted=False,
                meta={},
            ),
            message=link_response_message,
        )

    def construct_success_sync_update_response(
        self,
        update_request: UpdateRequest,
        single_update_responses: list[SingleUpdateResponse],
    ) -> UpdateResponse:
        update_request_message: UpdateRequestMessage = update_request.message
        update_response_message: UpdateResponseMessage = UpdateResponseMessage(
            transaction_id=update_request_message.transaction_id,
            correlation_id=None,
            update_response=single_update_responses,
        )
        total_count = len(update_response_message.update_response)
        completed_count = len(
            [
                update
                for update in update_response_message.update_response
                if update.status == StatusEnum.succ
            ]
        )
        return UpdateResponse(
            header=SyncResponseHeader(
                version="1.0.0",
                message_id=update_request.header.message_id,
                message_ts=datetime.now().isoformat(),
                action=update_request.header.action,
                status=StatusEnum.succ,
                status_reason_code=None,
                status_reason_message=None,
                total_count=total_count,
                completed_count=completed_count,
                sender_id=update_request.header.sender_id,
                receiver_id=update_request.header.receiver_id,
                is_msg_encrypted=False,
                meta={},
            ),
            message=update_response_message,
        )

    def construct_success_sync_resolve_response(
        self,
        resolve_request: ResolveRequest,
        single_resolve_responses: list[SingleResolveResponse],
    ) -> ResolveResponse:
        resolve_request_message: ResolveRequestMessage = resolve_request.message
        resolve_response_message: ResolveResponseMessage = ResolveResponseMessage(
            transaction_id=resolve_request_message.transaction_id,
            correlation_id=None,
            resolve_response=single_resolve_responses,
        )
        total_count = len(resolve_response_message.resolve_response)
        completed_count = len(
            [
                resolve
                for resolve in resolve_response_message.resolve_response
                if resolve.status == StatusEnum.succ
            ]
        )
        return ResolveResponse(
            header=SyncResponseHeader(
                version="1.0.0",
                message_id=resolve_request.header.message_id,
                message_ts=datetime.now().isoformat(),
                action=resolve_request.header.action,
                status=StatusEnum.succ,
                status_reason_code=None,
                status_reason_message=None,
                total_count=total_count,
                completed_count=completed_count,
                sender_id=resolve_request.header.sender_id,
                receiver_id=resolve_request.header.receiver_id,
                is_msg_encrypted=False,
                meta={},
            ),
            message=resolve_response_message,
        )

    def construct_success_sync_unlink_response(
        self,
        unlink_request: UnlinkRequest,
        single_unlink_responses: list[SingleUnlinkResponse],
    ) -> UnlinkResponse:
        unlink_request_message: UnlinkRequestMessage = unlink_request.message
        unlink_response_message: UnlinkResponseMessage = UnlinkResponseMessage(
            transaction_id=unlink_request_message.transaction_id,
            correlation_id=None,
            unlink_response=single_unlink_responses,
        )
        total_count = len(unlink_response_message.unlink_response)
        completed_count = len(
            [
                unlink
                for unlink in unlink_response_message.unlink_response
                if unlink.status == StatusEnum.succ
            ]
        )
        return UnlinkResponse(
            header=SyncResponseHeader(
                version="1.0.0",
                message_id=unlink_request.header.message_id,
                message_ts=datetime.now().isoformat(),
                action=unlink_request.header.action,
                status=StatusEnum.succ,
                status_reason_code=None,
                status_reason_message=None,
                total_count=total_count,
                completed_count=completed_count,
                sender_id=unlink_request.header.sender_id,
                receiver_id=unlink_request.header.receiver_id,
                is_msg_encrypted=False,
                meta={},
            ),
            message=unlink_response_message,
        )

    def construct_error_sync_response(
        self, request: Request, exception: RequestValidationException
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
        exception: RequestValidationException,
    ) -> AsyncResponse:
        return AsyncResponse(
            message=AsyncResponseMessage(
                ack_status=AsyncAck.NACK,
                timestamp=datetime.utcnow(),
                error={
                    "code": exception.code,
                    "message": exception.message,
                },
            )
        )

    def construct_success_async_callback_link_request(
        self,
        link_request: LinkRequest,
        correlation_id: str,
        single_link_responses: list[SingleLinkResponse],
    ) -> AsyncCallbackRequest:
        total_count = len(single_link_responses)
        completed_count = len(
            [link for link in single_link_responses if link.status == StatusEnum.succ]
        )
        link_request_message: LinkRequestMessage = link_request.message

        link_response_message: LinkResponseMessage = LinkResponseMessage(
            transaction_id=link_request_message.transaction_id,
            correlation_id=None,
            link_response=single_link_responses,
        )
        return AsyncCallbackRequest(
            signature=None,
            header=AsyncCallbackRequestHeader(
                version="1.0.0",
                message_id=link_request.header.message_id,
                message_ts=datetime.now().isoformat(),
                action=link_request.header.action,
                status=StatusEnum.succ,
                status_reason_code=None,
                status_reason_message=None,
                total_count=total_count,
                completed_count=completed_count,
                sender_id=link_request.header.sender_id,
                receiver_id=link_request.header.receiver_id,
                is_msg_encrypted=False,
                meta={},
            ),
            message=link_response_message,
        )

    def construct_success_async_callback_update_request(
        self,
        update_request: UpdateRequest,
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
        update_request_message: UpdateRequestMessage = update_request.message
        update_response_message: UpdateResponseMessage = UpdateResponseMessage(
            transaction_id=update_request_message.transaction_id,
            correlation_id=None,
            update_response=single_update_responses,
        )
        return AsyncCallbackRequest(
            signature=None,
            header=AsyncCallbackRequestHeader(
                version="1.0.0",
                message_id=update_request.header.message_id,
                message_ts=datetime.now().isoformat(),
                action=update_request.header.action,
                status=StatusEnum.succ,
                status_reason_code=None,
                status_reason_message=None,
                total_count=total_count,
                completed_count=completed_count,
                sender_id=update_request.header.sender_id,
                receiver_id=update_request.header.receiver_id,
                is_msg_encrypted=False,
                meta={},
            ),
            message=update_response_message,
        )

    def construct_success_async_callback_resolve_request(
        self,
        resolve_request: ResolveRequest,
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
        resolve_request_message: ResolveRequestMessage = resolve_request.message
        resolve_response_message: ResolveResponseMessage = ResolveResponseMessage(
            transaction_id=resolve_request_message.transaction_id,
            correlation_id=None,
            resolve_response=single_resolve_responses,
        )
        return AsyncCallbackRequest(
            signature=None,
            header=AsyncCallbackRequestHeader(
                version="1.0.0",
                message_id=resolve_request.header.message_id,
                message_ts=datetime.now().isoformat(),
                action=resolve_request.header.action,
                status=StatusEnum.succ,
                status_reason_code=None,
                status_reason_message=None,
                total_count=total_count,
                completed_count=completed_count,
                sender_id=resolve_request.header.sender_id,
                receiver_id=resolve_request.header.receiver_id,
                is_msg_encrypted=False,
                meta={},
            ),
            message=resolve_response_message,
        )

    def construct_success_async_callback_unlink_request(
        self,
        unlink_request: UnlinkRequest,
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
        unlink_request_message: UnlinkRequestMessage = unlink_request.message
        unlink_response_message: UnlinkResponseMessage = UnlinkResponseMessage(
            transaction_id=unlink_request_message.transaction_id,
            correlation_id=None,
            unlink_response=single_unlink_responses,
        )
        return AsyncCallbackRequest(
            signature=None,
            header=AsyncCallbackRequestHeader(
                version="1.0.0",
                message_id=unlink_request.header.message_id,
                message_ts=datetime.now().isoformat(),
                action=unlink_request.header.action,
                status=StatusEnum.succ,
                status_reason_code=None,
                status_reason_message=None,
                total_count=total_count,
                completed_count=completed_count,
                sender_id=unlink_request.header.sender_id,
                receiver_id=unlink_request.header.receiver_id,
                is_msg_encrypted=False,
                meta={},
            ),
            message=unlink_response_message,
        )

    def construct_error_async_callback_request(
        self,
        request: Request,
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
