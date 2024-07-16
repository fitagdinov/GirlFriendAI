from dataclasses import dataclass
from telebot import types


@dataclass
class Content:
    text: str

    @property
    def markup(self) -> types.InlineKeyboardMarkup | None:
        return None


@dataclass
class WelcomeMenuContent(Content):
    text: str = "Привет! Это главный GirlFriendAI бот, который создает AI девушек для общения с ними."

    @property
    def markup(self) -> types.InlineKeyboardMarkup:
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(types.InlineKeyboardButton("🍓 Создать AI девушку", callback_data="welcome_create"))
        markup.add(types.InlineKeyboardButton("🍒 Изменить AI девушку", callback_data="welcome_edit"))
        markup.add(types.InlineKeyboardButton("🍎 Удалить AI девушку", callback_data="welcome_remove"))
        return markup


@dataclass
class CreateMenuContent(Content):
    text: str = "Создадим твою идеальную девушку!"

    create_text = {
        "name": "Введите имя девушки. Длина имени - не более 10 символов.",
        "age": "Введите возраст девушки. Возраст должен быть больше 18 лет.",
        "face": "Отправьте фото предпочитаемого лица девушки.",
        "features": "Опишите ее внешность, например 'голубые глаза, узкая талия' и т.д."
    }

    done_text = {
        "name": "Имя успешно сохранено!",
        "age": "Возраст успешно сохранен!",
        "face": "Фото успешно сохранено!",
        "features": "Описание внешности успешно сохранено!",
        "save": "Поздравляем! Ваша AI девушка создана! В скором времени она Вам напишет."
    }

    exception_text = {
        "quota": "Нельзя создать еще одну девушку. Максимальное количество девушек для вас: {quota}.",
        "temp_exists": "Вы уже создаете девушку.",
        "long_name": "Имя должно быть не более 10 символов.",
        "age_not_valid": "Возраст должен быть числом больше 18.",
        "long_features": "Описание должно содержать не более 50 символов.",
        "photo": "Необходимо отправить одну фотографию.",
        "save_none": "Не все данные заполнены.",
        "no_free_tokens": "Нет свободных ботов."
    }

    preview_template = \
        "Вот, что уже есть:\n*Имя*: {name}\n*Возраст*: {age}\n*Внешность*: {features}"

    @property
    def markup(self) -> types.InlineKeyboardMarkup:
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(types.InlineKeyboardButton("📝 Имя", callback_data="create_name"),
                   types.InlineKeyboardButton("🔞 Возраст", callback_data="create_age"))
        markup.add(types.InlineKeyboardButton("👩‍🦰 Лицо", callback_data="create_face"),
                   types.InlineKeyboardButton("💁‍♀️ Внешность", callback_data="create_features"))
        markup.add(types.InlineKeyboardButton("🔎 Превью", callback_data="create_preview"),
                   types.InlineKeyboardButton("✏️ Сохранить", callback_data="create_save"))
        markup.add(types.InlineKeyboardButton("⬅️ Назад", callback_data="create_back"))
        return markup



