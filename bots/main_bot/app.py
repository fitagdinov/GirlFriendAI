from telebot import types

from bots.main_bot.bot import MainBot
from bots.main_bot import markup
from bots.main_bot.content import cfg

from db.utils import get_engine

bot = MainBot("6362570409:AAHoYwCL9Uz9UdNPP9mnQCDbvYXbEOsPXtA")
bot.set_engine(get_engine())


@bot.message_handler(commands=['start'])
@bot.exception()
def welcome(message: types.Message | types.CallbackQuery):
    bot.add_user_if_not_exists(message.from_user)
    bot.send_message(message.from_user.id, cfg["messages"]["welcome"], reply_markup=markup.welcome())


@bot.callback_query_handler(lambda call: call.data == "welcome_create")
@bot.exception()
def create(call: types.CallbackQuery):
    bot.create_temp_girl_for_user(call.from_user)
    bot.send_message(call.from_user.id, cfg["messages"]["create"], reply_markup=markup.create())


@bot.callback_query_handler(lambda call: call.data == "welcome_edit")
@bot.exception()
def edit(call: types.CallbackQuery):
    bot.send_message(call.from_user.id, "Пока не работает(", reply_markup=markup.welcome())


@bot.callback_query_handler(lambda call: call.data == "welcome_remove")
@bot.exception()
def remove(call: types.CallbackQuery):
    bot.send_message(call.from_user.id, "Пока не работает(", reply_markup=markup.welcome())


@bot.callback_query_handler(lambda call: call.data.split('_')[0] == "create")
@bot.exception()
def create_handler(call: types.CallbackQuery):
    key = call.data.split('_')[1]

    @bot.exception()
    def add_temp_girl_key(message: types.Message):
        bot.add_temp_girl_key(key, call.from_user, message)

    if key in cfg["messages"]["add"].keys():
        bot.send_message(call.from_user.id, cfg["messages"]["add"][key])
        bot.register_next_step_handler(call.message, add_temp_girl_key)
    if key == "preview":
        bot.get_temp_girl_preview(call.from_user)
    if key == "save":
        bot.create_girl_for_user(call.from_user)
    if key == "back":
        welcome(call)


bot.polling(none_stop=True, interval=0)
