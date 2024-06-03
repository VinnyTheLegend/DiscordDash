from sqlalchemy.orm import Session

from . import models, schemas

import hashlib
from passlib.context import CryptContext

#token hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_token(token: str) -> str:
    """Hash the token using bcrypt."""
    return pwd_context.hash(token)

def verify_token(token: str, hashed_token: str) -> bool:
    """Verify the token against the hashed token."""
    return pwd_context.verify(token, hashed_token)

def generate_token_identifier(token: str) -> str:
    """Generate a unique identifier for the token using SHA-256."""
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
    token_identifier = generate_token_identifier(user.access_token)
    hashed_token = hash_token(user.access_token)

    user_data = user.model_dump()
    user_data['access_token'] = hashed_token
    user_data['token_identifier'] = token_identifier
    
    db_user = models.User(**user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user: schemas.UserCreate):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        token_identifier = generate_token_identifier(user.access_token)
        hashed_token = hash_token(user.access_token)

        updated_user_data = user.model_dump()
        updated_user_data['access_token'] = hashed_token
        updated_user_data['token_identifier'] = token_identifier

        db.query(models.User).filter(models.User.id == user_id).update(updated_user_data)
        db.commit()
        db.refresh(db_user)
        return db_user
    return None