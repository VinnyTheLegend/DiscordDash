from typing import Optional

from pydantic import BaseModel

from datetime import datetime

class User(BaseModel):
    id: int
    username: str
    global_name: str
    avatar: str

    member: bool
    admin: bool
    nickname: Optional[str]
    joined_at: Optional[datetime]
    roles: Optional[list[int]]

    class Config:
        orm_mode = True

class UserCreate(User):
    access_token: str
    expires_in: int
    expires_at: int

