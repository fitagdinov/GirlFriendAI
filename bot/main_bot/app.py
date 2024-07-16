import os
import telebot

from telebot import types
from pathlib import Path
from sqlalchemy.orm import Session

from bot.main_bot.menu import WelcomeMenu, CreateMenu
from db.create_db import get_engine

bot = telebot.TeleBot(os.environ["TOKEN"])

session = Session(get_engine())

welcome_menu = WelcomeMenu(session)
create_menu = CreateMenu(session)


@bot.message_handler(commands=['start'])
def welcome(message: types.Message):
    welcome_menu.add_user_if_not_exists(message.from_user)
    bot.send_message(message.from_user.id, welcome_menu.content.text, reply_markup=welcome_menu.content.markup)


@bot.callback_query_handler(lambda call: call.data == "welcome_create")
def create(call: types.CallbackQuery):
    exception = create_menu.add_temp_girl_for_user(call.from_user)
    if exception:
        bot.send_message(call.from_user.id, exception, reply_markup=create_menu.content.markup)
    else:
        bot.send_message(call.from_user.id, create_menu.content.text, reply_markup=create_menu.content.markup)


@bot.callback_query_handler(lambda call: call.data.split('_')[0] == "create")
def create_handler(call: types.CallbackQuery):
    key = call.data.split('_')[1]
    photo_path = Path(f"../../data/temp/photo_{call.from_user.id}.jpg")

    def add_girl_param(message: types.Message):
        if message.photo and key == "face":
            file_info = bot.get_file(message.photo[-1].file_id)
            with open(photo_path.resolve(), "wb") as file:
                file.write(bot.download_file(file_info.file_path))

        bot.send_message(call.from_user.id, create_menu.add_temp_girl_param(key, call.from_user, message),
                         reply_markup=create_menu.content.markup)

    if key in ["name", "age", "face", "features"]:
        text = create_menu.content.create_text.get(key)
        bot.send_message(call.from_user.id, text)
        bot.register_next_step_handler(call.message, add_girl_param)
    if key == "preview":
        if photo_path.exists():
            bot.send_photo(call.from_user.id,
                           open(photo_path.resolve(), "rb"),
                           create_menu.preview_temp_girl(call.from_user),
                           parse_mode='Markdown',
                           reply_markup=create_menu.content.markup)
        else:
            bot.send_message(call.from_user.id,
                             create_menu.preview_temp_girl(call.from_user),
                             parse_mode='Markdown',
                             reply_markup=create_menu.content.markup)
    if key == "save":
        bot.send_message(call.from_user.id, create_menu.save_temp_girl(call.from_user))

    if key == "back":
        bot.send_message(call.from_user.id, welcome_menu.content.text, reply_markup=welcome_menu.content.markup)


@bot.callback_query_handler(lambda call: call.data == "welcome_edit")
def edit_handler(call: types.CallbackQuery):
    bot.send_message(call.from_user.id, "Пока не работает(")


@bot.callback_query_handler(lambda call: call.data == "welcome_remove")
def remove_handler(call: types.CallbackQuery):
    bot.send_message(call.from_user.id, "Пока не работает(")


bot.polling(none_stop=True, interval=0)
