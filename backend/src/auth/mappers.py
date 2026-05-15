from src.core.repositories.base_data_mapper import BaseMapper
from src.auth.models import RefreshTokenOrm
from src.auth.schemas import RefreshTokenSchema


class AuthMapper(BaseMapper[RefreshTokenOrm, RefreshTokenSchema]):
    orm_class = RefreshTokenOrm
    schema_class = RefreshTokenSchema
