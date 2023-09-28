import re

from models import schemas

from jose import JWTError, jwt

from fastapi import HTTPException, Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware

SECRET_KEY = '8a15f7937b03471c75a2cf525ed5e4172af0cd9b2c8fa4c9449e2c7265a9c1d0'
ALGORITHM = 'HS256'


def get_user(db: dict, username: str) -> schemas.UserRead:
    if username in db:
        user_dict = db.get(username)
        return schemas.UserRead(**user_dict)


def validate_token(token: str) -> schemas.UserRead | HTTPException:
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
        token_data = schemas.TokenData(username=username)
    except JWTError:
        return credentials_exception

    user = get_user(users_db, token_data.username)
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
