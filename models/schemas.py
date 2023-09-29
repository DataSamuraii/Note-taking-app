import datetime

from sqlmodel import Relationship, Field, SQLModel


class Token(SQLModel):
    access_token: str
    token_type: str


class UserBase(SQLModel):
    username: str = Field(regex=r'^[a-zA-Z][a-zA-Z0-9_]*$',
                          min_length=3, max_length=16, unique=True)
    email: str | None = Field(default=None, regex=r'^[\w%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
                              min_length=5, max_length=50, unique=True)
    full_name: str | None = None


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str
    disabled: bool = False


class UserCreate(UserBase):
    pass


class UserRead(UserBase):
    id: int


class UserRegister(UserBase):
    password: str = Field(regex=r'^[a-zA-Z][a-zA-Z0-9_]*$', min_length=8, max_length=16,
                          description='Starts with a letter followed by letters, numbers, and underscores')


class NoteTagLink(SQLModel, table=True):
    note_id: int = Field(foreign_key="note.id", primary_key=True)
    tag_id: int = Field(foreign_key="tag.id", primary_key=True)

    note: 'Note' = Relationship(back_populates="tags_link")
    tag: 'Tag' = Relationship(back_populates="notes_link")


class TagBase(SQLModel):
    tag_name: str = Field(title="The name of the tag", min_length=3, max_length=20)


class Tag(TagBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key='user.id')

    notes_link: list[NoteTagLink] = Relationship(back_populates="tag")


class TagCreate(TagBase):
    pass


class TagRead(TagBase):
    id: int
    owner_id: str


class NoteBase(SQLModel):
    title: str = Field(title="The title of the note", min_length=3, max_length=20)
    content: str = Field(title="The content of the note", min_length=3, max_length=1000)


class Note(NoteBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key='user.id')
    created_at: datetime.datetime
    updated_at: datetime.datetime

    tags_link: list[NoteTagLink] = Relationship(back_populates="note")


class NoteCreate(NoteBase):
    pass


class NoteRead(NoteBase):
    id: int
    owner_id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime


class NoteUpdate(SQLModel):
    title: str | None = Field(default=None, title="The title of the new note", min_length=3, max_length=20)
    content: str | None = Field(default=None, title="The content of the new note", min_length=3, max_length=1000)


class NoteUpdateTags(SQLModel):
    tag_ids: list[int]
