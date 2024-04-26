from openg2p_fastapi_common.service import BaseService
from openg2p_g2pconnect_common_lib.schemas import StatusEnum
from openg2p_g2pconnect_mapper_lib.schemas import (
    LinkStatusReasonCode,
    ResolveStatusReasonCode,
    SingleLinkRequest,
    SingleResolveRequest,
    SingleUnlinkRequest,
    SingleUpdateRequest,
    UnlinkStatusReasonCode,
    UpdateStatusReasonCode,
)
from sqlalchemy import and_, select

from ..models import IdFaMapping
from .exceptions import (
    LinkValidationException,
    ResolveValidationException,
    UnlinkValidationException,
    UpdateValidationException,
)


class IdFaMappingValidations(BaseService):
    async def validate_link_request(
        self, connection, single_link_request: SingleLinkRequest
    ) -> None:
        # Check if the ID is null
        if not single_link_request.id:
            raise LinkValidationException(
                message="ID is null",
                status=StatusEnum.rjct,
                validation_error_type=LinkStatusReasonCode.rjct_id_invalid,
            )

        # Check if the FA is null
        if not single_link_request.fa:
            raise LinkValidationException(
                message="FA is null",
                status=StatusEnum.rjct,
                validation_error_type=LinkStatusReasonCode.rjct_fa_invalid,
            )

        # Check if the ID is already mapped
        result = await connection.execute(
            select(IdFaMapping).where(
                and_(
                    IdFaMapping.id_value == single_link_request.id,
                    IdFaMapping.fa_value == single_link_request.fa,
                )
            )
        )
        link_request_from_db = result.first()

        if link_request_from_db:
            raise LinkValidationException(
                message="ID and FA are already mapped",
                status=StatusEnum.rjct,
                validation_error_type=LinkStatusReasonCode.rjct_reference_id_duplicate,
            )

        return None

    async def validate_update_request(
        self, connection, single_update_request: SingleUpdateRequest
    ) -> None:
        if not single_update_request.id:
            raise UpdateValidationException(
                message="ID is null",
                status=StatusEnum.rjct,
                validation_error_type=UpdateStatusReasonCode.rjct_id_invalid,
            )

        if not single_update_request.fa:
            raise UpdateValidationException(
                message="FA is null",
                status=StatusEnum.rjct,
                validation_error_type=UpdateStatusReasonCode.rjct_fa_invalid,
            )

        result = await connection.execute(
            select(IdFaMapping).where(
                and_(
                    IdFaMapping.id_value == single_update_request.id,
                )
            )
        )
        update_request_from_db = result.first()

        if not update_request_from_db:
            raise UpdateValidationException(
                message="ID doesnt exist please link first",
                status=StatusEnum.rjct,
                validation_error_type=UpdateStatusReasonCode.rjct_reference_id_duplicate,
            )

        return None

    async def validate_resolve_request(
        self, connection, single_resolve_request: SingleResolveRequest
    ) -> None:
        if not single_resolve_request.id and not single_resolve_request.fa:
            raise ResolveValidationException(
                message="ID is required",
                status=StatusEnum.rjct,
                validation_error_type=ResolveStatusReasonCode.rjct_reference_id_invalid,
            )

        result = await connection.execute(
            select(IdFaMapping).where(
                IdFaMapping.id_value == single_resolve_request.id,
            )
        )
        resolve_request_from_db = result.first()

        if not resolve_request_from_db:
            raise ResolveValidationException(
                message="ID doesnt exist please link first",
                status=StatusEnum.succ,
                validation_error_type=ResolveStatusReasonCode.succ_fa_not_linked_to_id,
            )
        return None

    async def validate_unlink_request(
        self, connection, single_unlink_request: SingleUnlinkRequest
    ) -> None:
        if not single_unlink_request.id:
            raise UnlinkValidationException(
                message="ID is null",
                status=StatusEnum.rjct,
                validation_error_type=UnlinkStatusReasonCode.rjct_id_invalid,
            )

        result = await connection.execute(
            select(IdFaMapping).where(
                IdFaMapping.id_value == single_unlink_request.id,
            )
        )

        if single_unlink_request.fa:
            result = result.where(IdFaMapping.fa_value == single_unlink_request.fa)

        unlink_request_from_db = result.first()

        if not unlink_request_from_db:
            raise UnlinkValidationException(
                message="ID doesnt exist please link first",
                status=StatusEnum.rjct,
                validation_error_type=UnlinkStatusReasonCode.rjct_id_invalid,
            )

        return None
