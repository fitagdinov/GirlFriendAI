from telebot import types
from bots.main_bot import markup


class UnknownError(Exception):
    def __init__(self):
        text = f"Возникла ошибка. Попробуйте снова"
        super().__init__(text)


class KnownError(Exception):
    markup: types.InlineKeyboardMarkup = None


class CreateError(KnownError):
    markup = markup.create()


class WelcomeError(KnownError):
    markup = markup.welcome()


class InvalidNameError(CreateError):
    def __init__(self, min_len: int, max_len: int):
        text = f"Имя должно состоять из букв и содержать от {min_len} до {max_len} символов."
        super().__init__(text)


class InvalidUsernameError(CreateError):
    def __init__(self):
        text = f"Ник должен соответствовать правилам Telegram и заканчиваться на `bot`."
        super().__init__(text)


class NotAvailableUsernameError(CreateError):
    def __init__(self):
        text = f"Этот ник уже занят."
        super().__init__(text)


class InvalidAppearanceError(CreateError):
    def __init__(self, min_len: int, max_len: int):
        text = f"Описание внешности должно состоять из слов, разделенных пробелами, и " \
               f"содержать от {min_len} до {max_len} символов."
        super().__init__(text)


class InvalidInterestsError(CreateError):
    def __init__(self, min_len: int, max_len: int):
        text = f"Текст интересов девушке должен состоять из слов, разделенных пробелами, и " \
               f"содержать от {min_len} до {max_len} символов."
        super().__init__(text)


class InvalidAgeError(CreateError):
    def __init__(self, min_age: int, max_age: int):
        text = f"Возраст должен быть числом и лежать в диапазоне от {min_age} до {max_age} лет."
        super().__init__(text)


class InvalidPhotoError(CreateError):
    def __init__(self):
        text = f"Необходимо отправить фото лица."
        super().__init__(text)


class QuotaError(KnownError):
    def __init__(self, quota: int):
        text = f"Нельзя создать еще одну девушку. Максимальное количество девушек для вас: {quota}."
        super().__init__(text)


class AlreadyCreatingError(CreateError):
    def __init__(self):
        text = "Вы уже создаете девушку."
        super().__init__(text)


class NotAllParamsFilledError(CreateError):
    def __init__(self):
        text = "Не все данные заполнены."
        super().__init__(text)


class NoFreeBotsError(KnownError):
    def __init__(self):
        text = "Нет доступных ботов."
        super().__init__(text)

