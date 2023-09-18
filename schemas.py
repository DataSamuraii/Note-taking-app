import datetime
from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str = Field(pattern=r'^[a-zA-Z][a-zA-Z0-9_]*$',
                          min_length=8, max_length=16,)
    email: str | None = Field(default=None, pattern=r'^[\w%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
                              min_length=5, max_length=50,)
    full_name: str | None = None
    disabled: bool = False


class UserInDB(User):
    hashed_password: str


class UserRegistration(User):
    password: str = Field(pattern=r'^[a-zA-Z][a-zA-Z0-9_]*$', min_length=8, max_length=16,
                          description='Starts with a letter followed by letters, numbers, and underscores')


class TagIn(BaseModel):
    tag_name: str = Field(title="The name of the tag", min_length=3, max_length=10)


class TagOut(TagIn):
    owner: str


class NoteIn(BaseModel):
    title: str = Field(title="The title of the note", min_length=3, max_length=20)
    content: str = Field(title="The content of the note", min_length=3, max_length=1000)
    tags: list[TagIn] | None = list()


class NoteOut(NoteIn):
    created_at: datetime.datetime
    updated_at: datetime.datetime
    owner: str


class NewNote(BaseModel):
    title: str | None = Field(default=None, title="The title of the new note", min_length=3, max_length=20)
    content: str | None = Field(default=None, title="The content of the new note", min_length=3, max_length=1000)
    tags: list[TagIn] | None = list()
