from openg2p_g2pconnect_common_lib.schemas import StatusEnum
from openg2p_g2pconnect_mapper_lib.schemas import (
    LinkStatusReasonCode,
    ResolveStatusReasonCode,
    UnlinkStatusReasonCode,
    UpdateStatusReasonCode,
)


class LinkValidationException(Exception):
    def __init__(self, message, status, validation_error_type: LinkStatusReasonCode):
        self.message = message
        super().__init__(self.message)
        self.status: StatusEnum = status
        self.validation_error_type: LinkStatusReasonCode = validation_error_type


class UpdateValidationException(Exception):
    def __init__(self, message, status, validation_error_type: UpdateStatusReasonCode):
        self.message = message
        super().__init__(self.message)
        self.status: StatusEnum = status
        self.validation_error_type: UpdateStatusReasonCode = validation_error_type


class ResolveValidationException(Exception):
    def __init__(self, message, status, validation_error_type: ResolveStatusReasonCode):
        self.message = message
        super().__init__(self.message)
        self.status: StatusEnum = status
        self.validation_error_type: ResolveStatusReasonCode = validation_error_type


class UnlinkValidationException(Exception):
    def __init__(self, message, status, validation_error_type: UnlinkStatusReasonCode):
        self.message = message
        super().__init__(self.message)
        self.status: StatusEnum = status
        self.validation_error_type: UnlinkStatusReasonCode = validation_error_type


class RequestValidationException(Exception):
    # TODO : Add code
    def __init__(self, code, message):
        self.code = code
        self.message = message
        super().__init__(self.message)
