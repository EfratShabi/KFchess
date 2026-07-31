from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from server.tokens import create_token


class Credentials(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    token: str


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

    return app


if __name__ == '__main__':
    import uvicorn
    from server.db import init_db, AccountRepository

    conn = init_db()
    repo = AccountRepository(conn)
    uvicorn.run(create_app(repo), host='0.0.0.0', port=8000)
