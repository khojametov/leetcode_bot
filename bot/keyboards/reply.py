from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def back_to_main_menu():
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton("Back to main menu"))
    return builder.as_markup(resize_keyboard=True)


def main_menu():
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton("Register"))
    builder.add(KeyboardButton("My profile"))
    builder.add(KeyboardButton("Contact to admins"))
    builder.add(KeyboardButton("Rating"))
    return builder.as_markup(rezie_keyboard=True)
