from datetime import datetime, timedelta
import telebot
import logging
from telebot.apihelper import session
from models import User
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, \
    ReplyKeyboardRemove
from models import User, session, engine

from barbershop_telegram import config
from config import BOT_TOKEN

logging.basicConfig(level=logging.INFO)

bot = telebot.TeleBot(config.BOT_TOKEN)

selected_date = None
selected_time_slot = None
selected_procedure = None
phone_number = None
procedures = ['Стрижка', 'Гоління', 'Комплекс']

@bot.message_handler(commands=['start'])
def get_phone_number(message):
    global chat_id
    chat_id = message.chat.id
    user = session.query(User).filter_by(chat_id=chat_id).first()
    if user:
        show_procedure_buttons(chat_id)
    else:
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button_phone = types.KeyboardButton(text="Відправити номер телефону", request_contact=True)
        keyboard.add(button_phone)
        msg = bot.send_message(message.chat.id, 'Номер телефона', reply_markup=keyboard)
        bot.register_next_step_handler(msg, save_phone_number)

def save_phone_number(message):
    global phone_number
    phone_number = message.contact.phone_number
    bot.send_message(message.chat.id, "Ваш номер телефону збережено. Тепер ви авторизовані.")
    show_procedure_buttons(message.chat.id)

def show_procedure_buttons(chat_id):
    inline_markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    for procedure in procedures:
        inline_markup.add(telebot.types.InlineKeyboardButton(procedure, callback_data=procedure))
    inline_markup.add(telebot.types.InlineKeyboardButton("Написати адміністратору", callback_data="Написати адміністратору"))
    bot.send_message(chat_id, "Виберіть процедуру:", reply_markup=inline_markup)


@bot.message_handler(content_types=['contact'])
def get_contact(message):
    if message.contact is not None:
        global phone_number
        phone_number = message.contact.phone_number
        inline_markup = telebot.types.InlineKeyboardMarkup(row_width=1)
        for procedure in procedures:
            inline_markup.add(telebot.types.InlineKeyboardButton(procedure, callback_data=procedure))
        inline_markup.add(telebot.types.InlineKeyboardButton("Написати адміну", callback_data="Написати адміністратору"))
        bot.send_message(message.chat.id, "Виберіть процедуру:", reply_markup=inline_markup)
        bot.clear_reply_handlers_by_message_id(message.chat.id)

@bot.callback_query_handler(func=lambda call: call.data == 'Написати адміністратору')
def contact_admin(callback_query):
    admin_username = '@Tony2307'
    admin_link = f"https://t.me/{admin_username}"
    bot.send_message(callback_query.from_user.id, f"Напишіть адміністратору тут: {admin_link}")



@bot.callback_query_handler(func=lambda call: call.data in procedures)
def process_procedure(callback_query):
    global selected_procedure
    selected_procedure = callback_query.data
    inline_markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    button_date = telebot.types.InlineKeyboardButton(text="Виберіть дату", callback_data="choose_date")
    inline_markup.add(button_date)
    bot.send_message(callback_query.from_user.id, "Виберіть дату:", reply_markup=inline_markup)


@bot.callback_query_handler(func=lambda call: call.data == "choose_date")
def choose_date(callback_query):
    keyboard = types.InlineKeyboardMarkup(row_width=7)
    today = datetime.today()
    for i in range(7):
        date = today + timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        button_date = types.InlineKeyboardButton(text=date_str, callback_data=f"date_{i}")
        keyboard.add(button_date)
    bot.send_message(callback_query.from_user.id, "Виберіть дату з календаря:", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda callback_query: callback_query.data.startswith("date_"))
def process_date(callback_query):
    global selected_date

    selected_day = int(callback_query.data.split("_")[1])
    today = datetime.today()
    selected_date = (today + timedelta(days=selected_day)).strftime("%Y-%m-%d")

    global selected_procedure
    if selected_procedure is None:
        bot.send_message(callback_query.message.chat.id, "Виберіть процедуру перед вибором дати.")
        print(f"Selected procedure: {selected_procedure}")
        return

    time_slots = ['10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00']
    inline_markup = telebot.types.InlineKeyboardMarkup(row_width=2)

    for slot in time_slots:
        inline_markup.add(telebot.types.InlineKeyboardButton(slot, callback_data=f"time_{slot}"))

    bot.send_message(callback_query.message.chat.id, f"Ви вибрали дату: {selected_date}\nОберіть зручний для вас час:",
                     reply_markup=inline_markup)



@bot.callback_query_handler(func=lambda callback_query: callback_query.data.startswith("time_"))
def process_time(callback_query):
    global selected_time_slot

    selected_time_slot = callback_query.data.split("_")[1]

    if phone_number and selected_date and selected_time_slot:
        if selected_procedure:
            new_user = User(
                chat_id=callback_query.from_user.id,
                first_name=callback_query.from_user.first_name,
                last_name=callback_query.from_user.last_name,
                phone=phone_number,
                procedure=selected_procedure,
                date=selected_date,
                time=selected_time_slot
            )
            session.add(new_user)
            session.commit()

            response = f"Бронування успішно збережено:\nПроцедура: {selected_procedure}\nДата: {selected_date}\nЧас: {selected_time_slot}"
            bot.send_message(callback_query.from_user.id, response)
        else:
            bot.send_message(callback_query.from_user.id, "Виберіть процедуру перед вибором часу.")
    else:
        print(f"Phone number: {phone_number}\nSelected date: {selected_date}\nSelected time slot: {selected_time_slot}")
        bot.send_message(callback_query.from_user.id, "Виникла помилка. Будь ласка, розпочніть бронювання знову.")



print("Telegram Support Bot started...")
bot.polling()
