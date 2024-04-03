import asyncio
import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

from fastapi import Request
from openg2p_g2pconnect_common_lib.common.schemas.status_codes import StatusEnum
from openg2p_g2pconnect_common_lib.mapper.schemas.link import SingleLinkResponse
from openg2p_spar_mapper_api.controllers.sync_mapper_controller import (
    SyncMapperController,
)


class TestSyncMapperController(unittest.TestCase):
    def setUp(self) -> None:
        self.mock_request = MagicMock(spec=Request)
        self.mock_request_validation = patch(
            "openg2p_spar_mapper_api.controllers.sync_mapper_controller.RequestValidation"
        ).start()
        self.mock_response_helper = patch(
            "openg2p_spar_mapper_api.controllers.sync_mapper_controller.SyncResponseHelper"
        ).start()

        self.mock_request_validation.validate_request.side_effect = None
        self.mock_request_validation.validate_link_request_header.side_effect = None

        self.mock_link_response = SingleLinkResponse(
            reference_id="string",
            timestamp=datetime.now(),
            status=StatusEnum.succ,
            additional_info=[{}],
            locale="eng",
            id="string",
            fa="string",
            name="string",
            phone_number="string",
        )

        self.mock_mapper_service = MagicMock()
        self.controller = SyncMapperController()
        self.controller.mapper_service = self.mock_mapper_service
        self.controller.mapper_service.link.return_value = [self.mock_link_response]

    def tearDown(self) -> None:
        patch.stopall()

    def test_link_sync(self):
        async def run_test():
            response = await self.controller.link_sync(self.mock_request)
            self.mock_mapper_service.link.assert_called_once()
            self.assertIsNotNone(response)
            self.mock_response_helper.get_component().construct_error_sync_response.assert_not_called()
            self.mock_response_helper.get_component().construct_success_sync_link_response.assert_called_once_with(
                self.mock_request, [self.mock_link_response]
            )

            asyncio.run(run_test())

    def test_update_sync(self):
        async def run_test():
            response = await self.controller.update_sync(self.mock_request)
            self.mock_mapper_service.update.assert_called_once()
            self.assertIsNotNone(response)
            self.mock_response_helper.get_component().construct_error_sync_response.assert_not_called()
            self.mock_response_helper.get_component().construct_success_sync_update_response.assert_called_once_with(
                self.mock_request, [self.mock_update_response]
            )

            asyncio.run(run_test())

    def test_resolve_sync(self):
        async def run_test():
            response = await self.controller.resolve_sync(self.mock_request)
            self.mock_mapper_service.resolve.assert_called_once()
            self.assertIsNotNone(response)
            self.mock_response_helper.get_component().construct_error_sync_response.assert_not_called()
            self.mock_response_helper.get_component().construct_success_sync_resolve_response.assert_called_once_with(
                self.mock_request, [self.mock_resolve_response]
            )

            asyncio.run(run_test())

    def test_unlink_sync(self):
        async def run_test():
            response = await self.controller.unlink_sync(self.mock_request)
            self.mock_mapper_service.unlink.assert_called_once()
            self.assertIsNotNone(response)
            self.mock_response_helper.get_component().construct_error_sync_response.assert_not_called()
            self.mock_response_helper.get_component().construct_success_sync_unlink_response.assert_called_once_with(
                self.mock_request, [self.mock_unlink_response]
            )

            asyncio.run(run_test())
