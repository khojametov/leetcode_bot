from datetime import datetime, timedelta

import aioredis
from aiogram import Bot, Dispatcher, types
from aiogram.utils import markdown
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, ParseMode

from markups import markup
from permissions import permissions

from settings import settings

TOKEN = settings.api_token

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

redis = aioredis.from_url("redis://localhost:6379/0", decode_responses=True)


class Form(StatesGroup):
    full_name = State()
    leetcode_profile = State()
    confirm = State()


@dp.message_handler(commands="start")
@permissions.private_chat()
async def start(message: types.Message):
    username = message.chat.username
    if not username:
        await message.answer("Please, set your username in Telegram settings")

    await bot.send_message(
        chat_id=message.chat.id, text="Hello World", reply_markup=markup.main_menu()
    )


@dp.message_handler(Text(equals=markup.register))
@permissions.private_chat()
async def register(message: types.Message):
    await Form.full_name.set()

    await message.reply("What is your full name?")


@dp.message_handler(Text(equals=markup.my_profile))
@permissions.private_chat()
async def my_profile(message: types.Message):
    profile_info = await redis.hgetall(message.chat.id)
    if not profile_info:
        await bot.send_message(
            message.chat.id,
            text="You have not registered yet",
        )
        return
    await bot.send_message(
        message.chat.id,
        text=markdown.text(
            markdown.text("Full name: ", profile_info.get("full_name", "")),
            markdown.text(
                "Leetcode profile: ", profile_info.get("leetcode_profile", "")
            ),
            sep="\n",
        ),
        reply_markup=markup.back_to_main_menu(),
    )


@dp.message_handler(Text(equals=markup.admins))
@permissions.private_chat()
async def contact_to_admins(message: types.Message):
    await bot.send_message(chat_id=message.chat.id, text="@dilshodbek_xojametov")


@dp.message_handler(Text(equals=markup.back))
@permissions.private_chat()
async def back_to_main_menu(message: types.Message):
    await bot.send_message(
        chat_id=message.chat.id, text="back to menu", reply_markup=markup.main_menu()
    )


@dp.message_handler(state="*", commands="cancel")
@dp.message_handler(Text(equals="cancel", ignore_case=True), state="*")
@permissions.private_chat()
async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    await message.reply("Cancelled.", reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(state=Form.full_name)
async def process_full_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["full_name"] = message.text

    await Form.next()
    await message.reply("Enter your leetcode profile name")


@dp.message_handler(state=Form.leetcode_profile)
async def process_leetcode_profile(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["leetcode_profile"] = message.text

    markup = ReplyKeyboardMarkup(
        one_time_keyboard=True,
    )
    markup.add("Send", "Cancel")

    await Form.next()

    await bot.send_message(
        chat_id=message.chat.id,
        text=markdown.text(
            markdown.text("Full name: ", markdown.bold(data["full_name"])),
            markdown.text(
                "Leetcode profile: ", markdown.bold(data["leetcode_profile"])
            ),
            sep="\n",
        ),
        reply_markup=markup,
        parse_mode=ParseMode.MARKDOWN,
    )


@dp.message_handler(state=Form.confirm)
async def confirm_data(message: types.Message, state: FSMContext):
    if message.text == "Send":
        async with state.proxy() as data:
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
            chat_id=settings.group_id,
            text=markdown.text(
                markdown.text("Chat ID: ", message.chat.id),
                markdown.text("Username: ", "@", message.chat.username),
                markdown.text("Full name: ", markdown.bold(data["full_name"])),
                markdown.text(
                    "Leetcode profile: ", markdown.bold(data["leetcode_profile"])
                ),
                sep="\n",
            ),
            reply_markup=markup.confirm_button(),
        )
        await message.reply("Thanks for registration", reply_markup=markup.main_menu())
    elif message.text == "Cancel":
        await message.reply("Registration cancelled", reply_markup=markup.main_menu())
    else:
        await message.reply("Please, use keyboard")

    await state.finish()


@dp.callback_query_handler(lambda call: True)
async def callback_inline(call):
    if str(call.from_user.id) not in settings.admins:
        return
    if call.message:
        chat_id = call.message.html_text[9:].split("\n")[0]
        text = "None of the buttons were clicked"
        if call.data == "cancel":
            await bot.send_message(
                chat_id=int(chat_id),
                text="Your request is not approved please contact to admins",
            )
            text = "✅"
        elif call.data == "send":
            tomorrow = datetime.now() + timedelta(days=1)
            link = await bot.create_chat_invite_link(
                chat_id=settings.group_id,
                expire_date=tomorrow,
                creates_join_request=True,
            )
            await bot.send_message(
                chat_id=int(chat_id),
                text=link["invite_link"],
            )

            data = await redis.hgetall(int(chat_id))
            if data:
                data["approved"] = 1
                await redis.hset(int(chat_id), mapping=data)
            text = "❌"
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        m = await bot.send_message(call.message.chat.id, call.message.html_text)
        await m.reply(text)


@dp.chat_join_request_handler()
async def join(message: types.ChatJoinRequest):
    chat_id = message.from_user.id
    data = await redis.hgetall(chat_id)
    if data and "approved" in data and data["approved"] == "1":
        await message.approve()
    else:
        await message.decline()
