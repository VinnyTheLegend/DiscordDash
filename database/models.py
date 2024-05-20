from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, PickleType
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True)
    global_name = Column(String, index=True)
    avatar = Column(String)

    access_token = Column(String, index=True)
    expires_in = Column(Integer)
    refresh_token = Column(String)
    expires_at = Column(Integer)

    member = Column(Boolean)
    admin = Column(Boolean)
    nickname = Column(String, index=True, nullable=True)
    joined_at = Column(DateTime(timezone=True), nullable=True)
    roles = Column(PickleType, nullable=True)

    guilds = relationship("Guild", back_populates="user")


class Guild(Base):
    __tablename__ = "guilds"

    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    owner = Column(Boolean)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="guilds")