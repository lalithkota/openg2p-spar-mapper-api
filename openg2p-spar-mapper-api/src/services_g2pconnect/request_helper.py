from datetime import datetime

from openg2p_fastapi_common.service import BaseService
from openg2p_g2pconnect_common_lib.common.schemas import (
    SyncRequest,
)
from openg2p_g2pconnect_common_lib.spar.schemas.link import (
    LinkRequest,
)

from ..models.orm.id_fa_mapping import IdFaMapping


class SyncRequestHelper(BaseService):

    def deconstruct_link_request(self, request: SyncRequest) -> list[IdFaMapping]:
        linkRequest: LinkRequest = LinkRequest.model_validate(request.message)
        return [
            IdFaMapping(
                id_value=link_req.id,
                fa_value=link_req.fa,
                name=link_req.name,
                phone=link_req.phone_number,
                additional_info=link_req.additional_info,
                active=True,
                created_at=datetime.now(),
            )
            for link_req in linkRequest.link_request
        ]
