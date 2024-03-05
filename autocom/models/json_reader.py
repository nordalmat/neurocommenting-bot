import json
import sys
from os.path import dirname
from typing import Any, Optional


class JSONClient:
    def __getitem__(self, __key: object) -> Any: ...

    def get_id(self) -> int:
        return int(self.id)

    def get_name(self) -> str:
        return str(self["name"])

    def get_api_id(self) -> str:
        return str(self["apiId"])

    def get_api_hash(self) -> str:
        return str(self["apiHash"])

    def get_prompt(self) -> str:
        return str(self["gptPrompt"])

    def get_active_status(self) -> bool:
        return self["isActive"] == 1

    def get_ignore_step(self) -> int:
        return int(self["countOfIgnoredPostBetweenExecutions"])

    def get_ban_list(self) -> list[int]:
        return self["banListId"]


class JSONReader:
    def __init__(self) -> None:
        if getattr(sys, 'frozen', False):
            application_path = dirname(dirname(sys.executable))
        else:
            application_path = dirname(dirname(dirname(__file__)))

        with open(application_path + '/view.json', encoding='utf-8') as f:
            self.data = json.load(f)

    def get_data(self) -> dict:
        return self.data

    def get_clients_data(self) -> list[JSONClient]:
        return self.data["clients"]

    def get_open_ai_api_key(self) -> Optional[str]:
        if len(self.data["apiKeys"]) > 0:
            return self.data["apiKeys"][0]["key"]
        return None

    def get_settings(self) -> dict:
        return self.data["settings"]


json_reader = JSONReader()
