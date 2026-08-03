from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from core.config.constants import WHITE_COLOR, BLACK_COLOR
from server.tokens import create_token, verify_token

bearer_scheme = HTTPBearer()


def _authenticate(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    username = verify_token(credentials.credentials)
    if username is None:
        raise HTTPException(status_code=401, detail='invalid or expired token')
    return username


class Credentials(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    token: str


class HistoryEntry(BaseModel):
    room_id: str
    opponent: str
    color: str
    result: str
    rating_after: int
    finished_at: datetime


def _to_history_entry(record, username):
    if record.white_username == username:
        opponent, color, rating_after = record.black_username, WHITE_COLOR, record.white_rating_after
    else:
        opponent, color, rating_after = record.white_username, BLACK_COLOR, record.black_rating_after
    result = 'win' if record.winner == color else 'loss'
    return HistoryEntry(
        room_id=record.room_id, opponent=opponent, color=color,
        result=result, rating_after=rating_after, finished_at=record.finished_at,
    )


def create_app(repo):
    app = FastAPI()

    @app.post('/register', response_model=TokenResponse)
    def register(credentials: Credentials):
        if not repo.register(credentials.username, credentials.password):
            raise HTTPException(status_code=409, detail='username already taken')
        return TokenResponse(token=create_token(credentials.username))

    @app.post('/login', response_model=TokenResponse)
    def login(credentials: Credentials):
        if not repo.authenticate(credentials.username, credentials.password):
            raise HTTPException(status_code=401, detail='invalid credentials')
        return TokenResponse(token=create_token(credentials.username))

    @app.get('/history', response_model=list[HistoryEntry])
    def history(username: str = Depends(_authenticate)):
        records = repo.get_history(username)
        return [_to_history_entry(record, username) for record in records]

    return app


if __name__ == '__main__':
    import uvicorn
    from server.db import init_db, AccountRepository

    conn = init_db()
    repo = AccountRepository(conn)
    uvicorn.run(create_app(repo), host='0.0.0.0', port=8000)
