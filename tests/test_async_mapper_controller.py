import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from openg2p_g2pconnect_common_lib.schemas import (
    AsyncAck,
    AsyncCallbackRequest,
    AsyncCallbackRequestHeader,
    AsyncResponse,
    AsyncResponseMessage,
    RequestHeader,
    StatusEnum,
)
from openg2p_g2pconnect_mapper_lib.schemas import (
    LinkRequest,
    LinkRequestMessage,
    SingleLinkRequest,
    SingleLinkResponse,
)
from openg2p_g2pconnect_mapper_lib.schemas.resolve import (
    ResolveRequest,
    ResolveRequestMessage,
    SingleResolveRequest,
    SingleResolveResponse,
)
from openg2p_g2pconnect_mapper_lib.schemas.unlink import (
    SingleUnlinkRequest,
    SingleUnlinkResponse,
    UnlinkRequest,
    UnlinkRequestMessage,
)
from openg2p_g2pconnect_mapper_lib.schemas.update import (
    SingleUpdateRequest,
    SingleUpdateResponse,
    UpdateRequest,
    UpdateRequestMessage,
)
from openg2p_spar_mapper_api.controllers.async_mapper_controller import (
    AsyncMapperController,
)


@pytest.mark.asyncio
@patch(
    "openg2p_spar_mapper_api.controllers.async_mapper_controller.AsyncResponseHelper.get_component"
)
@patch(
    "openg2p_spar_mapper_api.controllers.async_mapper_controller.RequestValidation.get_component"
)
@patch(
    "openg2p_spar_mapper_api.controllers.async_mapper_controller.MapperService.get_component"
)
async def test_link_async(
    mock_mapper_service_get_component,
    mock_request_validation_get_component,
    mock_async_response_helper_get_component,
):
    # Setup MagicMock for MapperService and RequestValidation components
    mock_mapper_service_instance = MagicMock()
    mock_mapper_service_instance.link = (
        AsyncMock()
    )  # link method should return an awaitable
    mock_request_validation_instance = MagicMock()

    # Assign return values to the get_component mocks
    mock_mapper_service_get_component.return_value = mock_mapper_service_instance
    mock_request_validation_get_component.return_value = (
        mock_request_validation_instance
    )
    mock_async_response_helper_instance = MagicMock()
    expected_response = AsyncResponse(
        message=AsyncResponseMessage(
            correlation_id="1234",
            timestamp=datetime.utcnow().isoformat(),
            ack_status="ACK",
        )
    )
    mock_async_response_helper_instance.construct_success_async_response.return_value = (
        expected_response
    )
    mock_async_response_helper_get_component.return_value = (
        mock_async_response_helper_instance
    )

    controller = AsyncMapperController()

    mock_link_request = LinkRequest(
        header=RequestHeader(
            message_id="test_message_id",
            message_ts=datetime.utcnow().isoformat(),
            action="link",
            sender_id="test_sender",
            total_count=1,
        ),
        message=LinkRequestMessage(
            transaction_id="test_transaction_id",
            link_request=[
                SingleLinkRequest(
                    reference_id="test_ref",
                    timestamp=datetime.utcnow(),
                    id="test_id",
                    fa="test_fa",
                )
            ],
        ),
    )

    actual_response = await controller.link_async(mock_link_request)
    assert (
        actual_response == expected_response
    ), "The response did not match the expected response."
    assert actual_response.message.correlation_id == "1234"
    assert actual_response.message.ack_status == AsyncAck.ACK
    assert actual_response.message.timestamp == expected_response.message.timestamp


@pytest.mark.asyncio
@patch(
    "openg2p_spar_mapper_api.controllers.async_mapper_controller.AsyncResponseHelper.get_component"
)
@patch(
    "openg2p_spar_mapper_api.controllers.async_mapper_controller.RequestValidation.get_component"
)
@patch(
    "openg2p_spar_mapper_api.controllers.async_mapper_controller.MapperService.get_component"
)
async def test_handle_service_and_link_callback(
    mock_mapper_service_get_component,
    mock_request_validation_get_component,
    mock_async_response_helper_get_component,
):
    mock_mapper_service_instance = AsyncMock()
    mock_mapper_service_get_component.return_value = mock_mapper_service_instance
    single_link_responses = [
        SingleLinkResponse(
            reference_id="test_ref",
            timestamp=datetime.utcnow(),
            status=StatusEnum.succ,
            locale="en",
        )
    ]
    mock_mapper_service_instance.link.return_value = single_link_responses

    mock_request_validation_instance = AsyncMock()
    mock_request_validation_get_component.return_value = (
        mock_request_validation_instance
    )
    mock_async_response_helper_instance = AsyncMock()
    mock_async_response_helper_get_component.return_value = (
        mock_async_response_helper_instance
    )

    controller = AsyncMapperController()

    link_request = LinkRequest(
        header=RequestHeader(
            message_id="test_message_id",
            message_ts=datetime.utcnow().isoformat(),
            action="link",
            sender_id="test_sender",
            total_count=1,
        ),
        message=LinkRequestMessage(
            transaction_id="test_transaction_id",
            link_request=[
                SingleLinkRequest(
                    reference_id="test_ref",
                    timestamp=datetime.utcnow(),
                    id="test_id",
                    fa="test_fa",
                )
            ],
        ),
    )

    # Simulate the behavior without actual execution
    await controller.handle_service_and_link_callback(
        link_request, "correlation_id", "link"
    )

    mock_async_response_helper_instance.construct_success_async_callback_link_request.assert_called_once_with(
        link_request, "correlation_id", single_link_responses
    )

    callback_args = (
        mock_async_response_helper_instance.construct_success_async_callback_link_request.call_args
    )
    assert callback_args[0][0] == link_request
    assert callback_args[0][1] == "correlation_id"
    assert callback_args[0][2] == single_link_responses


@pytest.mark.asyncio
@patch(
    "openg2p_spar_mapper_api.controllers.async_mapper_controller.AsyncResponseHelper.get_component"
)
@patch(
    "openg2p_spar_mapper_api.controllers.async_mapper_controller.RequestValidation.get_component"
)
@patch(
    "openg2p_spar_mapper_api.controllers.async_mapper_controller.MapperService.get_component"
)
async def test_update_async(
    mock_mapper_service_get_component,
    mock_request_validation_get_component,
    mock_async_response_helper_get_component,
):
    mock_mapper_service_instance = MagicMock()
    mock_mapper_service_instance.update = AsyncMock()
    mock_request_validation_instance = MagicMock()
    mock_mapper_service_get_component.return_value = mock_mapper_service_instance
    mock_request_validation_get_component.return_value = (
        mock_request_validation_instance
    )
    mock_async_response_helper_instance = MagicMock()
    expected_response = AsyncResponse(
        message=AsyncResponseMessage(
            correlation_id="1234",
            timestamp=datetime.utcnow().isoformat(),
            ack_status="ACK",
        )
    )
    mock_async_response_helper_instance.construct_success_async_response.return_value = (
        expected_response
    )
    mock_async_response_helper_get_component.return_value = (
        mock_async_response_helper_instance
    )

    controller = AsyncMapperController()

    mock_update_request = UpdateRequest(
        header=RequestHeader(
            message_id="test_message_id",
            message_ts=datetime.utcnow().isoformat(),
            action="update",
            sender_id="test_sender",
            total_count=1,
        ),
        message=UpdateRequestMessage(
            transaction_id="test_transaction_id",
            update_request=[
                SingleUpdateRequest(
                    reference_id="test_ref",
                    timestamp=datetime.utcnow(),
                    id="test_id",
                    fa="test_fa",
                )
            ],
        ),
    )

    actual_response = await controller.update_async(mock_update_request)
    assert (
        actual_response == expected_response
    ), "The response did not match the expected response."
    assert actual_response.message.correlation_id == "1234"
    assert actual_response.message.ack_status == AsyncAck.ACK
    assert actual_response.message.timestamp == expected_response.message.timestamp


@pytest.mark.asyncio
@patch(
    "openg2p_spar_mapper_api.controllers.async_mapper_controller.AsyncResponseHelper.get_component"
)
@patch(
    "openg2p_spar_mapper_api.controllers.async_mapper_controller.RequestValidation.get_component"
)
@patch(
    "openg2p_spar_mapper_api.controllers.async_mapper_controller.MapperService.get_component"
)
async def test_handle_service_and_update_callback(
    mock_mapper_service_get_component,
    mock_request_validation_get_component,
    mock_async_response_helper_get_component,
):
    mock_mapper_service_instance = AsyncMock()
    mock_mapper_service_get_component.return_value = mock_mapper_service_instance
    single_update_responses = [
        SingleUpdateResponse(
            reference_id="test_ref",
            timestamp=datetime.utcnow(),
            status=StatusEnum.succ,
            locale="en",
        )
    ]
    mock_mapper_service_instance.update.return_value = single_update_responses

    mock_request_validation_instance = AsyncMock()
    mock_request_validation_get_component.return_value = (
        mock_request_validation_instance
    )
    mock_async_response_helper_instance = AsyncMock()
    mock_async_response_helper_get_component.return_value = (
        mock_async_response_helper_instance
    )

    controller = AsyncMapperController()

    update_request = UpdateRequest(
        header=RequestHeader(
            message_id="test_message_id",
            message_ts=datetime.utcnow().isoformat(),
            action="update",
            sender_id="test_sender",
            total_count=1,
        ),
        message=UpdateRequestMessage(
            transaction_id="test_transaction_id",
            update_request=[
                SingleUpdateRequest(
                    reference_id="test_ref",
                    timestamp=datetime.utcnow(),
                    id="test_id",
                    fa="test_fa",
                )
            ],
        ),
    )
    await controller.handle_service_and_update_callback(
        update_request, "correlation_id", "update"
    )

    mock_async_response_helper_instance.construct_success_async_callback_update_request.assert_called_once_with(
        update_request, "correlation_id", single_update_responses
    )

    callback_args = (
        mock_async_response_helper_instance.construct_success_async_callback_update_request.call_args
    )
    assert callback_args[0][0] == update_request
    assert callback_args[0][1] == "correlation_id"
    assert callback_args[0][2] == single_update_responses


@pytest.mark.asyncio
@patch(
    "openg2p_spar_mapper_api.controllers.async_mapper_controller.AsyncResponseHelper.get_component"
)
@patch(
    "openg2p_spar_mapper_api.controllers.async_mapper_controller.RequestValidation.get_component"
)
@patch(
    "openg2p_spar_mapper_api.controllers.async_mapper_controller.MapperService.get_component"
)
async def test_resolve_async(
    mock_mapper_service_get_component,
    mock_request_validation_get_component,
    mock_async_response_helper_get_component,
):
    mock_mapper_service_instance = MagicMock()
    mock_mapper_service_instance.resolve = AsyncMock()
    mock_request_validation_instance = MagicMock()
    mock_mapper_service_get_component.return_value = mock_mapper_service_instance
    mock_request_validation_get_component.return_value = (
        mock_request_validation_instance
    )
    mock_async_response_helper_instance = MagicMock()
    expected_response = AsyncResponse(
        message=AsyncResponseMessage(
            correlation_id="1234",
            timestamp=datetime.utcnow().isoformat(),
            ack_status="ACK",
        )
    )
    mock_async_response_helper_instance.construct_success_async_response.return_value = (
        expected_response
    )
    mock_async_response_helper_get_component.return_value = (
        mock_async_response_helper_instance
    )

    controller = AsyncMapperController()

    mock_resolve_request = ResolveRequest(
        header=RequestHeader(
            message_id="test_message_id",
            message_ts=datetime.utcnow().isoformat(),
            action="resolve",
            sender_id="test_sender",
            total_count=1,
        ),
        message=ResolveRequestMessage(
            transaction_id="test_transaction_id",
            resolve_request=[
                SingleResolveRequest(
                    reference_id="test_ref",
                    timestamp=datetime.utcnow(),
                    id="test_id",
                    fa="test_fa",
                )
            ],
        ),
    )

    actual_response = await controller.resolve_async(mock_resolve_request)
    assert (
        actual_response == expected_response
    ), "The response did not match the expected response."
    assert actual_response.message.correlation_id == "1234"
    assert actual_response.message.ack_status == AsyncAck.ACK
    assert actual_response.message.timestamp == expected_response.message.timestamp


@pytest.mark.asyncio
@patch(
    "openg2p_spar_mapper_api.controllers.async_mapper_controller.AsyncResponseHelper.get_component"
)
@patch(
    "openg2p_spar_mapper_api.controllers.async_mapper_controller.RequestValidation.get_component"
)
@patch(
    "openg2p_spar_mapper_api.controllers.async_mapper_controller.MapperService.get_component"
)
async def test_handle_service_and_resolve_callback(
    mock_mapper_service_get_component,
    mock_request_validation_get_component,
    mock_async_response_helper_get_component,
):
    mock_mapper_service_instance = AsyncMock()
    mock_mapper_service_get_component.return_value = mock_mapper_service_instance
    single_resolve_responses = [
        SingleResolveResponse(
            reference_id="test_ref",
            timestamp=datetime.utcnow(),
            status=StatusEnum.succ,
            locale="en",
        )
    ]
    mock_mapper_service_instance.resolve.return_value = single_resolve_responses

    mock_request_validation_instance = AsyncMock()
    mock_request_validation_get_component.return_value = (
        mock_request_validation_instance
    )
    mock_async_response_helper_instance = AsyncMock()
    mock_async_response_helper_get_component.return_value = (
        mock_async_response_helper_instance
    )

    controller = AsyncMapperController()

    resolve_request = ResolveRequest(
        header=RequestHeader(
            message_id="test_message_id",
            message_ts=datetime.utcnow().isoformat(),
            action="resolve",
            sender_id="test_sender",
            total_count=1,
        ),
        message=ResolveRequestMessage(
            transaction_id="test_transaction_id",
            resolve_request=[
                SingleResolveRequest(
                    reference_id="test_ref",
                    timestamp=datetime.utcnow(),
                    id="test_id",
                    fa="test_fa",
                )
            ],
        ),
    )
    await controller.handle_service_and_resolve_callback(
        resolve_request, "correlation_id", "resolve"
    )

    mock_async_response_helper_instance.construct_success_async_callback_resolve_request.assert_called_once_with(
        resolve_request, "correlation_id", single_resolve_responses
    )

    callback_args = (
        mock_async_response_helper_instance.construct_success_async_callback_resolve_request.call_args
    )
    assert callback_args[0][0] == resolve_request
    assert callback_args[0][1] == "correlation_id"
    assert callback_args[0][2] == single_resolve_responses


@pytest.mark.asyncio
@patch(
    "openg2p_spar_mapper_api.controllers.async_mapper_controller.AsyncResponseHelper.get_component"
)
@patch(
    "openg2p_spar_mapper_api.controllers.async_mapper_controller.RequestValidation.get_component"
)
@patch(
    "openg2p_spar_mapper_api.controllers.async_mapper_controller.MapperService.get_component"
)
async def test_unlink_async(
    mock_mapper_service_get_component,
    mock_request_validation_get_component,
    mock_async_response_helper_get_component,
):
    mock_mapper_service_instance = MagicMock()
    mock_mapper_service_instance.unlink = AsyncMock()
    mock_request_validation_instance = MagicMock()
    mock_mapper_service_get_component.return_value = mock_mapper_service_instance
    mock_request_validation_get_component.return_value = (
        mock_request_validation_instance
    )
    mock_async_response_helper_instance = MagicMock()
    expected_response = AsyncResponse(
        message=AsyncResponseMessage(
            correlation_id="1234",
            timestamp=datetime.utcnow().isoformat(),
            ack_status="ACK",
        )
    )
    mock_async_response_helper_instance.construct_success_async_response.return_value = (
        expected_response
    )
    mock_async_response_helper_get_component.return_value = (
        mock_async_response_helper_instance
    )

    controller = AsyncMapperController()

    mock_unlink_request = UnlinkRequest(
        header=RequestHeader(
            message_id="test_message_id",
            message_ts=datetime.utcnow().isoformat(),
            action="unlink",
            sender_id="test_sender",
            total_count=1,
        ),
        message=UnlinkRequestMessage(
            transaction_id="test_transaction_id",
            unlink_request=[
                SingleUnlinkRequest(
                    reference_id="test_ref",
                    timestamp=datetime.utcnow(),
                    id="test_id",
                    fa="test_fa",
                )
            ],
        ),
    )

    actual_response = await controller.unlink_async(mock_unlink_request)
    assert (
        actual_response == expected_response
    ), "The response did not match the expected response."
    assert actual_response.message.correlation_id == "1234"
    assert actual_response.message.ack_status == AsyncAck.ACK
    assert actual_response.message.timestamp == expected_response.message.timestamp


@pytest.mark.asyncio
@patch(
    "openg2p_spar_mapper_api.controllers.async_mapper_controller.AsyncResponseHelper.get_component"
)
@patch(
    "openg2p_spar_mapper_api.controllers.async_mapper_controller.RequestValidation.get_component"
)
@patch(
    "openg2p_spar_mapper_api.controllers.async_mapper_controller.MapperService.get_component"
)
async def test_handle_service_and_unlink_callback(
    mock_mapper_service_get_component,
    mock_request_validation_get_component,
    mock_async_response_helper_get_component,
):
    mock_mapper_service_instance = AsyncMock()
    mock_mapper_service_get_component.return_value = mock_mapper_service_instance
    single_unlink_responses = [
        SingleUnlinkResponse(
            reference_id="test_ref",
            timestamp=datetime.utcnow(),
            status=StatusEnum.succ,
            locale="en",
        )
    ]
    mock_mapper_service_instance.unlink.return_value = single_unlink_responses

    mock_request_validation_instance = AsyncMock()
    mock_request_validation_get_component.return_value = (
        mock_request_validation_instance
    )
    mock_async_response_helper_instance = AsyncMock()
    mock_async_response_helper_get_component.return_value = (
        mock_async_response_helper_instance
    )

    controller = AsyncMapperController()

    unlink_request = UnlinkRequest(
        header=RequestHeader(
            message_id="test_message_id",
            message_ts=datetime.utcnow().isoformat(),
            action="unlink",
            sender_id="test_sender",
            total_count=1,
        ),
        message=UnlinkRequestMessage(
            transaction_id="test_transaction_id",
            unlink_request=[
                SingleUnlinkRequest(
                    reference_id="test_ref",
                    timestamp=datetime.utcnow(),
                    id="test_id",
                    fa="test_fa",
                )
            ],
        ),
    )

    await controller.handle_service_and_unlink_callback(
        unlink_request, "correlation_id", "unlink"
    )

    mock_async_response_helper_instance.construct_success_async_callback_unlink_request.assert_called_once_with(
        unlink_request, "correlation_id", single_unlink_responses
    )

    callback_args = (
        mock_async_response_helper_instance.construct_success_async_callback_unlink_request.call_args
    )
    assert callback_args[0][0] == unlink_request
    assert callback_args[0][1] == "correlation_id"
    assert callback_args[0][2] == single_unlink_responses


@pytest.mark.asyncio
async def test_make_callback():
    async_call_back_request = AsyncCallbackRequest(
        header=AsyncCallbackRequestHeader(
            message_id="123",
            message_ts="2021-05-01T12:00:00Z",
            action="test_action",
            status=StatusEnum.succ,
        ),
        message={"key": "value"},
    )

    url = "http://test.com/callback"
    url_suffix = "/suffix"

    with patch(
        "openg2p_spar_mapper_api.controllers.async_mapper_controller.httpx.post"
    ) as mock_post:
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        task = asyncio.ensure_future(
            AsyncMapperController.make_callback(
                async_call_back_request, url, url_suffix
            )
        )
        await task
        await asyncio.gather(
            *[t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        )

        mock_post.assert_called_once_with(
            f"{url.rstrip('/')}{url_suffix}",
            headers={"content-type": "application/json"},
            content=async_call_back_request.model_dump_json(),
            timeout=10,
        )
