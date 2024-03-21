from openg2p_g2pconnect_common_lib.spar.schemas import LinkStatusReasonCode

class LinkValidationException(Exception):
    def __init__(self, message, validation_error_type: LinkStatusReasonCode):
        self.message = message
        super().__init__(self.message)
        self.validation_error_type: LinkStatusReasonCode = validation_error_type


class RequestValidationException(Exception):
    # TODO : Add code
    def __init__(self, code, message):
        self.code = code
        self.message = message
        super().__init__(self.message)
