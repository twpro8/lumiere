from dataclasses import dataclass
from uuid import UUID


@dataclass
class AccessTokenPayload:
    sub: UUID
