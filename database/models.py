from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, PickleType, Float
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    username = Column(String, unique=True, index=True)
    global_name = Column(String, index=True, nullable=True)
    avatar = Column(String, nullable=True)

    access_token = Column(String, index=True, nullable=True)
    token_identifier = Column(String, index=True, nullable=True)
    expires_in = Column(Integer, nullable=True)
    expires_at = Column(Integer, nullable=True)

    member = Column(Boolean)
    admin = Column(Boolean)
    nickname = Column(String, index=True, nullable=True)
    joined_at = Column(DateTime(timezone=True), nullable=True)
    roles = Column(PickleType, nullable=True)
    connection_time = Column(Float)
