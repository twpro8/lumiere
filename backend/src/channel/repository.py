from src.channel.mappers import ChannelMapper
from src.channel.models import ChannelOrm
from src.channel.schemas import ChannelSchema
from src.core.repositories import BaseRepository


class ChannelRepository(BaseRepository[ChannelOrm, ChannelSchema]):
    model = ChannelOrm
    schema = ChannelSchema
    mapper = ChannelMapper
