# Standard library imports
import os
import re

# Related third-party imports
from dotenv import load_dotenv
from fastapi import HTTPException, Request, Response, status
from jose import JWTError, jwt
from sqlmodel import Session, select
from starlette.middleware.base import BaseHTTPMiddleware

# Local application/library specific imports
from database.database import engine
from models import schemas


load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


def validate_token(token: str) -> schemas.User | HTTPException:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        username = payload.get('sub')
        if username is None:
            return credentials_exception
    except JWTError:
        return credentials_exception

    with Session(engine) as session:
        exp = select(schemas.User).where(schemas.User.username == username)
        user = session.exec(exp).one()

    if user is None:
        return credentials_exception

    return user


class AuthMiddleware(BaseHTTPMiddleware):
    # Specifies list of paths that require login
    patterns = [
        r'/users/me/', r'/users/me/notes', r'/users/me/tags',
        r'/notes/post', r'/notes/\d+', r'/notes/\d+/tags',
        r'/tags/post', r'/tags/\d+'
    ]

    async def dispatch(self, request: Request, call_next) -> Response:
        if any(re.fullmatch(pattern, request.url.path) for pattern in self.patterns):
            auth_header = request.headers.get("Authorization")

            if auth_header is None or not auth_header.startswith("Bearer "):
                # No Authorization header or it doesn't start with "Bearer"
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            token = auth_header.split(" ")[1]

            user_or_exception = validate_token(token)
            if isinstance(user_or_exception, HTTPException):
                raise user_or_exception

            if user_or_exception.disabled:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Inactive user')

            request.state.user = user_or_exception
        response = await call_next(request)
        return response
