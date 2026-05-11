from src.channel.models import ChannelOrm
from src.channel.schemas import ChannelSchema
from src.core.repositories.base_data_mapper import BaseMapper


class ChannelMapper(BaseMapper[ChannelOrm, ChannelSchema]):
    orm_class = ChannelOrm
    schema_class = ChannelSchema
