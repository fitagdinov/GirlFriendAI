from telebot import types
from sqlalchemy.orm import Session
from sqlalchemy import select

from bot.main_bot.content import Content, CreateMenuContent, WelcomeMenuContent
from db import table


class Menu:
    content: Content

    def __init__(self, session: Session):
        self.session = session


class WelcomeMenu(Menu):
    content = WelcomeMenuContent()

    def add_user_if_not_exists(self, user: types.User):
        if self.session.get(table.User, user.id) is None:
            user_to_add = table.User(
                id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                quota=1
            )
            self.session.add(user_to_add)
            self.session.commit()


class CreateMenu(Menu):
    content = CreateMenuContent()

    def add_temp_girl_for_user(self, user: types.User) -> str | None:
        stmt = select(table.Girl).where(table.Girl.owner_id == user.id)
        num_of_girls = self.session.scalars(stmt).all().__len__()
        quota = self.session.get(table.User, user.id).quota
        if quota <= num_of_girls:
            return self.content.exception_text["quota"].format(quota=quota)
        else:
            if self.session.get(table.TempGirl, user.id) is not None:
                return self.content.exception_text["temp_exists"]
            else:
                temp_girl_to_add = table.TempGirl(owner_id=user.id)
                self.session.add(temp_girl_to_add)
                self.session.commit()

    def add_temp_girl_param(self, key: str, user: types.User, message: types.Message) -> str:
        if key == "name":
            return self.add_temp_girl_name(user, message)
        elif key == "age":
            return self.add_temp_girl_age(user, message)
        elif key == "features":
            return self.add_temp_girl_features(user, message)
        elif key == "face":
            return self.add_temp_girl_face(user, message)

    def add_temp_girl_name(self, user: types.User, message: types.Message) -> str:
        temp_girl = self.session.get(table.TempGirl, user.id)
        if len(message.text) >= 10:
            return self.content.exception_text["long_name"]
        else:
            temp_girl.first_name = message.text
            self.session.add(temp_girl)
            self.session.commit()
            return self.content.done_text["name"]

    def add_temp_girl_age(self, user: types.User, message: types.Message) -> str:
        temp_girl = self.session.get(table.TempGirl, user.id)
        if not message.text.isdigit() or int(message.text) < 18:
            return self.content.exception_text["age_not_valid"]
        else:
            temp_girl.age = message.text
            self.session.add(temp_girl)
            self.session.commit()
            return self.content.done_text["age"]

    def add_temp_girl_face(self, user: types.User, message: types.Message) -> str:
        temp_girl = self.session.get(table.TempGirl, user.id)
        if message.photo is None:
            return self.content.exception_text["photo"]
        else:
            temp_girl.photo_path = f"../../data/temp/photo_{user.id}.jpg"
            self.session.add(temp_girl)
            self.session.commit()
            return self.content.done_text["face"]

    def add_temp_girl_features(self, user: types.User, message: types.Message) -> str:
        temp_girl = self.session.get(table.TempGirl, user.id)
        if len(message.text) >= 50:
            return self.content.exception_text["long_features"]
        else:
            temp_girl.features = message.text
            self.session.add(temp_girl)
            self.session.commit()
            return self.content.done_text["features"]

    def preview_temp_girl(self, user: types.User) -> str:
        temp_girl = self.session.get(table.TempGirl, user.id)
        params = {
            "name": temp_girl.first_name,
            "age": temp_girl.age,
            "features": temp_girl.features
        }
        return self.content.preview_template.format(**params)

    def save_temp_girl(self, user: types.User) -> str:
        temp_girl = self.session.get(table.TempGirl, user.id)
        if any([temp_girl.first_name, temp_girl.age, temp_girl.features, temp_girl.photo_path]) is None:
            return self.content.exception_text["save_none"]
        else:
            stmt = select(table.Token).where(table.Token.is_free == 1)
            token = self.session.scalars(stmt).one_or_none()
            if token is None:
                return self.content.exception_text["no_free_tokens"]
            else:
                girl_to_add = table.Girl(
                    id=token.id,
                    owner_id=user.id,
                    token=token.token,
                    username=token.username,
                    first_name=temp_girl.first_name,
                    age=temp_girl.age,
                    photo_path=temp_girl.photo_path,
                    features=temp_girl.features
                )
                self.session.add(girl_to_add)
                self.session.commit()
                return self.content.done_text["save"]
