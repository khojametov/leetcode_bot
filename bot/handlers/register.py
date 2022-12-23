from datetime import datetime, timedelta

from aiogram import Router, F, types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, CallbackQuery
from sqlalchemy import select

from bot.keyboards.inline import confirm_button
from bot.keyboards.reply import main_menu
from src.bot import redis
from src.config import settings
from src.database import db
from src.models import Link

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


@router.callback_query(lambda call: True)
async def callback_inline(call: CallbackQuery, bot: Bot):
    if str(call.from_user.id) not in settings.admins:
        return

    if call.message:
        chat_id = int(call.message.html_text[9:].split("\n")[0])
        text = "None of the buttons were clicked"

        if call.data == "send":
            tomorrow = datetime.now() + timedelta(days=1)
            query = select(Link).filter(
                Link.chat_id == chat_id, Link.expire_date > datetime.now()
            )
            result = await db.execute(query)
            link = result.scalars().first()
            if not link:
                link = await bot.create_chat_invite_link(
                    chat_id=settings.group_id,
                    expire_date=tomorrow,
                    creates_join_request=True,
                )
                db.add(
                    Link(
                        chat_id=chat_id,
                        invite_link=link["invite_link"],
                        expire_date=tomorrow,
                    )
                )
                await db.commit()
                link = link["invite_link"]
            else:
                link = link["invite_link"]

            await call.message.answer(text=link)
            data = await redis.hgetall(chat_id)
            if data:
                data["approved"] = 1
                await redis.hset(chat_id, mapping=data)
            text = "✅"
        elif call.data == "cancel":
            await call.message.answer(
                text="Admins declined your request to join the group due to incorrect information",
            )
            text = "❌"

        await call.message.delete()
        message = await call.message.answer(text=text)
        await message.reply(text)
