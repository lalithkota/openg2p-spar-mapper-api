from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from openg2p_g2pconnect_common_lib.common.schemas import (
    RequestHeader,
    StatusEnum,
    SyncResponseHeader,
    SyncResponseStatusReasonCodeEnum,
)
from openg2p_g2pconnect_common_lib.mapper.schemas import (
    LinkRequest,
    LinkRequestMessage,
    LinkResponse,
    LinkResponseMessage,
    SingleLinkRequest,
    SingleLinkResponse,
)
from openg2p_spar_mapper_api.controllers.sync_mapper_controller import (
    SyncMapperController,
)
from openg2p_spar_mapper_api.services import (
    RequestValidation,
    RequestValidationException,
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

    mock_error_response = LinkResponse(
        header=SyncResponseHeader(
            message_id="error_message_id",
            message_ts=datetime.now().isoformat(),
            action="error_action",
            status=StatusEnum.rjct,
            status_reason_code=SyncResponseStatusReasonCodeEnum.rjct_action_not_supported.value,
            status_reason_message="Validation error",
        ),
        message=LinkResponseMessage(
            transaction_id="error_trans_id",
            link_response=[],
        ),
    )

    # Mock SyncResponseHelper for error scenario
    response_helper_mock.construct_error_sync_response.return_value = (
        mock_error_response
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
    response = await controller.link_sync(mock_link_request)
    assert response.header.status == StatusEnum.succ
    assert response.message.transaction_id == "trans_id"
    controller.mapper_service.link.assert_called_once_with(mock_link_request)


@pytest.mark.asyncio
async def test_link_sync_validation_error(setup_controller):
    controller, mock_link_request = setup_controller
    validation_error = RequestValidationException(
        code=SyncResponseStatusReasonCodeEnum.rjct_action_not_supported,
        message="Validation error",
    )
    with patch.object(
        RequestValidation.get_component(),
        "validate_request",
        side_effect=validation_error,
    ), patch.object(
        RequestValidation.get_component(),
        "validate_link_request_header",
        side_effect=validation_error,
    ):
        response = await controller.link_sync(mock_link_request)
        assert response.header.status == StatusEnum.rjct
        assert validation_error.message in response.header.status_reason_message
        controller.mapper_service.link.assert_not_called()
