import uvicorn

from models import schemas
from database.database import create_db_and_tables, get_session
from middleware.middleware import AuthMiddleware

from typing import Annotated
from datetime import datetime, timedelta

from passlib.context import CryptContext
from jose import jwt

from fastapi import Depends, FastAPI, HTTPException, Request, Query, Path, status
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordRequestForm

from sqlmodel import Session, select, col
from sqlalchemy.exc import IntegrityError


SECRET_KEY = '8a15f7937b03471c75a2cf525ed5e4172af0cd9b2c8fa4c9449e2c7265a9c1d0'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

app = FastAPI()
app.add_middleware(AuthMiddleware)


ValidID = Annotated[int, Path(ge=1)]


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)
    return encoded_jwt


@app.on_event("startup")
def on_startup():
    print("Application startup")
    create_db_and_tables()


@app.post('/login', tags=['users'], response_model=schemas.Token)
async def login_for_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                          session: Session = Depends(get_session)):
    exp = select(schemas.User).where(schemas.User.username == form_data.username)
    user = session.exec(exp).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token({'sub': user.username}, access_token_expires)
    return {'access_token': access_token, 'token_type': "bearer"}


@app.post('/registration', tags=['users'], response_model=schemas.UserRead)
async def register_user(new_user: schemas.UserRegister, session: Session = Depends(get_session)):
    hashed_password = get_password_hash(new_user.password)
    db_user = schemas.User(**new_user.dict(), hashed_password=hashed_password)

    session.add(db_user)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=400, detail="Username or email already registered")
    return db_user


@app.get('/users', tags=['users'], response_model=list[schemas.UserRead])
async def get_users(session: Session = Depends(get_session)):
    users = session.exec(select(schemas.User)).all()
    return users


@app.get("/users/me/", tags=['users'], response_model=schemas.UserRead)
async def get_users_me(request: Request):
    return request.state.user


@app.get('/users/me/notes', tags=['users'], response_model=list[schemas.NoteRead])
async def get_own_notes(request: Request, session: Session = Depends(get_session)):
    exp = select(schemas.Note).where(schemas.Note.owner_id == request.state.user.id)
    notes = session.exec(exp).all()
    return notes


@app.get("/users/me/tags", tags=['users'], response_model=list[schemas.TagRead])
async def get_own_tags(request: Request, session: Session = Depends(get_session)):
    exp = select(schemas.Tag).where(schemas.Tag.owner_id == request.state.user.id)
    tags = session.exec(exp).all()
    return tags


@app.get("/notes", tags=['notes'], response_model=list[schemas.NoteRead])
async def get_notes(session: Session = Depends(get_session)):
    notes = session.exec(select(schemas.Note)).all()
    return notes


@app.get("/notes/search", tags=['notes'], response_model=list[schemas.NoteRead])
async def search_note(note_title: Annotated[str, Query(alias='note-title',
                                                       min_length=3, max_length=10)] = None,
                      note_content: Annotated[str, Query(alias='note-content',
                                                         min_length=3, max_length=20)] = None,
                      session: Session = Depends(get_session)):
    exp = select(schemas.Note).where(col(schemas.Note.title).contains(note_title.lower()) |
                                     col(schemas.Note.content).contains(note_content.lower()))
    found_notes = session.exec(exp).all()
    return found_notes


@app.get("/notes/{note_id}", tags=['notes'], response_model=schemas.NoteRead)
async def get_note(note_id: ValidID, session: Session = Depends(get_session)):
    note = session.get(schemas.Note, note_id)
    if note is None:
        raise HTTPException(status_code=404, detail='Note not found')
    return note


@app.post("/notes/post", tags=['notes'], response_model=schemas.NoteRead)
async def add_note(note: schemas.NoteCreate, request: Request, session: Session = Depends(get_session)):
    created_at = datetime.utcnow()
    note_model = schemas.Note(**note.dict(), **{'owner': request.state.user.id,
                                                'created_at': created_at, 'updated_at': created_at})

    session.add(note_model)
    session.commit()
    session.refresh(note_model)
    return note_model


@app.put("/notes/{note_id}", tags=['notes'], response_model=schemas.NoteRead)
async def update_note(note_id: ValidID, new_note: schemas.NoteUpdate,
                      request: Request, session: Session = Depends(get_session)):
    db_note = session.get(schemas.Note, note_id)
    if db_note is None:
        raise HTTPException(status_code=404, detail='Note not found')
    elif db_note.owner_id == request.state.user.id:
        note_data = new_note.dict(exclude_unset=True)
        for key, value in note_data.items():
            setattr(db_note, key, value)
        setattr(db_note, 'updated_at', datetime.utcnow())
        session.add(db_note)
        session.commit()
        session.refresh(db_note)
        return db_note
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You are not authorized to update this note')


@app.delete("/notes/{note_id}", tags=['notes'], response_model=schemas.NoteRead)
async def delete_note(note_id: ValidID, request: Request):
    i, note = find_note_by_id(note_id)
    if note:
        if note['owner'] == request.state.user.username:
            return notes_db.pop(i)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You are not authorized to update this note')
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")


@app.put("/notes/{note_id}/tags", tags=['notes'], response_model=schemas.NoteRead)
async def put_tag(note_id: ValidID, tags: list[schemas.TagCreate], request: Request):
    add_tags_to_db(tags, request.state.user.username)
    i, note = find_note_by_id(note_id)
    if note:
        if note['owner'] == request.state.user.username:
            for tag in tags:
                tag_as_dict = tag.model_dump()
                if tag_as_dict not in note['tags']:
                    note['tags'].append(tag_as_dict)
            note['updated_at'] = datetime.now()
            notes_db[i] = note
            return note
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You are not authorized to update this note')
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Note not found')


@app.delete("/notes/{note_id}/tags", tags=['notes'])
async def remove_tag(note_id: ValidID, tags: set[schemas.TagCreate], request: Request) -> schemas.NoteRead:
    i, note = find_note_by_id(note_id)
    if note:
        if note['tags']:
            if note['owner'] == request.state.user.username:
                for tag in tags:
                    tag_as_dict = tag.model_dump()
                    if tag_as_dict in note['tags']:
                        note['tags'].remove(tag_as_dict)
                note['updated_at'] = datetime.now()
                notes_db[i] = note
                return note
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail='You are not authorized to update this note')
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No tags to remove")
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")


@app.get("/tags", tags=['tags'])
async def get_tags() -> list[schemas.TagRead]:
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


@app.get("/tags/{tag_id}", tags=['tags'], response_model=schemas.TagRead)
async def get_tag(tag_id: ValidID):
    i, tag = find_tag_by_id(tag_id)
    if tag:
        return tag
    raise HTTPException(status_code=404, detail='Tag not found')


@app.post("/tags/post", tags=['tags'])
async def add_tags(tag: list[schemas.TagCreate], request: Request) -> list[schemas.TagRead]:
    added_tags = add_tags_to_db(tag, request.state.user.username)
    return added_tags


@app.put("/tags/{tag_id}", tags=['tags'], response_model=schemas.TagRead)
async def update_tag(tag_id: ValidID, new_tag: schemas.TagCreate):
    i, tag = find_tag_by_id(tag_id)
    if tag:
        tag.update({**new_tag.model_dump()})
        return tag
    raise HTTPException(status_code=404, detail="Tag not found")


@app.delete("/tags/{tag_id}", tags=['tags'], response_model=schemas.TagRead)
async def delete_tag(tag_id: ValidID):
    i, tag = find_tag_by_id(tag_id)
    if tag:
        return tags_db.pop(i)
    raise HTTPException(status_code=404, detail="Tag not found")

# This is added for running the module manually to have access to debugger and breakpoint
# To run the server, run this in Terminal: uvicorn app:main --reload
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
