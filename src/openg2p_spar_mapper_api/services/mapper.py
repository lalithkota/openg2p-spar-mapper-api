import logging
from datetime import datetime

from openg2p_fastapi_common.context import dbengine
from openg2p_fastapi_common.service import BaseService
from openg2p_g2pconnect_common_lib.schemas import StatusEnum
from openg2p_g2pconnect_mapper_lib.schemas import (
    LinkRequest,
    LinkRequestMessage,
    LinkStatusReasonCode,
    ResolveRequest,
    ResolveRequestMessage,
    ResolveScope,
    ResolveStatusReasonCode,
    SingleLinkResponse,
    SingleResolveRequest,
    SingleResolveResponse,
    SingleUnlinkResponse,
    SingleUpdateRequest,
    SingleUpdateResponse,
    UnlinkRequest,
    UnlinkRequestMessage,
    UpdateRequest,
    UpdateRequestMessage,
    UpdateStatusReasonCode,
)
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import async_sessionmaker

from ..config import Settings
from ..models import IdFaMapping
from ..services.exceptions import (
    LinkValidationException,
    ResolveValidationException,
    UnlinkValidationException,
    UpdateValidationException,
)
from ..services.id_fa_mapping_validations import IdFaMappingValidations

_config = Settings.get_config()
_logger = logging.getLogger(_config.logging_default_logger_name)


class MapperService(BaseService):
    async def link(self, link_request: LinkRequest):
        session_maker = async_sessionmaker(dbengine.get(), expire_on_commit=False)
        async with session_maker() as session:
            link_request_message: LinkRequestMessage = link_request.message
            mappings_to_add = []
            single_link_responses: list[SingleLinkResponse] = []

            for single_link_request in link_request_message.link_request:
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
                    LinkValidationException(
                        message="Duplicate ID exists. Use 'update' instead.",
                        status=StatusEnum.rjct,
                        validation_error_type=LinkStatusReasonCode.rjct_id_invalid,
                    )
                    single_link_responses.append(
                        self.construct_single_link_response_for_failure(
                            single_link_request, e
                        )
                    )
        session.add_all(mappings_to_add)
        await session.commit()
        return single_link_responses

    def construct_id_fa_mapping(self, single_link_request):
        return IdFaMapping(
            id_value=single_link_request.id,
            fa_value=single_link_request.fa,
            name=single_link_request.name,
            phone=single_link_request.phone_number,
            additional_info=single_link_request.additional_info,
            active=True,
        )

    def construct_single_link_response_for_success(self, single_link_request):
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

    def construct_single_link_response_for_failure(self, single_link_request, error):
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

    async def update(self, update_request: UpdateRequest):
        session_maker = async_sessionmaker(dbengine.get(), expire_on_commit=False)
        async with session_maker() as session:
            update_request_message: UpdateRequestMessage = update_request.message
            single_update_responses: list[SingleUpdateResponse] = []

            for single_update_request in update_request_message.update_request:
                try:
                    await IdFaMappingValidations.get_component().validate_update_request(
                        connection=session, single_update_request=single_update_request
                    )

                    single_update_responses.append(
                        self.construct_single_update_response_for_success(
                            single_update_request
                        )
                    )

                    await self.update_mapping(session, single_update_request)

                except UpdateValidationException as e:
                    UpdateValidationException(
                        message="Mapping doesn't exist against the given ID.",
                        status=StatusEnum.rjct,
                        validation_error_type=UpdateStatusReasonCode.rjct_id_invalid,
                    )
                    single_update_responses.append(
                        self.construct_single_update_response_for_failure(
                            single_update_request, e
                        )
                    )

        await session.commit()

        return single_update_responses

    async def update_mapping(self, session, single_update_request):
        single_update_request: SingleUpdateRequest = SingleUpdateRequest.model_validate(
            single_update_request
        )
        single_response = self.construct_single_update_response_for_success(
            single_update_request
        )
        result = await session.execute(
            select(IdFaMapping).where(IdFaMapping.id_value == single_update_request.id)
        )
        result = result.scalar()

        if result:
            if single_update_request.fa:
                result.fa_value = single_update_request.fa
            if single_update_request.name:
                result.name = single_update_request.name
            if single_update_request.phone_number:
                result.phone = single_update_request.phone_number
            if single_update_request.additional_info:
                addl_info_copy = (
                    result.additional_info.copy() if result.additional_info else []
                )
                result.additional_info = addl_info_copy
        else:
            single_response.status = StatusEnum.rjct
            single_response.status_reason_code = UpdateStatusReasonCode.rjct_id_invalid
            single_response.status_reason_message = (
                "Mapping doesnt exist against given ID. Use 'link' instead."
            )
        await session.commit()

    def construct_single_update_response_for_success(self, single_update_request):
        return SingleUpdateResponse(
            id=single_update_request.id,
            reference_id=single_update_request.reference_id,
            timestamp=datetime.now(),
            status=StatusEnum.succ,
            status_reason_code=None,
            status_reason_message=None,
            additional_info=None,
            locale=single_update_request.locale,
        )

    def construct_single_update_response_for_failure(
        self, single_update_request, error
    ):
        return SingleUpdateResponse(
            reference_id=single_update_request.reference_id,
            timestamp=datetime.now(),
            fa=single_update_request.fa,
            status=StatusEnum.rjct,
            status_reason_code=error.validation_error_type,
            status_reason_message=error.message,
            additional_info=None,
            locale=single_update_request.locale,
        )

    async def resolve(self, resolve_request: ResolveRequest):
        session_maker = async_sessionmaker(dbengine.get(), expire_on_commit=False)
        async with session_maker() as session:
            resolve_request_message: ResolveRequestMessage = resolve_request.message

            single_resolve_responses: list[SingleResolveResponse] = []

            for single_resolve_request in resolve_request_message.resolve_request:
                try:
                    await IdFaMappingValidations.get_component().validate_resolve_request(
                        connection=session,
                        single_resolve_request=single_resolve_request,
                    )
                    single_resolve_request: SingleResolveRequest = (
                        SingleResolveRequest.model_validate(single_resolve_request)
                    )
                    stmt, result = await self.construct_query(
                        session, single_resolve_request
                    )
                    single_resolve_response = self.construct_single_resolve(
                        single_resolve_request, result
                    )

                    single_resolve_responses.append(
                        self.construct_single_resolve_response_for_success(
                            single_resolve_response
                        )
                    )
                except ResolveValidationException as e:
                    single_resolve_responses.append(
                        self.construct_single_resolve_response_for_failure(
                            single_resolve_request, e
                        )
                    )
        await session.commit()
        return single_resolve_responses

    def construct_single_resolve(
        self, single_resolve_request, result
    ) -> SingleResolveResponse:
        single_response = self.construct_single_resolve_response_for_success(
            single_resolve_request
        )
        if result:
            if single_resolve_request.scope == ResolveScope.details:
                single_response.status = StatusEnum.succ
                single_response.additional_info = result.additional_info
                single_response.fa = result.fa_value
                single_response.id = result.id_value
                single_response.status_reason_code = (
                    ResolveStatusReasonCode.succ_id_active
                )
            else:
                single_response.status = StatusEnum.succ
                single_response.status_reason_code = (
                    ResolveStatusReasonCode.succ_id_active
                )
        else:
            single_response.status = StatusEnum.succ
            single_response.status_reason_code = (
                ResolveStatusReasonCode.succ_id_not_found
            )
            single_response.status_reason_message = (
                "Mapping not found against given ID."
            )
        return single_response

    async def construct_query(self, session, single_resolve_request):
        self.construct_single_resolve_response_for_success(single_resolve_request)
        stmt = None
        id_query = IdFaMapping.id_value == single_resolve_request.id
        stmt = select(IdFaMapping).where(id_query)
        result = await session.execute(stmt)
        result = result.scalar()
        return stmt, result

    def construct_single_resolve_response_for_success(self, single_resolve_request):
        return SingleResolveResponse(
            id=single_resolve_request.id,
            reference_id=single_resolve_request.reference_id,
            timestamp=datetime.now(),
            fa=single_resolve_request.fa,
            status=StatusEnum.succ,
            status_reason_code=None,
            status_reason_message=None,
            additional_info=single_resolve_request.additional_info,
            locale=single_resolve_request.locale,
        )

    def construct_single_resolve_response_for_failure(
        self, single_resolve_request, error
    ):
        return SingleResolveResponse(
            reference_id=single_resolve_request.reference_id,
            timestamp=datetime.now(),
            fa=single_resolve_request.fa,
            status=error.status,
            status_reason_code=error.validation_error_type,
            status_reason_message=error.message,
            additional_info=None,
            locale=single_resolve_request.locale,
        )

    async def unlink(self, unlink_request: UnlinkRequest):
        session_maker = async_sessionmaker(dbengine.get(), expire_on_commit=False)
        async with session_maker() as session:
            unlink_request_message: UnlinkRequestMessage = unlink_request.message
            single_unlink_responses: list[SingleUnlinkResponse] = []
            for single_unlink_request in unlink_request_message.unlink_request:
                try:
                    await IdFaMappingValidations.get_component().validate_unlink_request(
                        connection=session, single_unlink_request=single_unlink_request
                    )
                    await session.execute(
                        delete(IdFaMapping).where(
                            IdFaMapping.id_value == single_unlink_request.id
                        )
                    )
                    single_unlink_responses.append(
                        self.construct_single_unlink_response_for_success(
                            single_unlink_request
                        )
                    )
                except UnlinkValidationException as e:
                    single_unlink_responses.append(
                        self.construct_single_unlink_response_for_failure(
                            single_unlink_request, e
                        )
                    )
            await session.commit()
        return single_unlink_responses

    def construct_single_unlink_response_for_success(self, single_unlink_request):
        return SingleUnlinkResponse(
            reference_id=single_unlink_request.reference_id,
            timestamp=datetime.now(),
            fa=single_unlink_request.fa,
            status=StatusEnum.succ,
            status_reason_code=None,
            status_reason_message=None,
            additional_info=None,
            locale=single_unlink_request.locale,
        )

    def construct_single_unlink_response_for_failure(
        self, single_unlink_request, error
    ):
        return SingleUnlinkResponse(
            reference_id=single_unlink_request.reference_id,
            timestamp=datetime.now(),
            fa=single_unlink_request.fa,
            status=StatusEnum.rjct,
            status_reason_code=error.validation_error_type,
            status_reason_message=error.message,
            additional_info=None,
            locale=single_unlink_request.locale,
        )
