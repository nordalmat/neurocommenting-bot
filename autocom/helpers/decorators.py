from typing import Callable

import pyrogram
from pyrogram.filters import Filter


def list_on_message(
        lst: list,
        filters: Filter,
        group: int = 0
    ) -> Callable:
        """Decorator for handling new messages of the Clients in a list.

        This does the same thing as :meth:`~pyrogram.Client.add_handler` using the
        :obj:`~pyrogram.handlers.MessageHandler` on eventy Client inside a list.

        Parameters:
            filters (:obj:`~pyrogram.filters`, *optional*):
                Pass one or more filters to allow only a subset of messages to be passed
                in your function.

            group (``int``, *optional*):
                The group identifier, defaults to 0.
        """

        def decorator(func: Callable) -> Callable:
            for client in lst:
                if isinstance(client, pyrogram.client.Client):
                    client.add_handler(pyrogram.handlers.message_handler.MessageHandler(func, filters), group)
                elif isinstance(client, Filter) or client is None:
                    if not hasattr(func, "handlers"):
                        func.handlers = []
                    func.handlers.append(
                        (
                            pyrogram.handlers.message_handler.MessageHandler(func, client),
                            group if filters is None else filters
                        )
                    )
            return func

        return decorator
