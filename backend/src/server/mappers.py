from src.core.repositories.base_data_mapper import BaseMapper
from src.server.models import ServerOrm
from src.server.schemas import ServerSchema


class ServerMapper(BaseMapper[ServerOrm, ServerSchema]):
    orm_class = ServerOrm
    schema_class = ServerSchema
