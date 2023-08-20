from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

ACCEPTED = "✅"
DECLINED = "❌"
DECLINE_MESSAGE = "Admins declined your request to join the group due to incorrect information"
NOT_CLICKED = "None of the buttons were clicked"


ACCEPT = "accept"
DECLINE = "decline"


def confirm_button():
    yes = InlineKeyboardButton(text="✅", callback_data=ACCEPT)
    no = InlineKeyboardButton(text="❌", callback_data=DECLINE)
    return InlineKeyboardMarkup(inline_keyboard=[[yes, no]])
