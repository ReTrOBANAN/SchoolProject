from sqlalchemy import create_engine, String, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime
import os


class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    username: Mapped[str] = mapped_column(String(30))
    password: Mapped[str] = mapped_column(String(30))
    title: Mapped[str] = mapped_column(String(30))
    background: Mapped[str] = mapped_column(String(30))
    min_points: Mapped[int]
    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r}, username={self.username!r}, password={self.password!r}, title={self.title!r}, background={self.background!r}, min_points={self.min_points!r})"

class Question(Base):
    __tablename__ = "questions"
    id: Mapped[int] = mapped_column(primary_key=True)
    owner: Mapped[str] = mapped_column(String(30))
    subject: Mapped[str] = mapped_column(String(20))
    title: Mapped[str] = mapped_column(String(30))
    description: Mapped[str] = mapped_column(String(1000))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    def __repr__(self) -> str:
        return f"Question(id={self.id!r}, owner={self.owner!r}, subject={self.subject!r}, title={self.title!r}, description={self.description!r}, created={self.created_at!r})"

class Comment(Base):
    __tablename__ = "Comments"
    id: Mapped[int] = mapped_column(primary_key=True)
    question_id: Mapped[int]
    owner: Mapped[str] = mapped_column(String(30))
    description: Mapped[str] = mapped_column(String(1000))
    def __repr__(self) -> str:
        return f"Question(id={self.id!r}, owner={self.owner!r}, question_id={self.question_id!r}, description={self.description!r})"

current_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(current_dir, 'users.db')
engine = create_engine(f'sqlite:///{db_path}')