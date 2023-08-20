from datetime import datetime, timedelta, date

import aioredis
import src.crud as crud
from aiogram import types, Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, ParseMode, CallbackQuery
from prettytable import PrettyTable

from src.helpers import confirm_button, ACCEPTED, DECLINED, DECLINE_MESSAGE, NOT_CLICKED, ACCEPT, DECLINE
from src.database import db
from src.permissions import permissions

from src.config import settings


bot = Bot(token=settings.API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)


class Form(StatesGroup):
    full_name = State()
    leetcode_profile = State()
    confirm = State()


@dp.message_handler(commands="start")
@permissions.private_chat
@permissions.set_username
async def start(message: types.Message):
    await bot.send_message(
        chat_id=message.chat.id,
        text="Hi this is leetcode bot",
    )


@dp.message_handler(commands="register")
@permissions.private_chat
@permissions.set_username
async def register(message: types.Message):
    await Form.full_name.set()
    await message.reply("What is your full name?")


@dp.message_handler(commands="my_profile")
@permissions.private_chat
async def my_profile(message: types.Message):
    user = crud.user.get_by_chat_id(db, message.chat.id)
    if user:
        profile_info = "Chat id: {}\nFull name: {}\nLeetcode profile: {}".format(
            user.chat_id, user.full_name, user.leetcode_profile
        )
    else:
        profile_info = "You have not registered yet"
    await bot.send_message(message.chat.id, text=profile_info)


@dp.message_handler(commands="admins")
@permissions.private_chat
async def contact_to_admins(message: types.Message):
    admins_list = ""
    for admin_info in settings.ADMINS:
        admins_list += f"{admin_info}\n"
    await bot.send_message(chat_id=message.chat.id, text=admins_list)


@dp.message_handler(commands="rating")
@permissions.private_chat
async def rating(message: types.Message):
    user_ratings = await crud.user.get_rating(db)
    fields = ["#", "username", "solved", "score"]
    table = PrettyTable(fields)
    values = []
    for i, user_rating in enumerate(user_ratings):
        values.append(
            [i + 1, user_rating.User.telegram_username, user_rating.total, user_rating.score]
        )
    table.add_rows(values)
    await bot.send_message(chat_id=message.chat.id, text="Score calculation: 3 * hard + 2 * medium + easy")
    await bot.send_message(
        chat_id=message.chat.id, text=f"```{table}```", parse_mode=ParseMode.MARKDOWN
    )


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
        text="Chat id: {}\nUsername: @{}\nFull name: {}\nLeetcode profile: {}".format(
            message.chat.id,
            message.chat.username,
            data["full_name"],
            "https://leetcode.com/" + data["leetcode_profile"],
        ),
        reply_markup=markup,
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
            chat_id=settings.ADMINS_GROUP_ID,
            text="Chat id: {}\nUsername: @{}\nFull name: {}\nLeetcode profile: {}".format(
                message.chat.id,
                message.chat.username,
                data["full_name"],
                "https://leetcode.com/" + data["leetcode_profile"],
            ),
            reply_markup=confirm_button(),
        )
        await message.reply("Thanks for registration")
    elif message.text == "Cancel":
        await message.reply("Registration cancelled")
    else:
        await message.reply("Please, use keyboard")

    await state.finish()


@dp.callback_query_handler(lambda call: True)
async def callback_inline(call: CallbackQuery):
    if str(call.from_user.id) not in settings.ADMINS:
        return
    if call.message:
        chat_id = int(call.message.html_text[9:].split("\n")[0])
        text = NOT_CLICKED

        if call.data == ACCEPT:
            link = await crud.link.get_unexpired(db, chat_id)
            if not link:
                tomorrow = datetime.now() + timedelta(days=1)
                telegram_invite_link = (await bot.create_chat_invite_link(
                    chat_id=settings.GROUP_ID,
                    expire_date=tomorrow,
                    creates_join_request=True,
                ))["invite_link"]
                data = {
                    "chat_id": chat_id,
                    "invite_link": telegram_invite_link,
                    "expire_date": tomorrow,
                }
                link = await crud.link.create(db, data)

            await bot.send_message(
                chat_id=chat_id,
                text=link.invite_link,
            )
            redis_data = await redis.hgetall(chat_id)
            if not redis_data:
                await bot.send_message(chat_id=chat_id, text="Please register again your data was lost")
            redis_data["approved"] = 1
            await redis.hset(chat_id, mapping=redis_data)
            text = ACCEPTED
        elif call.data == DECLINE:
            await bot.send_message(
                chat_id=chat_id,
                text=DECLINE_MESSAGE
            )
            text = DECLINED
        await bot.delete_message(call.message.chat.id, call.message.message_id)
        message = await bot.send_message(
            call.message.chat.id, call.message.html_text, parse_mode=ParseMode.HTML
        )
        await message.reply(text)


@dp.chat_join_request_handler()
async def join(message: types.ChatJoinRequest):
    chat_id = message.from_user.id
    data = await redis.hgetall(chat_id)
    if data and "approved" in data and data["approved"] == "1":
        try:
            data = {
                "chat_id": chat_id,
                "telegram_username": data["username"],
                "leetcode_profile": data["leetcode_profile"],
                "full_name": data["full_name"],
            }
            user = await crud.user.create(db, data, commit=False)

            from src.scripts import create_statistic_for_user
            await create_statistic_for_user(user, date.today() - timedelta(days=1))
            await create_statistic_for_user(user, date.today())

            await db.commit()
            await message.approve()
        except Exception as e:
            print(e)
            db.rollback()
            await bot.send_message(
                chat_id=chat_id, text="Something went wrong please contact to admins"
            )
    else:
        await message.decline()
