from sqlalchemy import ForeignKey
from backend.database.database_connect import UserBase
from sqlalchemy.orm import Mapped,mapped_column,relationship

class UserData(UserBase):
    __tablename__ = "user_data"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_name: Mapped[str] = mapped_column(unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    is_admin: Mapped[bool] = mapped_column(default=False)
    # Use cascade="delete-orphan" to say delete any notes with a None user
    notes:Mapped[list["UserNotes"]] = relationship("UserNotes",back_populates="user",cascade="all,delete-orphan")

class UserNotes(UserBase):
    __tablename__ = "user_notes"
    id:Mapped[int] = mapped_column(primary_key=True)
    user_id:Mapped[int] = mapped_column(ForeignKey("user_data.id"),nullable=False)
    note:Mapped[str] = mapped_column(nullable=False)
    timestamp:Mapped[str] = mapped_column(nullable=False)
    user: Mapped["UserData"] = relationship("UserData", back_populates="notes")