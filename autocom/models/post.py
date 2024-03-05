import asyncio
import logging
import re

import pyrogram
from dotenv import load_dotenv
from helpers.logger import extensive_log, simple_log
from openai import OpenAI
from pyrogram.errors import Forbidden, SlowmodeWait

from .client import CustomClient
from .json_reader import json_reader

load_dotenv()

client = OpenAI(api_key=json_reader.get_open_ai_api_key())

settings = json_reader.get_settings()
contact_user_name = settings["contactUsername"]
send_ban_notifications = settings["sendBanNotifications"]
send_api_notifications = settings["sendApiKeyNotifications"]


def reply(func):
    async def wrapper(*args, **kwargs):
        try:
            result = await func(*args, **kwargs)
        except SlowmodeWait as sw:
            if sw.x > 30:
                logging.info(f'Script wont sleep {sw.x}s - >30s ({sw})')
                return
            logging.warning(f'Sleeping {sw.x}s due to {sw}')
            await asyncio.sleep(sw.x)
            result = await func(*args, **kwargs)
        await asyncio.sleep(0.25)
        return result
    return wrapper


class TextPost:
    def __init__(self, delay=1):
        self.delay = delay * 10 - 10

    @reply
    async def reply_to(self, message: pyrogram.types.Message, app: CustomClient):
        if message.caption or message.text:
            post_text = message.text if message.text else message.caption
        else:
            return
        content = app.prompt + post_text
        response = None
        await asyncio.sleep(self.delay)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            timeout=120,
            messages=[{"role": "user", "content": content}],
        )
        if response is None:
            if send_api_notifications:
                await app.send_message(contact_user_name, f"GPT returned nothing, if message persists, then your OpenAI's API key expired")
            simple_log.error(
                f"|{message.chat.title}|{app.name}|GPT returned nothing")
            extensive_log.error(
                f"|{message.chat.title}|{app.name}|GPT returned nothing")
            return
        remove_dot_pattern = re.compile(r"^[^\w\s]*|[^\w\s]*?$")
        msg_response = remove_dot_pattern.sub(
            "", str(response.choices[0].message.content))
        try:
            await app.send_message(message.chat.id, msg_response, reply_to_message_id=message.id)
        except Forbidden as fb:
            simple_log.error(
                f"|{message.chat.title}|{app.name}|Can't send comments as chat is forbidden for guests")
            extensive_log.error(
                f"|{message.chat.title}|{app.name}|Can't send comments as chat is forbidden for guests")
            if send_ban_notifications:
                await client.send_message(contact_user_name, f"I couldn't send comment at {message.chat.title} (@{message.chat.username}), chat is forbidden for guests")
        return msg_response
