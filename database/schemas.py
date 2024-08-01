from typing import Optional

from pydantic import BaseModel

from datetime import datetime

class User(BaseModel):
    id: str
    username: str
    global_name: Optional[str]
    avatar: Optional[str]

    member: bool
    admin: bool
    nickname: Optional[str]
    joined_at: Optional[datetime]
    roles: Optional[list[str]]
    connection_time: float

    class Config:
        orm_mode = True

class UserCreate(User):
    access_token: Optional[str]
    expires_in: Optional[int]
    expires_at: Optional[int]

class TwitchStream(BaseModel):
    user_login: str
    added_by: str

    class Config:
        orm_mode = True

class Role(BaseModel):
    id: str
    name: str
    optional: bool
    added_by: Optional[str]
    allowed_optional: bool

    class Config:
        orm_mode = True

class LeftOrRight(BaseModel):
    name: str
    img_url: str
    added_by: str
    wins: Optional[int]