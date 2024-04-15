from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from openg2p_g2pconnect_common_lib.schemas import (
    RequestHeader,
    StatusEnum,
    SyncResponseHeader,
    SyncResponseStatusReasonCodeEnum,
)
from openg2p_g2pconnect_mapper_lib.schemas import (
    LinkRequest,
    LinkRequestMessage,
    LinkResponse,
    LinkResponseMessage,
    SingleLinkRequest,
    SingleLinkResponse,
)
from openg2p_g2pconnect_mapper_lib.schemas.resolve import (
    ResolveRequest,
    ResolveRequestMessage,
    ResolveResponse,
    ResolveResponseMessage,
    SingleResolveRequest,
    SingleResolveResponse,
)
from openg2p_g2pconnect_mapper_lib.schemas.unlink import (
    SingleUnlinkRequest,
    SingleUnlinkResponse,
    UnlinkRequest,
    UnlinkRequestMessage,
    UnlinkResponse,
    UnlinkResponseMessage,
)
from openg2p_g2pconnect_mapper_lib.schemas.update import (
    SingleUpdateRequest,
    SingleUpdateResponse,
    UpdateRequest,
    UpdateRequestMessage,
    UpdateResponse,
    UpdateResponseMessage,
)
from openg2p_spar_mapper_api.controllers.sync_mapper_controller import (
    SyncMapperController,
)
from openg2p_spar_mapper_api.services import (
    RequestValidation,
    RequestValidationException,
)


@pytest.fixture
def setup_link_controller():
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
    response_helper_link_mock = MagicMock()

    response_helper_link_mock.construct_success_sync_link_response.return_value = (
        mock_link_response
    )

    mock_error_link_response = LinkResponse(
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
    response_helper_link_mock.construct_error_sync_response.return_value = (
        mock_error_link_response
    )
    with patch(
        "openg2p_spar_mapper_api.services.RequestValidation.get_component",
        return_value=request_validation_mock,
    ), patch(
        "openg2p_spar_mapper_api.services.SyncResponseHelper.get_component",
        return_value=response_helper_link_mock,
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


@pytest.fixture
def setup_update_controller():
    controller = SyncMapperController()
    controller.mapper_service = AsyncMock()

    request_validation_mock = MagicMock()
    request_validation_mock.validate_request = MagicMock(return_value=True)
    request_validation_mock.validate_update_request_header = MagicMock(
        return_value=True
    )

    mock_update_response = UpdateResponse(
        header=SyncResponseHeader(
            message_id="test_message_id",
            message_ts=datetime.now().isoformat(),
            action="update",
            status=StatusEnum.succ,
            status_reason_code=None,
            status_reason_message="Success",
        ),
        message=UpdateResponseMessage(
            transaction_id="trans_id",
            update_response=[
                SingleUpdateResponse(
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

    response_helper_update_mock = MagicMock()

    response_helper_update_mock.construct_success_sync_update_response.return_value = (
        mock_update_response
    )

    mock_error_update_response = UpdateResponse(
        header=SyncResponseHeader(
            message_id="error_message_id",
            message_ts=datetime.now().isoformat(),
            action="error_action",
            status=StatusEnum.rjct,
            status_reason_code=SyncResponseStatusReasonCodeEnum.rjct_action_not_supported.value,
            status_reason_message="Validation error",
        ),
        message=UpdateResponseMessage(
            transaction_id="error_trans_id",
            update_response=[],
        ),
    )

    response_helper_update_mock.construct_error_sync_response.return_value = (
        mock_error_update_response
    )

    with patch(
        "openg2p_spar_mapper_api.services.RequestValidation.get_component",
        return_value=request_validation_mock,
    ), patch(
        "openg2p_spar_mapper_api.services.SyncResponseHelper.get_component",
        return_value=response_helper_update_mock,
    ):
        mock_update_request = UpdateRequest(
            header=RequestHeader(
                message_id="test_message_id",
                message_ts=datetime.now().isoformat(),
                action="test_action",
                sender_id="test_sender",
                total_count=1,
            ),
            message=UpdateRequestMessage(
                transaction_id="test_transaction_id",
                update_request=[
                    SingleUpdateRequest(
                        reference_id="test_ref",
                        timestamp=datetime.now(),
                        id="test_id",
                        fa="test_fa",
                    )
                ],
            ),
        )
        yield controller, mock_update_request


@pytest.fixture
def setup_resolve_controller():
    controller = SyncMapperController()
    controller.mapper_service = AsyncMock()

    request_validation_mock = MagicMock()
    request_validation_mock.validate_request = MagicMock(return_value=True)
    request_validation_mock.validate_resolve_request_header = MagicMock(
        return_value=True
    )

    mock_resolve_response = ResolveResponse(
        header=SyncResponseHeader(
            message_id="test_message_id",
            message_ts=datetime.now().isoformat(),
            action="resolve",
            status=StatusEnum.succ,
            status_reason_code=None,
            status_reason_message="Success",
        ),
        message=ResolveResponseMessage(
            transaction_id="trans_id",
            resolve_response=[
                SingleResolveResponse(
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

    response_helper_resolve_mock = MagicMock()

    response_helper_resolve_mock.construct_success_sync_resolve_response.return_value = (
        mock_resolve_response
    )

    mock_error_resolve_response = ResolveResponse(
        header=SyncResponseHeader(
            message_id="error_message_id",
            message_ts=datetime.now().isoformat(),
            action="error_action",
            status=StatusEnum.rjct,
            status_reason_code=SyncResponseStatusReasonCodeEnum.rjct_action_not_supported.value,
            status_reason_message="Validation error",
        ),
        message=ResolveResponseMessage(
            transaction_id="error_trans_id",
            resolve_response=[],
        ),
    )

    response_helper_resolve_mock.construct_error_sync_response.return_value = (
        mock_error_resolve_response
    )

    with patch(
        "openg2p_spar_mapper_api.services.RequestValidation.get_component",
        return_value=request_validation_mock,
    ), patch(
        "openg2p_spar_mapper_api.services.SyncResponseHelper.get_component",
        return_value=response_helper_resolve_mock,
    ):
        mock_resolve_request = ResolveRequest(
            header=RequestHeader(
                message_id="test_message_id",
                message_ts=datetime.now().isoformat(),
                action="test_action",
                sender_id="test_sender",
                total_count=1,
            ),
            message=ResolveRequestMessage(
                transaction_id="test_transaction_id",
                resolve_request=[
                    SingleResolveRequest(
                        reference_id="test_ref",
                        timestamp=datetime.now(),
                        id="test_id",
                        fa="test_fa",
                    )
                ],
            ),
        )
        yield controller, mock_resolve_request


@pytest.fixture
def setup_unlink_controller():
    controller = SyncMapperController()
    controller.mapper_service = AsyncMock()

    request_validation_mock = MagicMock()
    request_validation_mock.validate_request = MagicMock(return_value=True)
    request_validation_mock.validate_link_request_header = MagicMock(return_value=True)
    request_validation_mock.validate_update_request_header = MagicMock(
        return_value=True
    )
    request_validation_mock.validate_resolve_request_header = MagicMock(
        return_value=True
    )
    request_validation_mock.validate_unlink_request_header = MagicMock(
        return_value=True
    )

    mock_unlink_response = UnlinkResponse(
        header=SyncResponseHeader(
            message_id="test_message_id",
            message_ts=datetime.now().isoformat(),
            action="unlink",
            status=StatusEnum.succ,
            status_reason_code=None,
            status_reason_message="Success",
        ),
        message=UnlinkResponseMessage(
            transaction_id="trans_id",
            unlink_response=[
                SingleUnlinkResponse(
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

    response_helper_unlink_mock = MagicMock()

    response_helper_unlink_mock.construct_success_sync_unlink_response.return_value = (
        mock_unlink_response
    )

    mock_error_unlink_response = UnlinkResponse(
        header=SyncResponseHeader(
            message_id="error_message_id",
            message_ts=datetime.now().isoformat(),
            action="error_action",
            status=StatusEnum.rjct,
            status_reason_code=SyncResponseStatusReasonCodeEnum.rjct_action_not_supported.value,
            status_reason_message="Validation error",
        ),
        message=UnlinkResponseMessage(
            transaction_id="error_trans_id",
            unlink_response=[],
        ),
    )

    response_helper_unlink_mock.construct_error_sync_response.return_value = (
        mock_error_unlink_response
    )

    with patch(
        "openg2p_spar_mapper_api.services.RequestValidation.get_component",
        return_value=request_validation_mock,
    ), patch(
        "openg2p_spar_mapper_api.services.SyncResponseHelper.get_component",
        return_value=response_helper_unlink_mock,
    ):
        mock_unlink_request = UnlinkRequest(
            header=RequestHeader(
                message_id="test_message_id",
                message_ts=datetime.now().isoformat(),
                action="test_action",
                sender_id="test_sender",
                total_count=1,
            ),
            message=UnlinkRequestMessage(
                transaction_id="test_transaction_id",
                unlink_request=[
                    SingleUnlinkRequest(
                        reference_id="test_ref",
                        timestamp=datetime.now(),
                        id="test_id",
                        fa="test_fa",
                    )
                ],
            ),
        )
        yield controller, mock_unlink_request


@pytest.mark.asyncio
async def test_link_sync_success(setup_link_controller):
    controller, mock_link_request = setup_link_controller
    assert controller is not None
    response = await controller.link_sync(mock_link_request)
    assert response.header.status == StatusEnum.succ
    assert response.message.transaction_id == "trans_id"
    controller.mapper_service.link.assert_called_once_with(mock_link_request)


@pytest.mark.asyncio
async def test_update_sync_success(setup_update_controller):
    controller, mock_update_request = setup_update_controller
    assert controller is not None
    response = await controller.update_sync(mock_update_request)
    assert response.header.status == StatusEnum.succ
    assert response.message.transaction_id == "trans_id"
    controller.mapper_service.update.assert_called_once_with(mock_update_request)


@pytest.mark.asyncio
async def test_resolve_sync_success(setup_resolve_controller):
    controller, mock_resolve_request = setup_resolve_controller
    assert controller is not None
    response = await controller.resolve_sync(mock_resolve_request)
    assert response.header.status == StatusEnum.succ
    assert response.message.transaction_id == "trans_id"
    controller.mapper_service.resolve.assert_called_once_with(mock_resolve_request)


@pytest.mark.asyncio
async def test_unlink_sync_success(setup_unlink_controller):
    controller, mock_unlink_request = setup_unlink_controller
    assert controller is not None
    response = await controller.unlink_sync(mock_unlink_request)
    assert response.header.status == StatusEnum.succ
    assert response.message.transaction_id == "trans_id"
    controller.mapper_service.unlink.assert_called_once_with(mock_unlink_request)


@pytest.mark.asyncio
async def test_link_sync_validation_error(setup_link_controller):
    controller, mock_link_request = setup_link_controller
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


@pytest.mark.asyncio
async def test_update_sync_validation_error(setup_update_controller):
    controller, mock_update_request = setup_update_controller
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
        "validate_update_request_header",
        side_effect=validation_error,
    ):
        response = await controller.update_sync(mock_update_request)
        assert response.header.status == StatusEnum.rjct
        assert validation_error.message in response.header.status_reason_message
        controller.mapper_service.update.assert_not_called()


@pytest.mark.asyncio
async def test_resolve_sync_validation_error(setup_resolve_controller):
    controller, mock_resolve_request = setup_resolve_controller
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
        "validate_resolve_request_header",
        side_effect=validation_error,
    ):
        response = await controller.resolve_sync(mock_resolve_request)
        assert response.header.status == StatusEnum.rjct
        assert validation_error.message in response.header.status_reason_message
        controller.mapper_service.resolve.assert_not_called()


@pytest.mark.asyncio
async def test_unlink_sync_validation_error(setup_unlink_controller):
    controller, mock_unlink_request = setup_unlink_controller
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
        "validate_unlink_request_header",
        side_effect=validation_error,
    ):
        response = await controller.unlink_sync(mock_unlink_request)
        assert response.header.status == StatusEnum.rjct
        assert validation_error.message in response.header.status_reason_message
        controller.mapper_service.unlink.assert_not_called()
