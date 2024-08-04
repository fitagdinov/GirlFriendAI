import io
import telebot
import logging
import asyncio

from datetime import datetime, timedelta

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

    def ban_check(self, user: types.User, type_: str):
        with Session(self.engine) as session:
            stmt = select(table.Ban).where(table.Ban.user_id == user.id, table.Ban.type == type_)
            ban: table.Ban | None = session.scalars(stmt).one_or_none()
            if ban is not None:
                expired_dt: datetime = ban.dt + timedelta(seconds=ban.seconds)
                delta = expired_dt - datetime.utcnow()
                if delta.seconds > 0:
                    raise exc.BanError(type_, delta.seconds)
                ban = session.get(table.Ban, ban.id)
                session.delete(ban)
                session.commit()

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

    def is_alpha_user(self, user: types.User) -> bool:
        with Session(self.engine) as session:
            if session.get(table.AlphaUser, user.username):
                return True
        return False

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

        async def async_client():
            client = Client("some_bot", session_string=account.string)
            async with client:
                try:
                    result = await client.invoke(functions.account.CheckUsername(username=username))
                except Exception:
                    raise exc.InvalidUsernameError()
            if not result:
                raise exc.NotAvailableUsernameError()

        asyncio.run(async_client())

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
                appearance=temp_girl.appearance,
                username=temp_girl.username,
                interests=temp_girl.interests
            )
            if temp_girl.photo_file_id:
                self.send_photo(user.id, temp_girl.photo_file_id, text, reply_markup=markup.create(), parse_mode="HTML")
            else:
                self.send_message(user.id, text, reply_markup=markup.create(), parse_mode="HTML")

    def create_girl_for_user(self, user: types.User):
        async def create_bot(account_string: str, girl: table.TempGirl | None) -> str:
            client = Client("create_bot", session_string=account_string)
            bot_father = "BotFather"
            async with client:
                await client.send_message(bot_father, "/newbot")
                await asyncio.sleep(1)
                async for msg in client.get_chat_history(bot_father, 1):
                    if msg.text.startswith("Sorry, too many attempts."):
                        seconds_to_wait = int(''.join([x for x in msg.text if x.isdigit()]))
                        raise exc.TooManyAttemptsError(seconds_to_wait)

                await client.send_message(bot_father, girl.first_name)
                await asyncio.sleep(1)
                async for msg in client.get_chat_history(bot_father, 1):
                    if not msg.text.startswith("Good."):
                        raise exc.InvalidNameError(cfg["limitations"]["name_len"]["min"],
                                                   cfg["limitations"]["name_len"]["max"])

                await client.send_message(bot_father, girl.username)
                await asyncio.sleep(1)
                async for msg in client.get_chat_history(bot_father, 1):
                    if not msg.text.startswith("Done!"):
                        raise exc.InvalidUsernameError()
                    token_str = msg.text.markdown[msg.text.markdown.find('`') + 1:msg.text.markdown.rfind('`')]

                if girl.photo_file_id:
                    await client.send_message(bot_father, "/setuserpic")
                    await asyncio.sleep(1)
                    await client.send_message(bot_father, f"@{girl.username}")
                    await asyncio.sleep(1)
                    file_info = self.get_file(str(girl.photo_file_id))
                    file = self.download_file(file_info.file_path)
                    await client.send_photo(bot_father, io.BytesIO(file))
                    await asyncio.sleep(1)

                if girl.age:
                    await client.send_message(bot_father, "/setabouttext")
                    await asyncio.sleep(1)
                    await client.send_message(bot_father, f"@{girl.username}")
                    await asyncio.sleep(1)
                    await client.send_message(bot_father, f"{girl.age} y.o.")
                    await asyncio.sleep(1)

                return token_str

        if not self.is_alpha_user(user):
            raise exc.NotAlphaUserError()

        self.ban_check(user, "create")

        with Session(self.engine) as session:
            temp_girl = session.get(table.TempGirl, user.id)

            if not all([temp_girl.first_name, temp_girl.age, temp_girl.appearance,
                        temp_girl.photo_file_id, temp_girl.username, temp_girl.interests]):
                raise exc.NotAllParamsFilledError()

            stmt = select(table.Account).where(table.Account.bots_num < 20)
            account: table.Account | None = session.scalars(stmt).one_or_none()

            if account is None:
                raise exc.NoFreeBotsError()

            self.send_message(user.id, cfg["callback_messages"]["save_processing"])

            token_string = asyncio.run(create_bot(account.string, temp_girl))
            token_id = int(token_string.split(":")[0])

            girl_to_add = table.Girl(
                id=token_id,
                owner_id=user.id,
                account_id=account.id,
                token=token_string,
                is_active=1,
                username=temp_girl.username,
                first_name=temp_girl.first_name,
                age=temp_girl.age,
                photo_file_id=temp_girl.photo_file_id,
                appearance=temp_girl.appearance,
                interests=temp_girl.interests
            )

            session.add(girl_to_add)
            session.commit()

            account.bots_num += 1
            session.add(account)
            session.commit()

            session.delete(temp_girl)
            session.commit()

            ban = table.Ban(user_id=user.id, type="create")
            session.add(ban)
            session.commit()

        self.send_message(user.id, cfg["callback_messages"]["save"], reply_markup=markup.welcome())

    def get_girls_names(self, user: types.User) -> list[str]:
        with Session(self.engine) as session:
            stmt = select(table.Girl).where(table.Girl.owner_id == user.id)
            girls = session.scalars(stmt).all()
            if len(girls) == 0:
                raise exc.NoCreatedGirlsError()
        return [girl.username for girl in girls]

    def remove_girl(self, user: types.User, girl_username: str):
        async def delete_bot(account_string: str, username: str):
            client = Client("create_bot", session_string=account_string)
            bot_father = "BotFather"
            async with client:
                await client.send_message(bot_father, "/deletebot")
                await asyncio.sleep(1)

                await client.send_message(bot_father, f"@{username}")
                await asyncio.sleep(1)
                async for msg in client.get_chat_history(bot_father, 1):
                    if msg.text.startswith("Invalid bot selected:"):
                        raise exc.IncorrectGirlUsernameError()

                await client.send_message(bot_father, "Yes, I am totally sure.")

        self.ban_check(user, "remove")

        with Session(self.engine) as session:
            stmt = select(table.Girl).where(table.Girl.owner_id == user.id, table.Girl.username == girl_username[1:])
            girl: table.Girl | None = session.scalars(stmt).one_or_none()
            if girl is None:
                raise exc.NoCreatedGirlsError()

            girl = session.get(table.Girl, girl.id)
            account = session.get(table.Account, girl.account_id)

            asyncio.run(delete_bot(account.string, girl.username))

            session.delete(girl)
            session.commit()

            account.bots_num -= 1
            session.add(account)
            session.commit()

            ban = table.Ban(user_id=user.id, type="remove")
            session.add(ban)
            session.commit()

        self.send_message(user.id, cfg["callback_messages"]["remove"], reply_markup=markup.welcome())
