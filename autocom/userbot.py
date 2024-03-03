import asyncio
import sys
from asyncio.queues import Queue

import nest_asyncio
from helpers.decorators import list_on_message
from helpers.logger import extensive_log, simple_log
from models.client import CustomClient
from models.json_reader import json_reader
from models.post import TextPost
from pyrogram import enums, filters
from pyrogram.errors.exceptions import ChannelPrivate
from pyrogram.sync import idle
from pyrogram.types import Message


nest_asyncio.apply()
sys.path.append("autocom/userbot.py") 

apps: list[CustomClient] = []
for client in json_reader.get_clients_data():
    app = CustomClient(name="data/" + client["name"],
                        api_id=int(client["apiId"]),
                        api_hash=client["apiHash"],
                        prompt=client["gptPrompt"],
                        is_active=bool(client["isActive"]),
                        ignore_step=int(client["countOfIgnoredPostBetweenExecutions"]))
    apps.append(app)



last_media_group = 1000000
queue = Queue()
length_delay = 0
length = 0



@list_on_message(apps, filters.channel)
async def answer(client: CustomClient, message: Message):
    if message is None or (message.text is None and message.caption is None): return
    message_text = message.text if message.text is not None else message.caption
    global last_media_group, queue, length_delay
    message_log = message_text.replace(
        "\n", "")[:40] + '..' if message_text is not None else str()

    if last_media_group == message.media_group_id and message.media_group_id is not None:
        simple_log.debug(
            f"|{message.chat.title}|{client.name}|Skipping message. (media group: last - {last_media_group}, message - {message.media_group_id}).")
        extensive_log.debug(
            f"|{message.chat.title}|{client.name}|Skipping message. (media group: last - {last_media_group}, message - {message.media_group_id}).")
        return
    
    client.comment_count_by_chat[message.chat.id] = client.comment_count_by_chat.get(message.chat.id, 0) + 1
    if (client.comment_count_by_chat[message.chat.id] - 1) % client.ignore_step != 0:
        simple_log.info(
            f"|{message.chat.title}|{client.name}|:Caught message. (Text: {message_log}) - skipping, current message count is {client.comment_count_by_chat[message.chat.id] - 1}")
        extensive_log.info(
            f"|{message.chat.title}|{client.name}|:Caught message. (Text: {message_log}) - skipping, current message count is {client.comment_count_by_chat[message.chat.id] - 1}")
        return

    simple_log.info(
        f"|{message.chat.title}|{client.name}|:Caught message. (Text: {message_log}) - answering")
    await queue.put(message)

    await asyncio.sleep(10)
    last_media_group = message.media_group_id
    curr = await queue.get()
    linked = await get_linked(curr, client)
    if linked:
        message_to_answer = await get_forwarded_in_linked(linked, client, curr)
    else:
        return
    if message_to_answer is None:
        simple_log.error(
            f"|{message.chat.title}|{client.name}|:Banned or couldn't get comments.")
        extensive_log.error(
            f"|{message.chat.title}|{client.name}|:Banned or couldn't get comments.")
        return
    length_delay += 1
    post = TextPost(length_delay)
    await asyncio.sleep(10)
    response = await post.reply_to(message_to_answer, client)
    length_delay -= 1
    if response is None:
        return
    simple_log.info(f"|{message.chat.title}|{client.name}|:Answered: " + response)
    extensive_log.info(f"|{message.chat.title}|{client.name}|\nPost content: " + message_text.replace("\n\n", "\n") + "\nAnswer: " + response + "\n")


async def get_linked(msg, app):
    channel = await app.get_chat(msg.sender_chat.id)
    return channel.linked_chat


async def get_forwarded_in_linked(linked, app, msg):
    first_msg = True
    return_msg = None
    try:
        async for message in app.search_messages(linked.id, limit=10, filter=enums.MessagesFilter.PINNED):
            if message.forward_from_message_id == msg.id:
                return message
            if first_msg:
                first_msg = False
                return_msg = message
        return return_msg
    except ChannelPrivate:
        return None   
    
    
async def main():
    simple_log.info('Started!')
    extensive_log.info('Session started')
    for app in apps:
        if app.is_active:
            await app.start()
    await idle()
    for app in apps:
        if app.is_active:
            await app.stop()


if __name__ == '__main__':
    asyncio.run(main())
