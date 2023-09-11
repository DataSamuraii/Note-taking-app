# Would later be used as DataBase models
# Since I'm using a mock database, the Pydantic schemas will serve as main models for now.

from datetime import datetime
from typing import Optional


class NoteDB:
    id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime
    tags: Optional[int] = None


class TagDB:
    id: int
    name: str
