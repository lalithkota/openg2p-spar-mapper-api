from openg2p_fastapi_common.service import BaseService
from openg2p_g2pconnect_common_lib.spar.schemas import LinkStatusReasonCode
from openg2p_g2pconnect_common_lib.spar.schemas import SingleLinkRequest
from sqlalchemy import and_, select

from .exceptions import LinkValidationException
from ..models.orm import IdFaMapping


class IdFaMappingValidations(BaseService):

    async def validate_link_request(
        self, connection, single_link_request: SingleLinkRequest
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
