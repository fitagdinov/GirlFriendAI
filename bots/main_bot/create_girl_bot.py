from telethon.sync import TelegramClient
from telethon.sessions import StringSession

from db.create_db import get_engine
from sqlalchemy.orm import Session
from db import table

engine = get_engine()
session = Session(engine)

account = session.get(table.Account, 7370993562)

# client = TelegramClient(StringSession(string), api_id, api_hash)
with TelegramClient(StringSession(account.string), account.api_id, account.api_hash) as client:
    client: TelegramClient
    bot_father = "BotFather"
    client.send_message(bot_father, "/newbot")


