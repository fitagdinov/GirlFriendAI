from sqlalchemy import Text, MetaData, Integer, BigInteger
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class Base(DeclarativeBase):
    metadata = MetaData(schema="general")


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True)
    username: Mapped[str] = mapped_column(Text(), nullable=True)
    first_name: Mapped[str] = mapped_column(Text(), nullable=True)
    last_name: Mapped[str] = mapped_column(Text(), nullable=True)
    quota: Mapped[int] = mapped_column(Integer(), nullable=False)


class Girl(Base):
    __tablename__ = "girl"
    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True)
    owner_id: Mapped[int] = mapped_column(BigInteger(), nullable=False)
    token: Mapped[str] = mapped_column(Text(), nullable=False)
    username: Mapped[str] = mapped_column(Text(), nullable=False)
    first_name: Mapped[str] = mapped_column(Text(), nullable=False)
    age: Mapped[str] = mapped_column(Text(), nullable=False)
    photo_file_id: Mapped[str] = mapped_column(Text(), nullable=False)
    appearance: Mapped[str] = mapped_column(Text(), nullable=False)
    interests: Mapped[str] = mapped_column(Text(), nullable=False)


class TempGirl(Base):
    __tablename__ = "temp_girl"
    owner_id: Mapped[int] = mapped_column(BigInteger(), primary_key=True)
    username: Mapped[str] = mapped_column(Text(), nullable=True)
    first_name: Mapped[str] = mapped_column(Text(), nullable=True)
    age: Mapped[str] = mapped_column(Text(), nullable=True)
    photo_file_id: Mapped[str] = mapped_column(Text(), nullable=True)
    appearance: Mapped[str] = mapped_column(Text(), nullable=True)
    interests: Mapped[str] = mapped_column(Text(), nullable=True)


class Token(Base):
    __tablename__ = "token"
    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True)
    account_id: Mapped[int] = mapped_column(BigInteger(), nullable=False)
    token: Mapped[str] = mapped_column(Text(), nullable=False)
    username: Mapped[str] = mapped_column(Text(), nullable=False)
    is_free: Mapped[int] = mapped_column(Integer(), nullable=False)


class Account(Base):
    __tablename__ = "account"
    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True)
    api_id: Mapped[int] = mapped_column(BigInteger(), nullable=False)
    api_hash: Mapped[str] = mapped_column(Text(), nullable=False)
    string: Mapped[str] = mapped_column(Text(), nullable=False)


