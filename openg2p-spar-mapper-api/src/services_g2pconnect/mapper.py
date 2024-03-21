import logging
from datetime import datetime

from openg2p_fastapi_common.context import dbengine
from openg2p_fastapi_common.service import BaseService
from openg2p_g2pconnect_common_lib.common.schemas import (
    SyncRequest,
    StatusEnum,
)
from openg2p_g2pconnect_common_lib.spar.schemas import (
    SingleLinkResponse,
    LinkRequest,
)
from sqlalchemy.ext.asyncio import async_sessionmaker

from ..config import Settings
from ..models.orm.id_fa_mapping import IdFaMapping
from ..services_g2pconnect.exceptions import LinkValidationException
from ..services_g2pconnect.id_fa_mapping_validations import IdFaMappingValidations

_config = Settings.get_config()
_logger = logging.getLogger(_config.logging_default_logger_name)


class MapperService(BaseService):
    async def link(self, request: SyncRequest) -> list[SingleLinkResponse]:
        session_maker = async_sessionmaker(dbengine.get(), expire_on_commit=False)

        async with session_maker() as session:
            linkRequest: LinkRequest = LinkRequest.model_validate(request.message)
            mappings_to_add = []
            single_link_responses: list[SingleLinkResponse] = []

            for single_link_request in linkRequest.link_request:

                try:
                    await IdFaMappingValidations.get_component().validate_link_request(
                        connection=session, single_link_request=single_link_request
                    )

                    mappings_to_add.append(
                        self.construct_id_fa_mapping(single_link_request)
                    )
                    single_link_responses.append(
                        self.construct_single_link_response_for_success(
                            single_link_request
                        )
                    )

                except LinkValidationException as e:
                    single_link_responses.append(
                        self.construct_single_link_response_for_failure(
                            single_link_request, e
                        )
                    )

            session.add_all(mappings_to_add)
            await session.commit()

        return single_link_responses

    @staticmethod
    def construct_id_fa_mapping(single_link_request):
        return IdFaMapping(
            id_value=single_link_request.id,
            fa_value=single_link_request.fa,
            name=single_link_request.name,
            phone=single_link_request.phone_number,
            additional_info=single_link_request.additional_info,
            active=True,
        )

    @staticmethod
    def construct_single_link_response_for_success(single_link_request):

        return SingleLinkResponse(
            reference_id=single_link_request.reference_id,
            timestamp=datetime.now(),
            fa=single_link_request.fa,
            status=StatusEnum.succ,
            status_reason_code=None,
            status_reason_message=None,
            additional_info=None,
            locale=single_link_request.locale,
        )

    @staticmethod
    def construct_single_link_response_for_failure(single_link_request, error):

        return SingleLinkResponse(
            reference_id=single_link_request.reference_id,
            timestamp=datetime.now(),
            fa=single_link_request.fa,
            status=StatusEnum.rjct,
            status_reason_code=error.validation_error_type,
            status_reason_message=error.message,
            additional_info=None,
            locale=single_link_request.locale,
        )

    # async def update(
    #     self, correlation_id: str, request: UpdateHttpRequest, make_callback=True
    # ):
    #     total_request_count = len(request.message.update_request)
    #     total_count = 0
    #     failure_count = 0

    #     response = UpdateCallbackHttpRequest(
    #         # TODO: dummy signature
    #         signature=request.signature,
    #         header=MsgCallbackHeader(
    #             message_id=request.header.message_id,
    #             message_ts=datetime.utcnow(),
    #             action="update",
    #             status=RequestStatusEnum.succ,
    #             total_count=total_request_count,
    #             sender_id=_config.callback_sender_id,
    #             receiver_id=request.header.sender_id,
    #             is_msg_encrypted=False,
    #         ),
    #         message=UpdateCallbackRequest(
    #             transaction_id=request.message.transaction_id,
    #             correlation_id=correlation_id,
    #             update_response=[],
    #         ),
    #     )
    #     session_maker = async_sessionmaker(dbengine.get(), expire_on_commit=False)
    #     async with session_maker() as session:
    #         for each_req in request.message.update_request:
    #             single_response = SingleUpdateCallbackRequest(
    #                 reference_id=each_req.reference_id,
    #                 timestamp=datetime.utcnow(),
    #                 id=each_req.id,
    #                 status=RequestStatusEnum.succ,
    #                 additional_info=each_req.additional_info,
    #                 locale=each_req.locale,
    #             )

    #             stmt = select(IdFaMapping).where(IdFaMapping.id_value == each_req.id)
    #             result = await session.execute(stmt)
    #             result = result.scalar()
    #             if result:
    #                 if each_req.fa:
    #                     result.fa_value = each_req.fa
    #                 if each_req.name:
    #                     result.name = each_req.name
    #                 if each_req.phone_number:
    #                     result.phone = each_req.phone_number
    #                 if each_req.additional_info:
    #                     addl_info_copy = (
    #                         result.additional_info.copy()
    #                         if result.additional_info
    #                         else []
    #                     )
    #                     addl_info_keys = [info["name"] for info in addl_info_copy]
    #                     for info in each_req.additional_info:
    #                         if info.name in addl_info_keys:
    #                             addl_info_copy[addl_info_keys.index(info.name)] = (
    #                                 info.model_dump()
    #                             )
    #                         else:
    #                             addl_info_copy.append(info.model_dump())
    #                     result.additional_info = addl_info_copy

    #                 await session.commit()
    #             else:
    #                 single_response.status = RequestStatusEnum.rjct
    #                 single_response.status_reason_code = (
    #                     UpdateRequestStatusReasonCode.rjct_id_invalid
    #                 )
    #                 single_response.status_reason_message = (
    #                     "Mapping doesnt exist against given ID. Use 'link' instead."
    #                 )
    #                 failure_count += 1

    #             total_count += 1
    #             response.message.update_response.append(single_response)
    #     response.header.completed_count = total_count
    #     if total_count == failure_count:
    #         response.header.status = RequestStatusEnum.rjct
    #         response.header.status_reason_code = (
    #             MsgHeaderStatusReasonCodeEnum.rjct_errors_too_many
    #         )
    #         response.header.status_reason_message = (
    #             "All requests in transaction failed."
    #         )
    #     if make_callback:
    #         self.make_callback(
    #             response, url=request.header.sender_uri, url_suffix="/on-update"
    #         )
    #     return response

    # async def resolve(
    #     self, correlation_id: str, request: ResolveHttpRequest, make_callback=True
    # ):
    #     total_request_count = len(request.message.resolve_request)
    #     total_count = 0
    #     failure_count = 0

    #     response = ResolveCallbackHttpRequest(
    #         # TODO: dummy signature
    #         signature=request.signature,
    #         header=MsgCallbackHeader(
    #             message_id=request.header.message_id,
    #             message_ts=datetime.utcnow(),
    #             action="resolve",
    #             status=RequestStatusEnum.succ,
    #             total_count=total_request_count,
    #             sender_id=_config.callback_sender_id,
    #             receiver_id=request.header.sender_id,
    #             is_msg_encrypted=False,
    #         ),
    #         message=ResolveCallbackRequest(
    #             transaction_id=request.message.transaction_id,
    #             correlation_id=correlation_id,
    #             resolve_response=[],
    #         ),
    #     )
    #     session_maker = async_sessionmaker(dbengine.get(), expire_on_commit=False)
    #     async with session_maker() as session:
    #         for each_req in request.message.resolve_request:
    #             single_response = SingleResolveCallbackRequest(
    #                 reference_id=each_req.reference_id,
    #                 timestamp=datetime.utcnow(),
    #                 status=RequestStatusEnum.succ,
    #                 status_reason_code=ResolveRequestStatusReasonCode.succ_id_active,
    #                 locale=each_req.locale,
    #             )

    #             stmt = None
    #             id_query = IdFaMapping.id_value == each_req.id
    #             fa_query = IdFaMapping.fa_value == each_req.fa
    #             if each_req.id and each_req.id.endswith("@") and ":" in each_req.id:
    #                 id_query = IdFaMapping.id_value.like(f"%{each_req.id}%")
    #             if each_req.fa and each_req.fa.endswith("@") and ":" in each_req.fa:
    #                 fa_query = IdFaMapping.fa_value.like(f"%{each_req.fa}%")

    #             if each_req.id and each_req.fa:
    #                 stmt = select(IdFaMapping).where(and_(id_query, fa_query))
    #             elif each_req.id:
    #                 stmt = select(IdFaMapping).where(id_query)
    #             elif each_req.fa:
    #                 stmt = select(IdFaMapping).where(fa_query)
    #             else:
    #                 single_response.status = RequestStatusEnum.rjct
    #                 single_response.status_reason_code = (
    #                     ResolveRequestStatusReasonCode.rjct_id_invalid
    #                 )
    #                 single_response.status_reason_message = (
    #                     "Neither ID (nor FA) is given."
    #                 )
    #                 failure_count += 1
    #                 continue
    #             result = await session.execute(stmt)
    #             result = result.scalar()
    #             if result:
    #                 if each_req.scope == ResolveScope.details:
    #                     single_response.fa = result.fa_value
    #                     single_response.id = result.id_value
    #                     single_response.additional_info = (
    #                         [
    #                             AdditionalInfo.model_validate(info)
    #                             for info in result.additional_info
    #                         ]
    #                         if result.additional_info
    #                         else None
    #                     )
    #                 elif each_req.scope == ResolveScope.yes_no:
    #                     # Do nothing as of now.
    #                     pass
    #                 if each_req.fa and not each_req.id:
    #                     single_response.status = RequestStatusEnum.succ
    #                     single_response.status_reason_code = (
    #                         ResolveRequestStatusReasonCode.succ_fa_active
    #                     )
    #                 else:
    #                     single_response.status = RequestStatusEnum.succ
    #                     single_response.status_reason_code = (
    #                         ResolveRequestStatusReasonCode.succ_id_active
    #                     )
    #             else:
    #                 single_response.status = RequestStatusEnum.succ
    #                 if each_req.id and each_req.fa:
    #                     single_response.status_reason_code = (
    #                         ResolveRequestStatusReasonCode.succ_fa_not_linked_to_id
    #                     )
    #                     single_response.status_reason_message = (
    #                         "No mapping found for given FA and ID combination."
    #                     )
    #                 elif each_req.fa:
    #                     single_response.status_reason_code = (
    #                         ResolveRequestStatusReasonCode.succ_fa_not_found
    #                     )
    #                     single_response.status_reason_message = (
    #                         "Mapping not found against given FA."
    #                     )
    #                 else:
    #                     single_response.status_reason_code = (
    #                         ResolveRequestStatusReasonCode.succ_id_not_found
    #                     )
    #                     single_response.status_reason_message = (
    #                         "Mapping not found against given ID."
    #                     )

    #             total_count += 1
    #             response.message.resolve_response.append(single_response)
    #     response.header.completed_count = total_count
    #     if total_count == failure_count:
    #         response.header.status = RequestStatusEnum.rjct
    #         response.header.status_reason_code = (
    #             MsgHeaderStatusReasonCodeEnum.rjct_errors_too_many
    #         )
    #         response.header.status_reason_message = (
    #             "All requests in transaction failed."
    #         )
    #     if make_callback:
    #         self.make_callback(
    #             response, url=request.header.sender_uri, url_suffix="/on-resolve"
    #         )
    #     return response

    # def make_callback(self, response: BaseModel, url=None, url_suffix=None):
    #     _logger.info("Make Callback Response json: %s", response.model_dump_json())
    #     if not (url or _config.default_callback_url):
    #         return
    #     elif not url:
    #         url = _config.default_callback_url

    #     asyncio.create_task(self._callback(response, url=url, url_suffix=url_suffix))

    # async def _callback(self, response: BaseModel, url, url_suffix=None):
    #     res = httpx.post(
    #         f"{url.rstrip('/')}{url_suffix}",
    #         headers={"content-type": "application/json"},
    #         content=response.model_dump_json(),
    #         timeout=_config.default_callback_timeout,
    #     )
    #     _logger.debug("Mapper callback Response:  %s", res.content)
    #     res.raise_for_status()
