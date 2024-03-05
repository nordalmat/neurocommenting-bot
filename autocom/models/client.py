import sys
from os.path import dirname
from pathlib import Path
import json
from pyrogram.client import Client
from pyrogram.types import Chat


class CustomClient(Client):

    PARENT_DIR = dirname(sys.executable) if getattr(
        sys, 'frozen', False) else Path(sys.argv[0]).parent

    def __init__(self, id: int, prompt: str, is_active: bool, ignore_step: int, *args, **kwargs):
        super(CustomClient, self).__init__(*args, **kwargs)
        self.id = id
        self.prompt = prompt
        self.is_active = is_active
        self.ignore_step = ignore_step

        self.comment_count_by_chat = {}
        self.ban_list = set()

    def add_to_banlist(self, chat: Chat, json_reader_data: dict):
        self.ban_list.add(chat)
        self._write_to_json_bans(json_reader_data)

    def _write_to_json_bans(self, json_reader_data: dict):
        json_reader_data["clients"][self.id]["banListId"] = []
        for chat in self.ban_list:
            json_reader_data["clients"][self.id]["banListId"].append(
                f"{chat.title}::@{chat.username}")
        with open(self.application_path + '/view.json', 'w', encoding='utf-8') as f:
            json.dump(json_reader_data, f, ensure_ascii=False, indent=4)
