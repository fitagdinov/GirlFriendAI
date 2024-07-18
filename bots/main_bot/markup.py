from telebot import types


def welcome() -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("🍓 Создать AI девушку", callback_data="welcome_create"))
    markup.add(types.InlineKeyboardButton("🍒 Изменить AI девушку", callback_data="welcome_edit"))
    markup.add(types.InlineKeyboardButton("🍎 Удалить AI девушку", callback_data="welcome_remove"))
    return markup


def create() -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton("📝 Имя", callback_data="create_name"),
               types.InlineKeyboardButton("🔞 Возраст", callback_data="create_age"))
    markup.add(types.InlineKeyboardButton("👩‍💻 Ник", callback_data="create_username"),
               types.InlineKeyboardButton("💃🏽 Интересы", callback_data="create_interests"))
    markup.add(types.InlineKeyboardButton("👩‍🦰 Фото", callback_data="create_face"),
               types.InlineKeyboardButton("💁‍♀️ Внешность", callback_data="create_appearance"))
    markup.add(types.InlineKeyboardButton("🔎 Превью", callback_data="create_preview"),
               types.InlineKeyboardButton("✏️ Сохранить", callback_data="create_save"))
    markup.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="create_back"))
    return markup
