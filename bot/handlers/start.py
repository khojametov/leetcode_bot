from aiogram import Router, types

from bot.keyboards.reply import main_menu

router = Router()


@router.message(commands="start")
async def start(message: types.Message):
    await message.answer(text="Hi this is leetcode bot", reply_markup=main_menu())
