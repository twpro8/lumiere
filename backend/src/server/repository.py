from src.core.repositories import BaseRepository
from src.server.mappers import ServerMapper
from src.server.models import ServerOrm
from src.server.schemas import ServerSchema


class ServerRepository(BaseRepository[ServerOrm, ServerSchema]):
    model = ServerOrm
    schema = ServerSchema
    mapper = ServerMapper
