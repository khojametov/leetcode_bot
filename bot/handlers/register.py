from aiogram import Router, F, types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup

from bot.keyboards.inline import confirm_button
from bot.keyboards.reply import main_menu
from src.bot import redis
from src.config import settings

router = Router()


class Form(StatesGroup):
    full_name = State()
    leetcode_profile = State()
    confirm = State()


@router.message(F.text == "Register")
async def register(message: types.Message, state: FSMContext):
    await message.reply("What is your full name?")
    await state.set_state(Form.full_name)


@router.message(state=Form.full_name)
async def process_full_name(message: types.Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await message.reply("Enter your leetcode profile name")
    await state.set_state(Form.leetcode_profile)


@router.message(state=Form.leetcode_profile)
async def process_leetcode_profile(message: types.Message, state: FSMContext):
    await state.update_data(leetcode_profile=message.text)
    data = await state.get_data()

    markup = ReplyKeyboardMarkup(
        one_time_keyboard=True,
    )
    markup.add("Send", "Cancel")

    await message.answer(
        text="Chat id: {}\nUsername: @{}\nFull name: {}\nLeetcode profile: {}".format(
            message.chat.id,
            message.chat.username,
            data["full_name"],
            "https://leetcode.com/" + data["leetcode_profile"],
        ),
        reply_markup=markup,
    )
    await state.set_state(Form.confirm)


@router.message(state=Form.confirm)
async def confirm_data(message: types.Message, state: FSMContext, bot: Bot):
    if message.text == "Send":
        data = await state.get_data()
        await redis.hset(
            message.chat.id,
            mapping={
                "username": message.chat.username,
                "full_name": data["full_name"],
                "leetcode_profile": data["leetcode_profile"],
                "approved": 0,
            },
        )

        await bot.send_message(
            chat_id=settings.admins_group_id,
            text="Chat id: {}\nUsername: @{}\nFull name: {}\nLeetcode profile: {}".format(
                message.chat.id,
                message.chat.username,
                data["full_name"],
                "https://leetcode.com/" + data["leetcode_profile"],
            ),
            reply_markup=confirm_button(),
        )
        await message.reply("Thanks for registration", reply_markup=main_menu())
    elif message.text == "Cancel":
        await message.reply("Registration cancelled", reply_markup=main_menu())
    else:
        await message.reply("Please, use keyboard")

    await state.clear()
