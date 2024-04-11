from unittest.mock import patch, AsyncMock, MagicMock
import pytest
from openg2p_spar_mapper_api.controllers.async_mapper_controller import (
    AsyncMapperController,
)
from openg2p_g2pconnect_common_lib.common.schemas import (
    AsyncResponse,
    AsyncResponseMessage,
    RequestHeader,
    AsyncAck,
)
from openg2p_g2pconnect_common_lib.mapper.schemas import (
    LinkRequest,
    LinkRequestMessage,
    SingleLinkRequest,
)
from datetime import datetime


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
