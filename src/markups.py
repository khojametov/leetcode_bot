from aiogram.types import (
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.utils import markdown


class Markups:
    register = "Register"
    my_profile = "My profile"
    admins = "Contact to admins"
    back = "Back to main menu"

    def main_menu(self):
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(self.register)
        markup.add(self.my_profile)
        markup.add(self.admins)
        return markup

    def back_to_main_menu(self):
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(self.back)
        return markup

    def info(self, data):
        return markdown.text(
            markdown.text("Full name: ", markdown.bold(data["full_name"])),
            markdown.text(
                "Leetcode profile: ", markdown.bold(data["leetcode_profile"])
            ),
            sep="\n",
        )

    def confirm_button(self):
        yes = InlineKeyboardButton(text="✅", callback_data="send")
        no = InlineKeyboardButton(text="❌", callback_data="cancel")
        return InlineKeyboardMarkup(inline_keyboard=[[yes, no]])


markup = Markups()
