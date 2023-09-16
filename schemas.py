import datetime
from pydantic import BaseModel, Field, ConfigDict


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str


class TagSchema(BaseModel):
    tag_name: str = Field(title="The name of the tag", min_length=3, max_length=10)

    # Makes tags frozen to make them hashable (I have many checks for tag presence in set)
    model_config = ConfigDict(frozen=True)


class NoteSchemaIn(BaseModel):
    title: str = Field(title="The title of the note", min_length=3, max_length=20)
    content: str = Field(title="The content of the note", min_length=3, max_length=1000)
    tags: set[TagSchema] | None = set()


class NoteSchemaOut(NoteSchemaIn):
    created_at: datetime.datetime
    updated_at: datetime.datetime


class NewNoteSchema(BaseModel):
    title: str | None = Field(default=None, title="The title of the new note", min_length=3, max_length=20)
    content: str | None = Field(default=None, title="The content of the new note", min_length=3, max_length=1000)
    tags: set[TagSchema] | None = set()
