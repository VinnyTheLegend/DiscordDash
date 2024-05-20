from sqlalchemy.orm import Session

from . import models, schemas


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_token(db: Session, access_token: str):
    return db.query(models.User).filter(models.User.access_token == access_token).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_guilds(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Guild).offset(skip).limit(limit).all()

def create_user_guild(db: Session, guild: schemas.Guild, user_id: int):
    db_item = models.Guild(**guild.model_dump(), user_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def update_user(db: Session, user_id: int, user: schemas.UserCreate):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db.query(models.User).filter(models.User.id == user_id).update(user.model_dump())
        db.commit()
        db.refresh(db_user)
        return db_user
    return None