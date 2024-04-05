import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch, MagicMock
from openg2p_g2pconnect_common_lib.mapper.schemas import (
    LinkRequest,
    LinkResponse,
    SingleLinkResponse,
    LinkResponseMessage,
    LinkRequestMessage,
    SingleLinkRequest,
)
from openg2p_g2pconnect_common_lib.common.schemas import (
    StatusEnum,
    SyncResponseHeader,
    RequestHeader,
    SyncResponseStatusReasonCodeEnum,
)

from openg2p_spar_mapper_api.controllers.sync_mapper_controller import (
    SyncMapperController,
)
from openg2p_spar_mapper_api.services import (
    RequestValidationException,
    RequestValidation,
)


@pytest.fixture(autouse=True)
def setup_controller():
    controller = SyncMapperController()
    controller.mapper_service = AsyncMock()

    request_validation_mock = MagicMock()
    request_validation_mock.validate_request = MagicMock(return_value=True)
    request_validation_mock.validate_link_request_header = MagicMock(return_value=True)

    mock_link_response = LinkResponse(
        header=SyncResponseHeader(
            message_id="test_message_id",
            message_ts=datetime.now().isoformat(),
            action="link",
            status=StatusEnum.succ,
            status_reason_code=None,
            status_reason_message="Success",
        ),
        message=LinkResponseMessage(
            transaction_id="trans_id",
            link_response=[
                SingleLinkResponse(
                    reference_id="test_ref",
                    timestamp=datetime.now(),
                    status=StatusEnum.succ,
                    additional_info=[{}],
                    fa="test_fa",
                    status_reason_code=None,
                    status_reason_message="Test message",
                    locale="en",
                )
            ],
        ),
    )

    response_helper_mock = MagicMock()
    response_helper_mock.construct_success_sync_link_response.return_value = (
        mock_link_response
    )

    with patch(
        "openg2p_spar_mapper_api.services.RequestValidation.get_component",
        return_value=request_validation_mock,
    ), patch(
        "openg2p_spar_mapper_api.services.SyncResponseHelper.get_component",
        return_value=response_helper_mock,
    ):
        mock_link_request = LinkRequest(
            header=RequestHeader(
                message_id="test_message_id",
                message_ts=datetime.now().isoformat(),
                action="test_action",
                sender_id="test_sender",
                total_count=1,
            ),
            message=LinkRequestMessage(
                transaction_id="test_transaction_id",
                link_request=[
                    SingleLinkRequest(
                        reference_id="test_ref",
                        timestamp=datetime.now(),
                        id="test_id",
                        fa="test_fa",
                    )
                ],
            ),
        )
        yield controller, mock_link_request


@pytest.mark.asyncio
async def test_link_sync_success(setup_controller):
    controller, mock_link_request = setup_controller
    assert controller is not None

    valid_single_link_response = SingleLinkResponse(
        reference_id="test_ref",
        timestamp=datetime.now(),
        status=StatusEnum.succ,
        additional_info=[{}],
    )

    valid_link_response_message = LinkResponseMessage(
        transaction_id="trans_id",
        link_response=[valid_single_link_response],
    )

    valid_sync_response_header = SyncResponseHeader(
        message_id="message_id",
        message_ts=datetime.now().isoformat(),
        action="link",
        status=StatusEnum.succ,
        status_reason_code=None,
        status_reason_message="Success",
    )

    valid_link_response = LinkResponse(
        header=valid_sync_response_header,
        message=valid_link_response_message,
    )

    # Mock the service call to return the constructed LinkResponse
    controller.mapper_service.link.return_value = valid_link_response

    # Call the link_sync method and verify the response
    response = await controller.link_sync(mock_link_request)

    assert response.header.status == StatusEnum.succ
    assert response.message.transaction_id == "trans_id"
    controller.mapper_service.link.assert_called_once_with(mock_link_request)
