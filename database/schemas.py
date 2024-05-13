from typing import Union

from pydantic import BaseModel

from datetime import datetime

class Guild(BaseModel):
    id: int
    name: str
    owner: bool

    user_id: int

class User(BaseModel):
    id: int
    username: str
    global_name: str
    avatar: str

    nickname: str
    joined_at: datetime
    roles: list[str]

    # guilds: list[Guild]

    class Config:
        orm_mode = True

class UserCreate(User):
    token: str
    expires_in: int
    refresh_token: str
    expires_at: int
    is_admin: bool

