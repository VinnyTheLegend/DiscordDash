from sqlalchemy.orm import Session

from . import models, schemas

import hashlib
from passlib.context import CryptContext

#token hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_token(token: str) -> str:
    return pwd_context.hash(token)

def verify_token(token: str, hashed_token: str) -> bool:
    return pwd_context.verify(token, hashed_token)

def generate_token_identifier(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


#crud
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_token(db: Session, access_token: str):
    token_identifier = generate_token_identifier(access_token)
    return db.query(models.User).filter(models.User.token_identifier == token_identifier).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    if 'access_token' in user:
        token_identifier = generate_token_identifier(user.access_token)
        hashed_token = hash_token(user.access_token)

        user_data = user.model_dump()
        user_data['access_token'] = hashed_token
        user_data['token_identifier'] = token_identifier
        
        db_user = models.User(**user_data)
    else:
        db_user = models.User(**user.model_dump())

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user: schemas.UserCreate):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        if user.access_token:
            token_identifier = generate_token_identifier(user.access_token)
            hashed_token = hash_token(user.access_token)
            updated_user_data = user.model_dump()
            updated_user_data['access_token'] = hashed_token
            updated_user_data['token_identifier'] = token_identifier
        else:
            updated_user_data = user.model_dump()
            updated_user_data['access_token'] = db_user.access_token
            updated_user_data['token_identifier'] = db_user.token_identifier
            updated_user_data['expires_in'] = db_user.expires_in
            updated_user_data['expires_at'] = db_user.expires_at

        if user.connection_time == 0 or user.connection_time == None:
            updated_user_data['connection_time'] = db_user.connection_time
        if user.muted_time == 0 or user.muted_time == None:
            if db_user.muted_time != 0 and db_user.muted_time != None:
                updated_user_data['muted_time'] = db_user.muted_time
            else:
                updated_user_data['muted_time'] = 0
        if user.deafened_time == 0 or user.deafened_time == None:
            if db_user.deafened_time != 0 and db_user.deafened_time != None:
                updated_user_data['deafened_time'] = db_user.deafened_time
            else:
                updated_user_data['deafened_time'] = 0
            
        db.query(models.User).filter(models.User.id == user_id).update(updated_user_data)
        db.commit()
        db.refresh(db_user)
        return db_user
    return None

def update_user_connection_time(db: Session, user_id: str, time: float):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db_user.connection_time = db_user.connection_time + time
        db.commit()
        db.refresh(db_user)
        return db_user
    return None

def update_user_muted_time(db: Session, user_id: str, time: float):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db_user.muted_time = db_user.muted_time + time
        db.commit()
        db.refresh(db_user)
        return db_user
    return None

def update_user_deafened_time(db: Session, user_id: str, time: float):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db_user.deafened_time = db_user.deafened_time + time
        db.commit()
        db.refresh(db_user)
        return db_user
    return None

def user_add_role(db: Session, user_id: str, role_id: str):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        roles = list(db_user.roles)
        roles.append(role_id)
        db_user.roles = roles
        db.commit()
        db.refresh(db_user)
        return db_user
    return None

def user_remove_role(db: Session, user_id: str, role_id: str):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        roles = list(db_user.roles)
        roles.remove(role_id)
        db_user.roles = roles
        db.commit()
        db.refresh(db_user)
        return db_user
    return None


# roles
def create_role(db: Session, role: schemas.Role):
    db_role = models.Role(**role.model_dump())
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

def get_role(db: Session, role_id: str):
    return db.query(models.Role).filter(models.Role.id == role_id).first()

def update_role(db: Session, role_id: str, role: schemas.Role):
    rows_updated = db.query(models.Role).filter(models.Role.id == role_id).update(role.model_dump())
    db.commit()
    return rows_updated

def get_roles(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Role).offset(skip).limit(limit).all()

def del_role(db: Session, role_id: str):
    deleted_rows = db.query(models.Role).filter(models.Role.id == role_id).delete()
    db.commit()
    return deleted_rows

# Twitch Streams
def create_twitchstream(db: Session, stream: schemas.TwitchStream):
    db_stream = models.TwitchStream(**stream.model_dump())
    db.add(db_stream)
    db.commit()
    db.refresh(db_stream)
    return db_stream

def get_twitchstream(db: Session, user_login: str):
    return db.query(models.TwitchStream).filter(models.TwitchStream.user_login == user_login).first()

def get_twitchstreams(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.TwitchStream).offset(skip).limit(limit).all()

def del_twitchstream(db: Session, user_login: str):
    deleted_rows = db.query(models.TwitchStream).filter(models.TwitchStream.user_login == user_login).delete()
    db.commit()
    return deleted_rows

#leftorright
def create_leftorright(db: Session, lor: schemas.LeftOrRight):
    lor.name = lor.name.lower()
    db_lor = models.LeftOrRight(**lor.model_dump())
    db.add(db_lor)
    db.commit()
    db.refresh(db_lor)
    return db_lor

def get_leftorright(db: Session, name: str):
    name = name.lower()
    return db.query(models.LeftOrRight).filter(models.LeftOrRight.name == name).first()

def get_leftorrights(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.LeftOrRight).offset(skip).limit(limit).all()

def del_leftorright(db: Session, name: str):
    name = name.lower()
    deleted_rows = db.query(models.LeftOrRight).filter(models.LeftOrRight.name == name).delete()
    db.commit()
    return deleted_rows

def leftorright_update_img(db: Session, name: str, img_url: str):
    name = name.lower()
    db_lor = db.query(models.LeftOrRight).filter(models.LeftOrRight.name == name).first()
    db_lor.img_url = img_url
    db.commit()
    db.refresh(db_lor)
    return db_lor

def leftorright_add_win(db: Session, name: str):
    name = name.lower()
    db_lor = db.query(models.LeftOrRight).filter(models.LeftOrRight.name == name).first()
    db_lor.wins = db_lor.wins + 1
    db.commit()
    db.refresh(db_lor)
    return db_lor