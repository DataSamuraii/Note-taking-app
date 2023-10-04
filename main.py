# Standard library imports
import os
from datetime import datetime, timedelta
from typing import Annotated

# Related third-party imports
import uvicorn
from dotenv import load_dotenv
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Request, Query, Path, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from passlib.context import CryptContext
from sqlmodel import Session, select, col
from sqlalchemy.exc import IntegrityError

# Local application/library specific imports
from database.database import create_db_and_tables, get_session
from middleware.middleware import AuthMiddleware
from models import schemas
from email_.email_function import send_email


load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))  # Default to 30 if not set

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
    create_db_and_tables()


@app.post('/registration', tags=['users'], response_model=schemas.UserRead)
async def register_user(new_user: schemas.UserRegister, background_tasks: BackgroundTasks,
                        session: Session = Depends(get_session)):
    hashed_password = get_password_hash(new_user.password)
    db_user = schemas.User(**new_user.dict(), hashed_password=hashed_password)

    session.add(db_user)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=400, detail="Username or email already registered")

    background_tasks.add_task(send_email, db_user.email, db_user.username)

    return db_user


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
    note_model = schemas.Note(**note.dict(), **{'owner_id': request.state.user.id,
                                                'created_at': created_at, 'updated_at': created_at})

    session.add(note_model)
    session.commit()
    return note_model


@app.patch("/notes/{note_id}", tags=['notes'], response_model=schemas.NoteRead)
async def update_note(note_id: ValidID, new_note: schemas.NoteUpdate,
                      request: Request, session: Session = Depends(get_session)):
    db_note = session.get(schemas.Note, note_id)
    if db_note is None:
        raise HTTPException(status_code=404, detail='Note not found')

    if db_note.owner_id != request.state.user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You are not authorized to update this note')

    note_data = new_note.dict(exclude_unset=True)
    for key, value in note_data.items():
        setattr(db_note, key, value)
    setattr(db_note, 'updated_at', datetime.utcnow())
    session.add(db_note)
    session.commit()
    return db_note


@app.delete("/notes/{note_id}", tags=['notes'], response_model=schemas.NoteRead)
async def delete_note(note_id: ValidID, request: Request, session: Session = Depends(get_session)):
    db_note = session.get(schemas.Note, note_id)
    if db_note is None:
        raise HTTPException(status_code=404, detail='Note not found')

    if db_note.owner_id != request.state.user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You are not authorized to delete this note')

    session.delete(db_note)
    session.commit()
    return db_note


@app.post("/notes/{note_id}/tags", tags=['notes'], response_model=schemas.NoteUpdateTags)
async def add_tags_to_note(note_id: ValidID, tag_update: schemas.NoteUpdateTags,
                           request: Request, session: Session = Depends(get_session)):
    db_note = session.get(schemas.Note, note_id)
    if db_note is None:
        raise HTTPException(status_code=404, detail='Note not found')

    if db_note.owner_id != request.state.user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You are not authorized to update this note')

    for tag_id in tag_update.tag_ids:
        exp = select(schemas.NoteTagLink).where((schemas.NoteTagLink.note_id == note_id) &
                                                (schemas.NoteTagLink.tag_id == tag_id))
        existing_link = session.exec(exp).first()
        if existing_link is None:
            link = schemas.NoteTagLink(note_id=note_id, tag_id=tag_id)
            session.add(link)
    session.commit()

    return tag_update


@app.delete("/notes/{note_id}/tags", tags=['notes'])
async def remove_tag(note_id: ValidID, tag_remove: schemas.NoteUpdateTags,
                     request: Request, session: Session = Depends(get_session)):
    db_note = session.get(schemas.Note, note_id)
    if db_note is None:
        raise HTTPException(status_code=404, detail='Note not found')

    if db_note.owner_id != request.state.user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You are not authorized to update this note')

    for tag_id in tag_remove.tag_ids:
        exp = select(schemas.NoteTagLink).where((schemas.NoteTagLink.note_id == note_id) &
                                                (schemas.NoteTagLink.tag_id == tag_id))
        existing_link = session.exec(exp).first()
        if existing_link:
            session.delete(existing_link)

    session.commit()

    return tag_remove


@app.get("/tags", tags=['tags'], response_model=list[schemas.TagRead])
async def get_tags(session: Session = Depends(get_session)):
    tags = session.exec(select(schemas.Tag)).all()
    return tags


@app.get("/tags/search", tags=['tags'])
async def search_tag(tag_name: Annotated[str, Query(alias='tag-name', min_length=3, max_length=10,)] = None,
                     session: Session = Depends(get_session)):
    exp = select(schemas.Tag).where(col(schemas.Tag.tag_name).contains(tag_name.lower()))
    found_tags = session.exec(exp).all()
    return found_tags


@app.get("/tags/{tag_id}", tags=['tags'], response_model=schemas.TagRead)
async def get_tag(tag_id: ValidID, session: Session = Depends(get_session)):
    db_tag = session.get(schemas.Tag, tag_id)
    if db_tag is None:
        raise HTTPException(status_code=404, detail='Tag not found')
    return db_tag


@app.post("/tags/post", tags=['tags'], response_model=schemas.TagRead)
async def add_tags(tag: schemas.TagCreate, request: Request, session: Session = Depends(get_session)):
    tag_model = schemas.Tag(**tag.dict(), **{'owner_id': request.state.user.id})

    session.add(tag_model)
    session.commit()
    return tag_model


@app.patch("/tags/{tag_id}", tags=['tags'], response_model=schemas.TagRead)
async def update_tag(tag_id: ValidID, new_tag: schemas.TagCreate,
                     request: Request, session: Session = Depends(get_session)):
    db_tag = session.get(schemas.Tag, tag_id)
    if db_tag is None:
        raise HTTPException(status_code=404, detail='Tag not found')

    if db_tag.owner_id != request.state.user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You are not authorized to update this tag')

    tag_data = new_tag.dict(exclude_unset=True)
    for key, value in tag_data.items():
        setattr(db_tag, key, value)

    session.add(db_tag)
    session.commit()
    return db_tag


@app.delete("/tags/{tag_id}", tags=['tags'], response_model=schemas.TagRead)
async def delete_tag(tag_id: ValidID, request: Request, session: Session = Depends(get_session)):
    db_tag = session.get(schemas.Tag, tag_id)
    if db_tag is None:
        raise HTTPException(status_code=404, detail='Tag not found')

    if db_tag.owner_id != request.state.user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You are not authorized to update this tag')

    session.delete(db_tag)
    session.commit()
    return db_tag


# This is added for running the module manually to have access to debugger and breakpoint
# To run the server properly, run this in Terminal: uvicorn app:main --reload
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
