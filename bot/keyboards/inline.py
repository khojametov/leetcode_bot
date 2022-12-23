from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def confirm_button():
    yes = InlineKeyboardButton(text="✅", callback_data="send")
    no = InlineKeyboardButton(text="❌", callback_data="cancel")
    return InlineKeyboardMarkup(inline_keyboard=[[yes, no]])
