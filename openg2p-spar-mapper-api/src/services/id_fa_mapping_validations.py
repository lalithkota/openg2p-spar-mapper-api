from openg2p_g2pconnect_common_lib.spar.schemas.resolve import SingleResolveRequest, ResolveStatusReasonCode

from openg2p_fastapi_common.service import BaseService
from openg2p_g2pconnect_common_lib.spar.schemas import LinkStatusReasonCode, SingleUpdateRequest, UpdateStatusReasonCode
from openg2p_g2pconnect_common_lib.spar.schemas import SingleLinkRequest
from sqlalchemy import and_, select

from .exceptions import LinkValidationException, UpdateValidationException, ResolveValidationException
from ..models.orm import IdFaMapping


class IdFaMappingValidations(BaseService):

    @staticmethod
    async def validate_link_request(
         connection, single_link_request: SingleLinkRequest
    ) -> None:

        # Check if the ID is null
        if not single_link_request.id:
            raise LinkValidationException(
                message="ID is null",
                validation_error_type=LinkStatusReasonCode.rjct_id_invalid,
            )

        # Check if the FA is null
        if not single_link_request.fa:
            raise LinkValidationException(
                message="FA is null",
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
                validation_error_type=LinkStatusReasonCode.rjct_reference_id_duplicate,
            )

        return None

    @staticmethod
    async def validate_update_request(
       connection, single_update_request: SingleUpdateRequest
    ) -> None:

        # Check if the ID is null
        if not single_update_request.id:
            raise UpdateValidationException(
                message="ID is null",
                validation_error_type=UpdateStatusReasonCode.rjct_id_invalid,
            )

        # Check if the FA is null
        if not single_update_request.fa:
            raise UpdateValidationException(
                message="FA is null",
                validation_error_type=UpdateStatusReasonCode.rjct_fa_invalid,
            )

        # Check if the ID is already mapped
        result = await connection.execute(
            select(IdFaMapping).where(
                and_(
                    IdFaMapping.id_value == single_update_request.id,
                    IdFaMapping.fa_value == single_update_request.fa,
                )
            )
        )
        link_request_from_db = result.first()

        if link_request_from_db is None:
            raise UpdateValidationException(
                message="ID doesnt exist please link first",
                validation_error_type=UpdateStatusReasonCode.rjct_reference_id_duplicate,
            )

        return None

    @staticmethod
    async def validate_resolve_request(
       connection, single_resolve_request: SingleResolveRequest
    ) -> None:

        # Check if the ID is null
        if not single_resolve_request.id:
            raise ResolveValidationException(
                message="ID is null",
                validation_error_type=ResolveStatusReasonCode.rjct_id_invalid,
            )

        # Check if the FA is null
        if not single_resolve_request.fa:
            raise ResolveValidationException(
                message="FA is null",
                validation_error_type=ResolveStatusReasonCode.rjct_fa_invalid,
            )

        # Check if the ID is already mapped
        result = await connection.execute(
            select(IdFaMapping).where(
                and_(
                    IdFaMapping.id_value == single_resolve_request.id,
                    IdFaMapping.fa_value == single_resolve_request.fa,
                )
            )
        )
        link_request_from_db = result.first()

        if link_request_from_db:
            raise ResolveValidationException(
                message="ID doesnt exist please link first",
                validation_error_type=ResolveStatusReasonCode.rjct_reference_id_duplicate,
            )
        return None
