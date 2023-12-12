import datetime
import uuid
from typing import Optional

from pydantic import BaseModel


class FileHashSchema(BaseModel):
    req_id: uuid.UUID
    file_name: str
    md5_hash: Optional[str]
    processed: Optional[bool]
    received_at: datetime.datetime
    processed_at: Optional[datetime.datetime]
