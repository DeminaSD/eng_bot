import sqlalchemy
from sqlalchemy import create_engine, delete,select
from sqlalchemy.orm import Session
from classes import Word, User, UsersWords 

def inserting_to_word_table(user, pswd, host, port, dbname, rus_word, eng_translate):
    engine = create_engine(
        f"postgresql+psycopg2://{user}:{pswd}@{host}:{port}/{dbname}"
    )
    with Session(engine) as session:
        new_word = Word(rus_word=rus_word, eng_translate=eng_translate)
        session.add(new_word)
        session.commit()
        return new_word.id  # Возвращаем id созданного слова

def inserting_to_user_table(user, pswd, host, port, dbname, user_tg_id):
    engine = create_engine(
        f"postgresql+psycopg2://{user}:{pswd}@{host}:{port}/{dbname}"
    )
    with Session(engine) as session:
        stmt = select(User).where(User.tgid == user_tg_id)
        existing_user = session.execute(stmt).scalar_one_or_none()
        
        if existing_user:
            return existing_user.id #Если юзер существует, то на этом функция заканчивает работать
        
        new_user = User(tgid=user_tg_id)
        session.add(new_user)
        session.commit()
        return new_user.id

def inserting_to_userswords_table(user, pswd, host, port, dbname, userid, wordid):
    engine = create_engine(
        f"postgresql+psycopg2://{user}:{pswd}@{host}:{port}/{dbname}"
    )
    with Session(engine) as session:
        # Проверяем существование связи через select
        stmt = select(UsersWords).where(
            UsersWords.user_id == userid,
            UsersWords.word_id == wordid
        )
        existing_relation = session.execute(stmt).scalar_one_or_none()
        
        if not existing_relation:
            new_relation = UsersWords(user_id=userid, word_id=wordid)
            session.add(new_relation)
            session.commit()
            return True
        return False

def get_user_id_by_tgid(user, pswd, host, port, dbname, tgid):
    engine = create_engine(
        f"postgresql+psycopg2://{user}:{pswd}@{host}:{port}/{dbname}"
    )
    with Session(engine) as session:
        stmt = select(User).where(User.tgid == tgid)
        user = session.execute(stmt).scalar_one_or_none()
        
        if user:
            return user.id
        return None

def get_word_id_by_rus_word(user, pswd, host, port, dbname, rus_word):
    engine = create_engine(
        f"postgresql+psycopg2://{user}:{pswd}@{host}:{port}/{dbname}"
    )
    with Session(engine) as session:
        stmt = select(Word).where(Word.rus_word == rus_word)
        word = session.execute(stmt).scalar_one_or_none()
        
        if word:
            return word.id
        return None