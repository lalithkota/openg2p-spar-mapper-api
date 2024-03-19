from pydantic import BaseModel
from enum import Enum


class IdFaMappingErrorType(Enum):
    id_unique_violation = "id_unique_violation"
    id_null_violation = "id_null_violation"
    fa_null_violation = "fa_null_violation"


class IdFaMappingError(BaseModel):
    id: str
    fa: str
    error_type: IdFaMappingErrorType
