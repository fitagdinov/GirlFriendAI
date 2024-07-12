import telebot
import yaml

from telebot import types
from pathlib import Path

from bots import BotConfig
from dataclasses import dataclass

with open(Path('./config_ru.yaml').resolve()) as file:
    params = yaml.load(file, yaml.SafeLoader)

bot_cfg = BotConfig(**params)

bot = telebot.TeleBot(bot_cfg.token)


@dataclass
class Girl:
    name: str = None
    age: str = None
    face: str = None
    features: str = None


girl = Girl()


@bot.callback_query_handler(lambda call: call.data == "create_name")
def create_name(call: types.CallbackQuery):
    bot.send_message(call.from_user.id, bot_cfg.messages["create"]["name"])
    bot.register_next_step_handler(call.message, lambda x: girl.__setattr__("name", x.text))


@bot.callback_query_handler(lambda call: call.data == "create_age")
def create_age(call: types.CallbackQuery):
    bot.send_message(call.from_user.id, bot_cfg.messages["create"]["age"])
    bot.register_next_step_handler(call.message, lambda x: girl.__setattr__("age", x.text))


@bot.callback_query_handler(lambda call: call.data == "create_face")
def create_face(call: types.CallbackQuery):
    bot.send_message(call.from_user.id, bot_cfg.messages["create"]["face"])
    bot.register_next_step_handler(call.message, lambda x: girl.__setattr__("face", x.text))


@bot.callback_query_handler(lambda call: call.data == "create_features")
def create_face(call: types.CallbackQuery):
    bot.send_message(call.from_user.id, bot_cfg.messages["create"]["features"])
    bot.register_next_step_handler(call.message, lambda x: girl.__setattr__("features", x.text))


@bot.callback_query_handler(lambda call: call.data == "create_preview")
def create_preview(call: types.CallbackQuery):
    bot.send_message(call.from_user.id, str(girl))


@bot.callback_query_handler(lambda call: call.data == "create")
def create(call: types.CallbackQuery):
    markup = types.InlineKeyboardMarkup(row_width=2)

    markup.add(types.InlineKeyboardButton(bot_cfg.buttons["create"]["name"], callback_data="create_name"),
               types.InlineKeyboardButton(bot_cfg.buttons["create"]["age"], callback_data="create_age"))

    markup.add(types.InlineKeyboardButton(bot_cfg.buttons["create"]["face"], callback_data="create_face"),
               types.InlineKeyboardButton(bot_cfg.buttons["create"]["features"], callback_data="create_features"))

    markup.add(types.InlineKeyboardButton(bot_cfg.buttons["create"]["preview"], callback_data="create_preview"))
    markup.add(types.InlineKeyboardButton(bot_cfg.buttons["create"]["save"], callback_data="create_save"))

    bot.send_message(call.from_user.id, bot_cfg.messages["create"]["start"], reply_markup=markup)


@bot.message_handler(commands=['start'])
def welcome(message: types.Message):
    markup = types.InlineKeyboardMarkup(row_width=2)

    markup.add(types.InlineKeyboardButton(bot_cfg.buttons["welcome"]["create"], callback_data="create"))
    markup.add(types.InlineKeyboardButton(bot_cfg.buttons["welcome"]["edit"], callback_data="edit"))
    markup.add(types.InlineKeyboardButton(bot_cfg.buttons["welcome"]["remove"], callback_data="remove"))

    bot.send_message(message.from_user.id, bot_cfg.messages["welcome"]["start"], reply_markup=markup)


bot.polling(none_stop=True, interval=0)
