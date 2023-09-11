from typing import Optional, List
from pydantic import BaseModel


class TagSchema(BaseModel):
    tag_name: str


class NoteSchema(BaseModel):
    title: str
    content: str
    tags: Optional[List[TagSchema]] = None


class NewNoteSchema(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[TagSchema]] = None
