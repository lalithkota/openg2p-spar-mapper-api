import logging
from datetime import datetime

from openg2p_fastapi_common.context import dbengine
from openg2p_fastapi_common.service import BaseService
from openg2p_g2pconnect_common_lib.common.schemas import Request, StatusEnum
from openg2p_g2pconnect_common_lib.mapper.schemas import (
    LinkRequest,
    LinkStatusReasonCode,
    ResolveRequest,
    SingleLinkResponse,
    SingleResolveResponse,
    SingleUnlinkResponse,
    SingleUpdateResponse,
    UnlinkRequest,
    UnlinkStatusReasonCode,
    UpdateRequest,
    UpdateStatusReasonCode,
)
from openg2p_g2pconnect_common_lib.mapper.schemas.resolve import (
    ResolveScope,
    ResolveStatusReasonCode,
)
from sqlalchemy import and_, select
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
    async def link(self, request: Request):
        session_maker = async_sessionmaker(dbengine.get(), expire_on_commit=False)
        async with session_maker() as session:
            linkRequest: LinkRequest = LinkRequest.model_validate(request.message)
            mappings_to_add = []
            single_link_responses: list[SingleLinkResponse] = []

            for single_link_request in linkRequest.link_request:
                try:
                    await IdFaMappingValidations.get_component().validate_link_request(
                        connection=session, single_update_request=single_link_request
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

    async def update(self, request: Request):
        session_maker = async_sessionmaker(dbengine.get(), expire_on_commit=False)
        async with session_maker() as session:
            updateRequest: UpdateRequest = UpdateRequest.model_validate(request.message)
            single_update_responses: list[SingleUpdateResponse] = []

            for single_update_request in updateRequest.link_request:
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
                        message="Mapping doesnt exist against given ID. Use 'link' instead.",
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

    @staticmethod
    def construct_single_update_response_for_success(single_update_request):
        return SingleUpdateResponse(
            reference_id=single_update_request.reference_id,
            timestamp=datetime.now(),
            fa=single_update_request.fa,
            status=StatusEnum.succ,
            status_reason_code=None,
            status_reason_message=None,
            additional_info=None,
            locale=single_update_request.locale,
        )

    @staticmethod
    def construct_single_update_response_for_failure(single_update_request, error):
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

    @staticmethod
    async def update_mapping(session, single_update_request):
        single_response = (
            single_update_request.construct_single_update_response_for_success()
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
                addl_info_keys = [info["name"] for info in addl_info_copy]
                for info in single_update_request.additional_info:
                    if info.name in addl_info_keys:
                        addl_info_copy[
                            addl_info_keys.index(info.name)
                        ] = info.model_dump()
                    else:
                        addl_info_copy.append(info.model_dump())
                result.additional_info = addl_info_copy
        else:
            single_response.status = StatusEnum.rjct
            single_response.status_reason_code = UpdateStatusReasonCode.rjct_id_invalid
            single_response.status_reason_message = (
                "Mapping doesnt exist against given ID. Use 'link' instead."
            )
        await session.commit()

    @staticmethod
    async def resolve(self, request: Request):
        session_maker = async_sessionmaker(dbengine.get(), expire_on_commit=False)
        async with session_maker() as session:
            resolveRequest: ResolveRequest = ResolveRequest.model_validate(
                request.message
            )
            single_resolve_responses: list[SingleResolveResponse] = []

            for single_resolve_request in resolveRequest.link_request:
                try:
                    await IdFaMappingValidations.get_component().validate_resolve_request(
                        connection=session,
                        single_resolve_request=single_resolve_request,
                    )

                    stmt, is_rejected = await self.construct_query(
                        single_resolve_request
                    )
                    if is_rejected:
                        return single_resolve_responses, True

                    result = await self.execute_query(session, stmt)
                    self.construct_single_resolve_response(
                        single_resolve_request, result
                    )

                    single_resolve_responses.append(
                        self.construct_single_resolve_response_for_success(
                            single_resolve_request
                        )
                    )
                except ResolveValidationException as e:
                    single_resolve_request.append(
                        self.construct_single_resolve_response_for_failure(
                            single_resolve_request, e
                        )
                    )

        await session.commit()

        return single_resolve_responses

    @staticmethod
    def construct_single_resolve(single_resolve_request, result):
        single_response = (
            single_resolve_request.construct_single_resolve_response_for_success()
        )

        if result:
            if single_resolve_request.scope == ResolveScope.details:
                single_response.fa = result.fa_value
                single_response.id = result.id_value
                single_response.additional_info = (
                    [
                        # AdditionalInfo.model_validate(info)
                        # for info in result.additional_info
                    ]
                    if result.additional_info
                    else None
                )
            elif single_resolve_request.scope == ResolveScope.yes_no:
                pass
            if single_resolve_request.fa and not single_resolve_request.id:
                single_response.status = StatusEnum.succ
                single_response.status_reason_code = (
                    ResolveStatusReasonCode.succ_fa_active
                )
            else:
                single_response.status = StatusEnum.succ
                single_response.status_reason_code = (
                    ResolveStatusReasonCode.succ_id_active
                )
        else:
            single_response.status = StatusEnum.succ
            if single_resolve_request.id and single_resolve_request.fa:
                single_response.status_reason_code = (
                    ResolveStatusReasonCode.succ_fa_not_linked_to_id
                )
                single_response.status_reason_message = (
                    "No mapping found for given FA and ID combination."
                )
            elif single_resolve_request.fa:
                single_response.status_reason_code = (
                    ResolveStatusReasonCode.succ_fa_not_found
                )
                single_response.status_reason_message = (
                    "Mapping not found against given FA."
                )
            else:
                single_response.status_reason_code = (
                    ResolveStatusReasonCode.succ_id_not_found
                )
                single_response.status_reason_message = (
                    "Mapping not found against given ID."
                )

    @staticmethod
    async def construct_query(each_req):
        id_query = IdFaMapping.id_value == each_req.id
        fa_query = IdFaMapping.fa_value == each_req.fa
        if each_req.id and each_req.id.endswith("@") and ":" in each_req.id:
            id_query = IdFaMapping.id_value.like(f"%{each_req.id}%")
        if each_req.fa and each_req.fa.endswith("@") and ":" in each_req.fa:
            fa_query = IdFaMapping.fa_value.like(f"%{each_req.fa}%")

        stmt = None
        if each_req.id and each_req.fa:
            stmt = select(IdFaMapping).where(and_(id_query, fa_query))
        elif each_req.id:
            stmt = select(IdFaMapping).where(id_query)
        elif each_req.fa:
            stmt = select(IdFaMapping).where(fa_query)
        else:
            raise ResolveValidationException(
                message="Neither ID (nor FA) is given.",
                status=StatusEnum.rjct,
                validation_error_type=ResolveStatusReasonCode.rjct_id_invalid,
            )  # Indicates query construction failure
        return stmt, False

    @staticmethod
    async def execute_query(session, stmt):
        result = await session.execute(stmt)
        return result.scalar() if result else None

    @staticmethod
    def construct_single_resolve_response_for_success(single_resolve_request):
        return SingleResolveResponse(
            reference_id=single_resolve_request.reference_id,
            timestamp=datetime.now(),
            fa=single_resolve_request.fa,
            status=StatusEnum.succ,
            status_reason_code=None,
            status_reason_message=None,
            additional_info=None,
            locale=single_resolve_request.locale,
        )

    @staticmethod
    def construct_single_resolve_response_for_failure(single_resolve_request, error):
        return SingleResolveResponse(
            reference_id=single_resolve_request.reference_id,
            timestamp=datetime.now(),
            fa=single_resolve_request.fa,
            status=StatusEnum.rjct,
            status_reason_code=error.validation_error_type,
            status_reason_message=error.message,
            additional_info=None,
            locale=single_resolve_request.locale,
        )

    async def unlink(self, request: Request):
        session_maker = async_sessionmaker(dbengine.get(), expire_on_commit=False)
        async with session_maker() as session:
            unlinkRequest: UnlinkRequest = UnlinkRequest.model_validate(request.message)
            single_unlink_responses: list[SingleUnlinkResponse] = []
            mappings_to_delete = []
            for single_unlink_request in unlinkRequest.link_request:
                try:
                    await IdFaMappingValidations.get_component().validate_unlink_request(
                        connection=session, single_update_request=single_unlink_request
                    )
                    mappings_to_delete.append(
                        self.unlink_id_fa_mapping(single_unlink_request)
                    )
                    single_unlink_responses.append(
                        self.construct_single_unlink_response_for_success(
                            single_unlink_request
                        )
                    )
                except UnlinkValidationException as e:
                    UnlinkValidationException(
                        message=" ID doesn't exist",
                        status=StatusEnum.rjct,
                        validation_error_type=UnlinkStatusReasonCode.rjct_id_invalid,
                    )
                    single_unlink_responses.append(
                        self.construct_single_unlink_response_for_failure(
                            single_unlink_request, e
                        )
                    )
        session.delete(*mappings_to_delete)
        await session.commit()
        return single_unlink_responses

    @staticmethod
    def unlink_id_fa_mapping(single_unlink_request):
        return IdFaMapping(
            id_value=single_unlink_request.id,
            fa_value=single_unlink_request.fa,
            name=single_unlink_request.name,
            phone=single_unlink_request.phone_number,
            additional_info=single_unlink_request.additional_info,
            active=True,
        )

    @staticmethod
    def construct_single_unlink_response_for_success(single_unlink_request):
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

    @staticmethod
    def construct_single_unlink_response_for_failure(single_unlink_request, error):
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
