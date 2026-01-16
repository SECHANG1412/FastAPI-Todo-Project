# app/sql_models/user.py

from sqlalchemy import String, Integer, Column
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import List, Optional
from ..database import Base
from sqlalchemy import Boolean



class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=True)
    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="owner")
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, server_default='false', nullable=False)


    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"