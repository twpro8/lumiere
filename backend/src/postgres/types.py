from datetime import datetime
from typing import Annotated
from uuid import UUID

from sqlalchemy import String, DateTime, text
from sqlalchemy.orm import mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

int_pk = Annotated[int, mapped_column(primary_key=True)]
uuid_pk = Annotated[
    UUID,
    mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    ),
]
str_128 = Annotated[str, mapped_column(String(128))]
created_at = Annotated[
    datetime,
    mapped_column(
        DateTime(timezone=True),
        server_default=text("TIMEZONE('UTC', now())"),
    ),
]
