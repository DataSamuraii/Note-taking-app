from typing import List
from datetime import datetime

from fastapi import FastAPI, HTTPException
from database import notes_db, tags_db
from schemas import NoteSchema, NewNoteSchema, TagSchema


def find_max_id(db):
    max_id = db[-1]['id'] + 1 if db else 0
    return max_id


def find_note_by_id(note_id: int):
    for i, note in enumerate(notes_db):
        if note_id == note['id']:
            return i, note
    return None, None


def find_tag_by_id(tag_id: int):
    for i, tag in enumerate(tags_db):
        if tag_id == tag['id']:
            return i, tag
    return None, None


def add_tags_to_db(tags: List[TagSchema]):
    tag_names_set = {tag['tag_name'] for tag in tags_db}
    for tag in tags:
        if not any(existing_tag['tag_name'] == tag.tag_name for existing_tag in tag_names_set):
            max_id = find_max_id(tags_db)
            new_tag = {'id': max_id, 'tag_name': tag.tag_name}
            tags_db.append(new_tag)


app = FastAPI()


@app.get("/notes")
async def get_notes():
    return notes_db


@app.get("/tags")
async def get_tags():
    return tags_db


@app.get("/notes/search")
async def search_note(note_title: str = None, note_content: str = None):
    found_notes = []
    if note_title or note_content:
        for note in notes_db:
            if note_title.lower() in note['title'].lower() or note_content.lower() in note['content'].lower():
                found_notes.append(note)
    return found_notes


@app.get("/tags/search")
async def search_tag(tag_name: str = None):
    found_tags = []
    if tag_name:
        for tag in tags_db:
            if tag_name.lower() in tag['tag_name'].lower():
                found_tags.append(tag)
    return found_tags


@app.get("/notes/{note_id}")
async def get_note(note_id: int):
    i, note = find_note_by_id(note_id)
    if note:
        return note
    raise HTTPException(status_code=404, detail='Note not found')


@app.get("/tags/{tag_id}")
async def get_tag(tag_id: int):
    i, tag = find_tag_by_id(tag_id)
    if tag:
        return tag
    raise HTTPException(status_code=404, detail='Tag not found')


@app.post("/notes")
async def add_note(note: NoteSchema):
    max_id = find_max_id(notes_db)
    created_at = datetime.now()
    notes_db.append({'id': max_id,
                     **note.model_dump(),
                     'created_at': created_at,
                     'updated_at': created_at})
    add_tags_to_db(note.tags)
    return note


@app.post("/tags")
async def add_tag(tag: List[TagSchema]):
    add_tags_to_db(tag)
    return tag


@app.put("/notes/{note_id}/tags")
async def put_tag(note_id: int, tags: List[TagSchema]):
    i, note = find_note_by_id(note_id)
    if note:
        for tag in tags:
            if tag.model_dump() not in note['tags']:
                note['tags'].append(tag)
                note['updated_at'] = datetime.now()
        notes_db[i] = note
        return note
    raise HTTPException(status_code=404, detail='Tag not found')


@app.delete("/notes/{note_id}/tags")
async def remove_tag(note_id: int, tags: List[TagSchema]):
    i, note = find_note_by_id(note_id)
    if note:
        if note['tags']:
            for tag in tags:
                if tag.model_dump() in note['tags']:
                    note['tags'].remove(tag)
                    note['updated_at'] = datetime.now()
            notes_db[i] = note
            return note
        raise HTTPException(status_code=400, detail="No tags to remove")
    raise HTTPException(status_code=404, detail="Note not found")


@app.put("/notes/{note_id}")
async def update_note(note_id: int, new_note: NewNoteSchema):
    i, note = find_note_by_id(note_id)
    if note:
        note.update({**new_note.model_dump(), 'updated_at': datetime.now()})
        add_tags_to_db(note.tags)
        notes_db[i] = note
        return note
    raise HTTPException(status_code=404, detail="Note not found")


@app.put("/tags/{tag_id}")
async def update_tag(tag_id: int, new_tag: TagSchema):
    i, tag = find_tag_by_id(tag_id)
    if tag:
        tag.update({**new_tag.model_dump()})
        tags_db[i] = tag
        return tag
    raise HTTPException(status_code=404, detail="Tag not found")


@app.delete("/notes/{note_id}")
async def delete_note(note_id: int):
    i, note = find_note_by_id(note_id)
    if note:
        return notes_db.pop(i)
    raise HTTPException(status_code=404, detail="Note not found")


@app.delete("/tags/{tag_id}")
async def delete_tag(tag_id: int):
    i, tag = find_tag_by_id(tag_id)
    if tag:
        return tags_db.pop(i)
    raise HTTPException(status_code=404, detail="Tag not found")
