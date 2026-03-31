import random
import telebot
from telebot import types, TeleBot
from inserting_base_to_db import (
    inserting_to_user_table, 
    inserting_to_word_table,
    inserting_to_userswords_table,
    get_user_id_by_tgid,
    get_word_id_by_rus_word  
)
import logging

from sqlalchemy import create_engine, delete, String, select
from sqlalchemy.orm import Session

# Импортируем ORM-классы из classes.py
from classes import Word, User, UsersWords, Base

logging.basicConfig(filename='bot_logs.txt', encoding='utf-8', level=logging.INFO)
logger = logging.getLogger(__name__)

# Константы для подключения к БД
from keys import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME

basic_words = {
    'алгоритм': 'algorithm',
    'компилятор': 'compiler',
    'база данных': 'database',
    'отладчик': 'debugger',
    'шифрование': 'encryption',
    'фреймворк': 'framework',
    'наследование': 'inheritance',
    'интерфейс': 'interface',
    'оптимизация': 'optimization',
    'полиморфный': 'polymorphic',
    'рефакторинг': 'refactor',
    'репозиторий': 'repository',
    'сериализовать': 'serialize',
    'тест': 'test',
    'версия': 'version',
    'виртуализация': 'virtualization',
    'абстракция': 'abstraction',
    'зависимость': 'dependency',
    'паттерн': 'pattern',
    'объект': 'object'
}

# Инициализация базовых слов для всех пользователей
# Создадим специального системного пользователя для общих слов
system_user_tgid = "SYSTEM"
system_user_id = inserting_to_user_table(
    DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME, system_user_tgid
)

for rus_word, eng_translate in basic_words.items():
    # Добавляем слово в таблицу слов
    word_id = inserting_to_word_table(
        DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME, rus_word, eng_translate
    )
    # Связываем слово с системным пользователем
    inserting_to_userswords_table(
        DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME, system_user_id, word_id
    )

from keys import token_bot
bot = TeleBot(token_bot)

@bot.message_handler(commands=['start'])
def start(message):
    user_tg_id = str(message.from_user.id)
    user_id = inserting_to_user_table(
        DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME, user_tg_id
    )
    
    
    logger.info(f"User {message.from_user.id} started the bot")
    bot.send_message(message.from_user.id, "Список команд:")
    bot.send_message(message.from_user.id, "/show - показать слова")
    bot.send_message(message.from_user.id, "/add - добавить слово")
    bot.send_message(message.from_user.id, "/delete - удалить слово")
    bot.send_message(message.from_user.id, "/teach - практиковаться")

@bot.message_handler(commands=['show'])
def show_words(message):
    logger.info(f"User {message.from_user.id} requested word list")
    user_tg_id = str(message.from_user.id)
    user_words = get_user_words(user_tg_id)
    
    if user_words:
        words_list = ', '.join([word[0] for word in user_words])
        bot.send_message(message.from_user.id, words_list)
    else:
        bot.send_message(message.from_user.id, "У вас пока нет слов. Добавьте слова с помощью /add")

def get_user_words(user_tg_id):
    """
    Получает список слов пользователя из БД
    """
    engine = create_engine(
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    with Session(engine) as session:
        # Получаем пользователя через select
        stmt_user = select(User).where(User.tgid == user_tg_id)
        user = session.execute(stmt_user).scalar_one_or_none()
        
        if user:
            # Вариант 1: Получаем все связи слов для пользователя через select
            stmt_relations = select(UsersWords).where(
                UsersWords.user_id == user.id
            )
            relations = session.execute(stmt_relations).scalars().all()
            
            words = []
            for relation in relations:
                stmt_word = select(Word).where(Word.id == relation.word_id)
                word = session.execute(stmt_word).scalar_one_or_none()
                if word:
                    words.append((word.rus_word, word.eng_translate))
            return words
        
        return []


@bot.message_handler(commands=['add'])
def add_word(message):
    logger.info(f"User {message.from_user.id} initiated word addition")
    bot.send_message(message.from_user.id, "Введите слово: русское слово-английский перевод") 
    bot.register_next_step_handler(message, process_added_word)

def process_added_word(message):
    if '-' in message.text:
        rus_word, eng_translate = message.text.strip().lower().split('-')
        
        # Добавляем слово в таблицу слов
        word_id = inserting_to_word_table(
            DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME, 
            rus_word, eng_translate
        )
        
        # Получаем id пользователя
        user_id = get_user_id_by_tgid(
            DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME, 
            str(message.from_user.id)
        )
        
        # Связываем слово с пользователем
        if user_id and word_id:
            inserting_to_userswords_table(
                DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME, 
                user_id, word_id
            )
        
        bot.send_message(message.from_user.id, f"{rus_word}-{eng_translate} - ЗАПИСАНО")
    else:
        bot.send_message(message.from_user.id, f"Неправильный ввод. Вызовите команду /add еще раз и повторите ввод.")

# Запуск бота
if __name__ == "__main__":
    bot.polling(none_stop=True)