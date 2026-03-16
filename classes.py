from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import ForeignKey, create_engine

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    tgid: Mapped[str] = mapped_column()

class Word(Base):
    __tablename__ = "words"
    id: Mapped[int] = mapped_column(primary_key=True)
    rus_word: Mapped[str] = mapped_column()
    eng_translate: Mapped[str] = mapped_column()

class UsersWords(Base):
    __tablename__ = "users_words"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    word_id: Mapped[int] = mapped_column(ForeignKey("words.id"))

engine = create_engine("postgresql+psycopg2://postgres:postgres@localhost:5432/english")
Base.metadata.create_all(engine)