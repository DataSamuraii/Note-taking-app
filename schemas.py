from pydantic import BaseModel, Field


class TagSchema(BaseModel):
    tag_name: str = Field(title="The name of the tag", min_length=3, max_length=10)

    # Makes tags frozen to make them hashable (I have many checks for tag presence in set)
    class Config:
        frozen = True


class NoteSchema(BaseModel):
    title: str = Field(title="The title of the note", min_length=3, max_length=20)
    content: str = Field(title="The content of the note", min_length=3, max_length=1000)
    tags: set[TagSchema] | None = set()


class NewNoteSchema(BaseModel):
    title: str | None = Field(default=None, title="The title of the new note", min_length=3, max_length=20)
    content: str | None = Field(default=None, title="The content of the new note", min_length=3, max_length=1000)
    tags: set[TagSchema] | None = set()
