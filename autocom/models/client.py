import sys
from os.path import dirname
from pathlib import Path

from pyrogram.client import Client


class CustomClient(Client):
    
    PARENT_DIR = dirname(sys.executable) if getattr(sys, 'frozen', False) else Path(sys.argv[0]).parent

    def __init__(self, prompt: str, is_active: bool, ignore_step: int, *args, **kwargs):
        super(CustomClient, self).__init__(*args, **kwargs)
        self.prompt = prompt
        self.is_active = is_active
        self.ignore_step = ignore_step

        self.comment_count_by_chat = {}
        self.ban_list = set()