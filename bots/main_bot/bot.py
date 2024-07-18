import telebot
import logging

from sqlalchemy import Engine, select
from sqlalchemy.orm import Session

from pyrogram.raw import functions
from pyrogram import Client

from telebot import types

from db import table

from bots.main_bot.content import exception as exc
from bots.main_bot.content import cfg
from bots.main_bot import markup


class MainBot(telebot.TeleBot):
    engine: Engine = None
    logger = logging.getLogger("MainBot")

    def exception(self):
        def decorator(func):
            def wrapper(message_or_call: types.Message | types.CallbackQuery):
                try:
                    func(message_or_call)
                except exc.KnownError as e:
                    self.send_message(message_or_call.from_user.id, str(e), reply_markup=e.markup)
                except Exception as e:
                    self.send_message(message_or_call.from_user.id, str(exc.UnknownError()))
                    self.logger.error(e)

            return wrapper
        return decorator

    def set_engine(self, engine: Engine):
        self.engine = engine
        self.parse_mode = "Markdown"

    def add_user_if_not_exists(self, user: types.User):
        with Session(self.engine) as session:
            if session.get(table.User, user.id) is None:
                user_to_add = table.User(
                    id=user.id,
                    username=user.username,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    quota=1
                )
                session.add(user_to_add)
                session.commit()

    def create_temp_girl_for_user(self, user: types.User):
        with Session(self.engine) as session:
            stmt = select(table.Girl).where(table.Girl.owner_id == user.id)
            num_of_girls = session.scalars(stmt).all().__len__()
            quota = session.get(table.User, user.id).quota

            if quota <= num_of_girls:
                raise exc.QuotaError(quota)
            if session.get(table.TempGirl, user.id) is not None:
                raise exc.AlreadyCreatingError()

            temp_girl_to_add = table.TempGirl(owner_id=user.id)
            session.add(temp_girl_to_add)
            session.commit()

    def add_temp_girl_name(self, user: types.User, message: types.Message):
        name = message.text
        min_len = cfg["limitations"]["name_len"]["min"]
        max_len = cfg["limitations"]["name_len"]["max"]

        if name is None:
            raise exc.InvalidNameError(min_len, max_len)
        if not name.isalpha():
            raise exc.InvalidNameError(min_len, max_len)
        if not (min_len <= len(name) <= max_len):
            raise exc.InvalidNameError(min_len, max_len)

        with Session(self.engine) as session:
            temp_girl = session.get(table.TempGirl, user.id)
            temp_girl.first_name = name
            session.add(temp_girl)
            session.commit()
            self.send_message(user.id, cfg["callback_messages"]["add"]["name"], reply_markup=markup.create())

    def add_temp_girl_username(self, user: types.User, message: types.Message):
        username = message.text

        min_len = cfg["limitations"]["username_len"]["min"]
        max_len = cfg["limitations"]["username_len"]["max"]

        if username is None:
            raise exc.InvalidUsernameError()
        if not (min_len <= len(username) <= max_len):
            raise exc.InvalidUsernameError()
        if username[-3:].lower() != "bot":
            raise exc.InvalidUsernameError()

        with Session(self.engine) as session:
            account: table.Account = session.scalars(select(table.Account)).one()

        with Client("some_bot", session_string=account.string) as client:
            try:
                result = client.invoke(functions.account.CheckUsername(username=username))
            except Exception as e:
                raise exc.InvalidUsernameError()

        if not result:
            raise exc.NotAvailableUsernameError()

        with Session(self.engine) as session:
            temp_girl = session.get(table.TempGirl, user.id)
            temp_girl.username = username
            session.add(temp_girl)
            session.commit()
            self.send_message(user.id, cfg["callback_messages"]["add"]["username"], reply_markup=markup.create())

    def add_temp_girl_age(self, user: types.User, message: types.Message):
        age = message.text
        min_age = cfg["limitations"]["age"]["min"]
        max_age = cfg["limitations"]["age"]["max"]

        if age is None:
            raise exc.InvalidAgeError(min_age, max_age)
        if not (min_age <= int(age) <= max_age):
            raise exc.InvalidAgeError(min_age, max_age)

        with Session(self.engine) as session:
            temp_girl = session.get(table.TempGirl, user.id)
            temp_girl.age = age
            session.add(temp_girl)
            session.commit()
            self.send_message(user.id, cfg["callback_messages"]["add"]["age"], reply_markup=markup.create())

    def add_temp_girl_appearance(self, user: types.User, message: types.Message):
        appearance = message.text
        min_len = cfg["limitations"]["appearance_len"]["min"]
        max_len = cfg["limitations"]["appearance_len"]["max"]

        if appearance is None:
            raise exc.InvalidAppearanceError(min_len, max_len)
        if not all(x.isspace() or x.isalpha() or x.isdigit() or x == "," for x in appearance):
            raise exc.InvalidAppearanceError(min_len, max_len)
        if not (min_len <= len(appearance) <= max_len):
            raise exc.InvalidAppearanceError(min_len, max_len)

        with Session(self.engine) as session:
            temp_girl = session.get(table.TempGirl, user.id)
            temp_girl.appearance = appearance
            session.add(temp_girl)
            session.commit()
            self.send_message(user.id, cfg["callback_messages"]["add"]["appearance"], reply_markup=markup.create())

    def add_temp_girl_interests(self, user: types.User, message: types.Message):
        interests = message.text
        min_len = cfg["limitations"]["interests_len"]["min"]
        max_len = cfg["limitations"]["interests_len"]["max"]

        if interests is None:
            raise exc.InvalidInterestsError(min_len, max_len)
        if not all(x.isspace() or x.isalpha() or x.isdigit() or x == "," for x in interests):
            raise exc.InvalidInterestsError(min_len, max_len)
        if not (min_len <= len(interests) <= max_len):
            raise exc.InvalidInterestsError(min_len, max_len)

        with Session(self.engine) as session:
            temp_girl = session.get(table.TempGirl, user.id)
            temp_girl.interests = interests
            session.add(temp_girl)
            session.commit()
            self.send_message(user.id, cfg["callback_messages"]["add"]["interests"], reply_markup=markup.create())

    def add_temp_girl_face(self, user: types.User, message: types.Message):
        face_photo = message.photo

        if face_photo is None:
            raise exc.InvalidPhotoError()

        file_id = face_photo[-1].file_id

        with Session(self.engine) as session:
            temp_girl = session.get(table.TempGirl, user.id)
            temp_girl.photo_file_id = file_id
            session.add(temp_girl)
            session.commit()
            self.send_message(user.id, cfg["callback_messages"]["add"]["face"], reply_markup=markup.create())

    def add_temp_girl_key(self, key: str, user: types.User, message: types.Message):
        if key == "name":
            self.add_temp_girl_name(user, message)
        if key == "age":
            self.add_temp_girl_age(user, message)
        if key == "appearance":
            self.add_temp_girl_appearance(user, message)
        if key == "face":
            self.add_temp_girl_face(user, message)
        if key == "username":
            self.add_temp_girl_username(user, message)
        if key == "interests":
            self.add_temp_girl_interests(user, message)

    def get_temp_girl_preview(self, user: types.User):
        with Session(self.engine) as session:
            temp_girl = session.get(table.TempGirl, user.id)
            text = cfg["callback_messages"]["preview"].format(
                age=temp_girl.age,
                name=temp_girl.first_name,
                appearance=temp_girl.appearance
            )
            if temp_girl.photo_file_id:
                self.send_photo(user.id, temp_girl.photo_file_id, text, reply_markup=markup.create())
            else:
                self.send_message(user.id, text, reply_markup=markup.create())

    def create_girl_for_user(self, user: types.User):
        with Session(self.engine) as session:
            temp_girl = session.get(table.TempGirl, user.id)

            if not all([temp_girl.first_name, temp_girl.age, temp_girl.appearance, temp_girl.photo_file_id]):
                raise exc.NotAllParamsFilledError()

            stmt = select(table.Token).where(table.Token.is_free == 1)
            token = session.scalars(stmt).one_or_none()

            if token is None:
                raise exc.NoFreeBotsError()

            token = session.get(table.Token, token.id)

            girl_to_add = table.Girl(
                id=token.id,
                owner_id=user.id,
                token=token.token,
                username=token.username,
                first_name=temp_girl.first_name,
                age=temp_girl.age,
                photo_file_id=temp_girl.photo_file_id,
                appearance=temp_girl.appearance
            )
            session.add(girl_to_add)
            session.commit()
            self.send_message(user.id, cfg["callback_messages"]["save"], reply_markup=markup.welcome())

    def create_bots_for_account(self, account_id: int):
        with Session(self.engine) as session:
            account = session.get(table.Account, account_id)
            stmt = select(table.Token).where(table.Token.account_id == account_id)
            tokens = session.scalars(stmt).all()

        with sync.TelegramClient(StringSession(account.string), account.api_id, account.api_hash) as client:
            client: sync.TelegramClient
            bot_father = "BotFather"
            client.send_message(bot_father, "/newbot")
            client.send_message(bot_father, "Default")
            client.send_message(bot_father, "Default")
