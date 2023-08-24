import telebot
import logging

from telebot.apihelper import session

from models import User
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, \
    ReplyKeyboardRemove
from models import User, Base, engine

from barbershop_telegram import config
from config import BOT_TOKEN

logging.basicConfig(level=logging.INFO)
bot = telebot.TeleBot(config.BOT_TOKEN)

# connect = sqlite3.connect("barbershop_telegram.db")
# cursor = connect.cursor()
# cursor.execute("CREATE TABLE people (id INTEGER PRIMARY KEY AUTOINCREMENT,chat_id BIGINT, first_name TEXT, last_name TEXT, phone TEXT, procedure TEXT, date BIGINT, time TEXT)")

procedures = ['Стрижка', 'Гоління', 'Комплекс', 'Написати адміністратору']


@bot.message_handler(commands=['start'])
def phone(message):
    global chat_id
    chat_id = message.chat.id
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_phone = types.KeyboardButton(text="Відправити номер телефону", request_contact=True)
    keyboard.add(button_phone)
    bot.send_message(message.chat.id, 'Номер телефона', reply_markup=keyboard)


@bot.message_handler(content_types=['contact'])
def contact(message):
    if message.contact is not None:
        print(message.contact)
        inline_markup = telebot.types.InlineKeyboardMarkup(row_width=1)
        for procedure in procedures:
            inline_markup.add(telebot.types.InlineKeyboardButton(procedure, callback_data=procedure))
        bot.send_message(message.chat.id, "Виберіть процедуру:", reply_markup=inline_markup)


@bot.callback_query_handler(func=lambda call: call.data in procedures)
def process_procedure(callback_query, process_date_time=str):
    procedure = callback_query.data
    bot.send_message(callback_query.from_user.id, f"Ви обрали процедуру: {procedure}")
    new_user = User(chat_id=callback_query.message.chat.id, procedure=procedure, first_name=callback_query.from_user.first_name, last_name=callback_query.from_user.last_name, phone=callback_query.from_user.contact.phone_number)
    session.add(new_user)
    session.commit()
    bot.send_message(callback_query.from_user.id,
                     "Введіть дату та час візиту у форматі ДД-ММ та час(приклад -> 19.05 15:00)")
    bot.register_next_step_handler(callback_query.message, process_date_time)
    bot.answer_callback_query(callback_query.id)


print("Telegram Support Bot started...")
bot.polling()
