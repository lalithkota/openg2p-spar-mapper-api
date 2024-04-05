# import asyncio
# import unittest
# from unittest.mock import MagicMock, patch
#
# from fastapi import Request
# from openg2p_spar_mapper_api.controllers.async_mapper_controller import (
#     AsyncMapperController,
# )
#
#
# class TestAsyncMapperController(unittest.TestCase):
#     def setUp(self) -> None:
#         self.mock_request = MagicMock(spec=Request)
#         self.mock_request_validation = patch(
#             "openg2p_spar_mapper_api.controllers.async_mapper_controller.RequestValidation"
#         ).start()
#         self.mock_response_helper = patch(
#             "openg2p_spar_mapper_api.controllers.async_mapper_controller.AsyncResponseHelper"
#         ).start()
#
#         self.mock_request_validation.validate_request.side_effect = None
#         self.mock_request_validation.validate_link_request_header.side_effect = None
#
#         self.mock_mapper_service = MagicMock()
#         self.controller = AsyncMapperController()
#
#     def tearDown(self) -> None:
#         patch.stopall()
#
#     def test_link_async(self):
#         async def run_test():
#             response = await self.controller.link_async(self.mock_request)
#             self.assertIsNotNone(response)
#             # self.mock_response_helper.get_component().construct_error_async_response.assert_not_called()
#             self.mock_response_helper.get_component().construct_success_async_response.assert_called_once_with(
#                 self.mock_request, 123555
#             )
#
#             asyncio.run(run_test())
#
#     # def test_update_sync(self):
#     #     async def run_test():
#     #         response = await self.controller.update_async(self.mock_request)
#     #         self.assertIsNotNone(response)
#     #         # self.mock_response_helper.get_component().construct_error_async_response.assert_not_called()
#     #         self.mock_response_helper.get_component().construct_success_async_response.assert_called_once_with(
#     #             self.mock_request, 123555
#     #         )
#
#     #         asyncio.run(run_test())
#
#     # def test_resolve_sync(self):
#     #     async def run_test():
#     #         response = await self.controller.resolve_async(self.mock_request)
#     #         self.assertIsNotNone(response)
#     #         # self.mock_response_helper.get_component().construct_error_async_response.assert_not_called()
#     #         self.mock_response_helper.get_component().construct_success_async_response.assert_called_once_with(
#     #             self.mock_request, 123555
#     #         )
#     #         asyncio.run(run_test())
#
#     # def test_unlink_sync(self):
#     #     async def run_test():
#     #         response = await self.controller.unlink_async(self.mock_request)
#     #         self.assertIsNotNone(response)
#     #         # self.mock_response_helper.get_component().construct_error_async_response.assert_not_called()
#     #         self.mock_response_helper.get_component().construct_success_async_response.assert_called_once_with(
#     #             self.mock_request,123555
#     #         )
#
#     #         asyncio.run(run_test())
