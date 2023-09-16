import schemas

from database import notes_db, tags_db, users_db

from typing import Annotated
from datetime import datetime, timedelta

from fastapi import Depends, FastAPI, HTTPException, Query, Path, status
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from passlib.context import CryptContext
from jose import JWTError, jwt


SECRET_KEY = '8a15f7937b03471c75a2cf525ed5e4172af0cd9b2c8fa4c9449e2c7265a9c1d0'
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

oauth_scheme = OAuth2PasswordBearer(tokenUrl='login')

app = FastAPI()

ValidID = Annotated[int, Path(ge=1)]


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(plain_password):
    return pwd_context.hash(plain_password)


def get_user(db, username: str):
    if username in db:
        user_dict = db.get(username)
        return schemas.UserInDB(**user_dict)


def authenticate_user(user_db, username, password):
    user = get_user(user_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        username = payload.get('sub')
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(users_db, token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: Annotated[schemas.User, Depends(get_current_user)]):
    if current_user.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Inactive user')
    return current_user


def find_max_id(db) -> int:
    max_id = db[-1]['id'] + 1 if db else 0
    return max_id


def find_note_by_id(note_id: int) -> tuple[int, schemas.NoteSchemaOut] | tuple[None, None]:
    for i, note in enumerate(notes_db):
        if note_id == note['id']:
            return i, note
    return None, None


def find_tag_by_id(tag_id: int) -> tuple[int, schemas.TagSchema] | tuple[None, None]:
    for i, tag in enumerate(tags_db):
        if tag_id == tag['id']:
            return i, tag
    return None, None


def add_tags_to_db(tags: set[schemas.TagSchema]) -> None:
    tag_names_set = {tag['tag_name'] for tag in tags_db}
    for tag in tags:
        if tag.tag_name not in tag_names_set:
            max_id = find_max_id(tags_db)
            new_tag = {'id': max_id, 'tag_name': tag.tag_name}
            tags_db.append(new_tag)


@app.post('/login', tags=['users'], response_model=schemas.Token)
async def login_for_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token({'sub': user.username}, access_token_expires)
    return {'access_token': access_token, 'token_type': "bearer"}


@app.get('/users', tags=['users'])
async def get_users() -> dict[str, schemas.User]:
    return users_db


@app.get("/users/me/", tags=['users'], response_model=schemas.User)
async def get_users_me(current_user: Annotated[schemas.User, Depends(get_current_active_user)]):
    return current_user


@app.get('/users/me/notes', tags=['users'])
async def get_own_notes(current_user: Annotated[schemas.User, Depends(get_current_active_user)]):
    return [note for note in notes_db if note['owner'] == current_user.username]


@app.get("/notes", tags=['notes'])
async def get_notes() -> list[schemas.NoteSchemaOut]:
    return notes_db


@app.get("/notes/search", tags=['notes'])
async def search_note(note_title: Annotated[str, Query(alias='note-title',
                                                       min_length=3,
                                                       max_length=10)] = None,
                      note_content: Annotated[str, Query(alias='note-content',
                                                         min_length=3,
                                                         max_length=10)] = None) -> list:
    found_notes = []
    for note in notes_db:
        if (note_title and note_title.lower() in note['title'].lower()) or \
                (note_content and note_content.lower() in note['content'].lower()):
            found_notes.append(note)
    return found_notes


@app.get("/notes/{note_id}", tags=['notes'])
async def get_note(note_id: ValidID) -> schemas.NoteSchemaOut:
    i, note = find_note_by_id(note_id)
    if note:
        return note
    raise HTTPException(status_code=404, detail='Note not found')


@app.post("/notes", tags=['notes'])
async def add_note(note: schemas.NoteSchemaIn) -> schemas.NoteSchemaOut:
    max_id = find_max_id(notes_db)
    created_at = datetime.now()
    add_tags_to_db(note.tags)

    note_model = schemas.NoteSchemaOut(**note.model_dump(), **{'created_at': created_at, 'updated_at': created_at})
    notes_db.append({'id': max_id, **note_model.model_dump()})
    return note_model


@app.put("/notes/{note_id}", tags=['notes'])
async def update_note(note_id: ValidID, new_note: schemas.NewNoteSchema) -> schemas.NoteSchemaOut:
    i, note = find_note_by_id(note_id)
    if note:
        update_data = {**new_note.model_dump(exclude_unset=True), 'updated_at': datetime.now()}
        note.update(jsonable_encoder(update_data))
        return note
    raise HTTPException(status_code=404, detail="Note not found")


@app.delete("/notes/{note_id}", tags=['notes'])
async def delete_note(note_id: ValidID) -> schemas.NoteSchemaOut:
    i, note = find_note_by_id(note_id)
    if note:
        return notes_db.pop(i)
    raise HTTPException(status_code=404, detail="Note not found")


@app.put("/notes/{note_id}/tags", tags=['notes'])
async def put_tag(note_id: ValidID, tags: set[schemas.TagSchema]) -> schemas.NoteSchemaOut:
    add_tags_to_db(tags)
    i, note = find_note_by_id(note_id)
    if note:
        for tag in tags:
            tag_as_dict = tag.model_dump()
            if tag_as_dict not in note['tags']:
                note['tags'].append(tag_as_dict)
        note['updated_at'] = datetime.now()
        notes_db[i] = note
        return note
    raise HTTPException(status_code=404, detail='Note not found')


@app.delete("/notes/{note_id}/tags", tags=['notes'])
async def remove_tag(note_id: ValidID, tags: set[schemas.TagSchema]) -> schemas.NoteSchemaOut:
    i, note = find_note_by_id(note_id)
    if note:
        if note['tags']:
            for tag in tags:
                tag_as_dict = tag.model_dump()
                if tag_as_dict in note['tags']:
                    note['tags'].remove(tag_as_dict)
            note['updated_at'] = datetime.now()
            notes_db[i] = note
            return note
        raise HTTPException(status_code=400, detail="No tags to remove")
    raise HTTPException(status_code=404, detail="Note not found")


@app.get("/tags", tags=['tags'])
async def get_tags() -> list[schemas.TagSchema]:
    return tags_db


@app.get("/tags/search", tags=['tags'])
async def search_tag(tag_name: Annotated[str, Query(alias='tag-name',
                                                    min_length=3,
                                                    max_length=10,)] = None) -> list:
    found_tags = []
    if tag_name:
        for tag in tags_db:
            if tag_name.lower() in tag['tag_name'].lower():
                found_tags.append(tag)
    return found_tags


@app.get("/tags/{tag_id}", tags=['tags'])
async def get_tag(tag_id: ValidID) -> schemas.TagSchema:
    i, tag = find_tag_by_id(tag_id)
    if tag:
        return tag
    raise HTTPException(status_code=404, detail='Tag not found')


@app.post("/tags", tags=['tags'])
async def add_tag(tag: set[schemas.TagSchema]) -> set[schemas.TagSchema]:
    add_tags_to_db(tag)
    return tag


@app.put("/tags/{tag_id}", tags=['tags'])
async def update_tag(tag_id: ValidID, new_tag: schemas.TagSchema) -> schemas.TagSchema:
    i, tag = find_tag_by_id(tag_id)
    if tag:
        tag.update({**new_tag.model_dump()})
        return tag
    raise HTTPException(status_code=404, detail="Tag not found")


@app.delete("/tags/{tag_id}", tags=['tags'])
async def delete_tag(tag_id: ValidID) -> schemas.TagSchema:
    i, tag = find_tag_by_id(tag_id)
    if tag:
        return tags_db.pop(i)
    raise HTTPException(status_code=404, detail="Tag not found")
