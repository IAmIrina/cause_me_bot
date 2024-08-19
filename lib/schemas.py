import typing as t

from pydantic import BaseModel
from enum import Enum


class From(BaseModel):
    id: int
    username: str = None
    first_name: str = None
    last_name: str = None


class Chat(BaseModel):
    id: int


class Message(BaseModel):
    text: str
    from_: From
    message_id: int
    chat: Chat

    class Config:
        fields = {
            'from_': 'from'
        }


class Callback(BaseModel):
    data: str
    message: Message


class TLGResponse(BaseModel):
    text: str
    reply_markup: dict = None
    parse_mode: t.Literal['MarkdownV2'] = None


class Button(BaseModel):
    text: str
    callback_data: str


class Commands(Enum):
    ADD = '/add'
    DELETE = '/del'
    START = '/start'
    HELP = '/help'
    REPEATED = '/repeated'
    MORE = '/more'
    REGISTER_COMMANDS = '/register'
    STATISTICS = '/statistics'


class Keyboards():
    @staticmethod
    def get_inline_keyboard(buttons: t.List[Button]) -> dict:
        return {
            'inline_keyboard': [
                [
                    dict(button) for button in buttons
                ],
            ]
        }
