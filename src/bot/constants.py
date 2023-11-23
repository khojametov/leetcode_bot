from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

# Bot commands
START = "start"
REGISTER = "register"
MY_PROFILE = "my_profile"
ADMINS = "admins"
RATING = "rating"


# Messages
DECLINE_MESSAGE = (
    "Admins declined your request to join the group due to incorrect information"
)
NOT_CLICKED = "None of the buttons were clicked"
ACCEPT = "accept"
DECLINE = "decline"

# Buttons
ACCEPTED = "✅"
DECLINED = "❌"
YES = InlineKeyboardButton(text=ACCEPTED, callback_data=ACCEPT)
NO = InlineKeyboardButton(text=DECLINED, callback_data=DECLINE)
CONFIRM_BUTTON = InlineKeyboardMarkup(inline_keyboard=[[YES, NO]])
