from sqlalchemy import Text, MetaData, Integer
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class Base(DeclarativeBase):
    metadata = MetaData(schema="general")


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(Integer(), primary_key=True)
    username: Mapped[str] = mapped_column(Text(), nullable=False)
    first_name: Mapped[str] = mapped_column(Text(), nullable=False)
    last_name: Mapped[str] = mapped_column(Text(), nullable=False)
    quota: Mapped[int] = mapped_column(Integer(), nullable=False)


class Girl(Base):
    __tablename__ = "girl"
    id: Mapped[int] = mapped_column(Integer(), primary_key=True)
    owner_id: Mapped[int] = mapped_column(Integer(), nullable=False)
    token: Mapped[str] = mapped_column(Text(), nullable=False)
    username: Mapped[str] = mapped_column(Text(), nullable=False)
    first_name: Mapped[str] = mapped_column(Text(), nullable=False)
    age: Mapped[str] = mapped_column(Text(), nullable=False)
    photo_path: Mapped[str] = mapped_column(Text(), nullable=False)
    features: Mapped[str] = mapped_column(Text(), nullable=False)


class TempGirl(Base):
    __tablename__ = "temp_girl"
    owner_id: Mapped[int] = mapped_column(Integer(), primary_key=True)
    first_name: Mapped[str] = mapped_column(Text(), nullable=True)
    age: Mapped[str] = mapped_column(Text(), nullable=True)
    photo_path: Mapped[str] = mapped_column(Text(), nullable=True)
    features: Mapped[str] = mapped_column(Text(), nullable=True)


class Token(Base):
    __tablename__ = "token"
    id: Mapped[int] = mapped_column(Integer(), primary_key=True)
    token: Mapped[str] = mapped_column(Text(), nullable=False)
    username: Mapped[str] = mapped_column(Text(), nullable=False)
    is_free: Mapped[int] = mapped_column(Integer(), nullable=False)
