from datetime import datetime, timedelta, date

import aioredis
from aiogram import types, Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, ParseMode, CallbackQuery
from prettytable import PrettyTable
from sqlalchemy import select, func

from src.database import db
from src.markups import markup
from src.models import User, Link, Statistic
from src.permissions import permissions

from src.config import settings


bot = Bot(token=settings.api_token)
dp = Dispatcher(bot, storage=MemoryStorage())

redis = aioredis.from_url(settings.redis_url, decode_responses=True)


class Form(StatesGroup):
    full_name = State()
    leetcode_profile = State()
    confirm = State()


@dp.message_handler(commands="start")
@permissions.private_chat()
@permissions.set_username()
async def start(message: types.Message):
    await bot.send_message(
        chat_id=message.chat.id,
        text="Hi this is leetcode bot",
        reply_markup=markup.main_menu(),
    )


@dp.message_handler(Text(equals=markup.register))
@permissions.private_chat()
@permissions.set_username()
async def register(message: types.Message):
    await Form.full_name.set()
    await message.reply("What is your full name?")


@dp.message_handler(Text(equals=markup.my_profile))
@permissions.private_chat()
async def my_profile(message: types.Message):
    query = select(User).filter(User.chat_id == message.chat.id)
    result = await db.execute(query)
    user = result.scalars().first()
    if user:
        profile_info = "Chat id: {}\nFull name: {}\nLeetcode profile: {}".format(
            user.chat_id, user.full_name, user.leetcode_profile
        )
    else:
        redis_data = await redis.hgetall(message.chat.id)
        if not redis_data:
            await bot.send_message(
                message.chat.id,
                text="You have not registered yet",
            )
            return
        profile_info = "Chat id: {}\nFull name: {}\nLeetcode profile: {}".format(
            message.chat.id, redis_data["full_name"], redis_data["leetcode_profile"]
        )
    await bot.send_message(message.chat.id, text=profile_info)


@dp.message_handler(Text(equals=markup.admins))
@permissions.private_chat()
async def contact_to_admins(message: types.Message):
    await bot.send_message(chat_id=message.chat.id, text="@dilshodbek_xojametov")


@dp.message_handler(Text(equals=markup.rating))
@permissions.private_chat()
async def rating(message: types.Message):
    total = func.max(Statistic.easy + Statistic.medium + Statistic.hard).label("total")
    score = func.max(3 * Statistic.hard + 2 * Statistic.medium + Statistic.easy).label(
        "score"
    )
    query = (
        select(
            User,
            total,
            score,
        )
        .group_by(User.id)
        .join(Statistic)
        .order_by(total.desc())
    )
    result = await db.execute(query)
    statistics = result.fetchall()
    fields = ["#", "username", "solved", "score"]
    table = PrettyTable(fields)
    values = []
    for i, statistic in enumerate(statistics):
        values.append(
            [i + 1, statistic[0].telegram_username, statistic[1], statistic[2]]
        )
    table.add_rows(values)
    await bot.send_message(
        chat_id=message.chat.id, text=f"```{table}```", parse_mode=ParseMode.MARKDOWN
    )


@dp.message_handler(Text(equals=markup.back))
@permissions.private_chat()
async def back_to_main_menu(message: types.Message):
    await bot.send_message(
        chat_id=message.chat.id, text="back to menu", reply_markup=markup.main_menu()
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
            chat_id=settings.admin_group_id,
            text="Chat id: {}\nUsername: @{}\nFull name: {}\nLeetcode profile: {}".format(
                message.chat.id,
                message.chat.username,
                data["full_name"],
                "https://leetcode.com/" + data["leetcode_profile"],
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
async def callback_inline(call: CallbackQuery):
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
            link = await db.execute(query)
            link = link.scalars().first()
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
                link = link.invite_link
            await bot.send_message(
                chat_id=chat_id,
                text=link,
            )
            data = await redis.hgetall(chat_id)
            if data:
                data["approved"] = 1
                await redis.hset(chat_id, mapping=data)
            text = "✅"
        elif call.data == "cancel":
            await bot.send_message(
                chat_id=chat_id,
                text="Admins declined your request to join the group due to incorrect information",
            )
            text = "❌"
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
            user = User(
                chat_id=chat_id,
                telegram_username=data["username"],
                leetcode_profile=data["leetcode_profile"],
                full_name=data["full_name"],
            )
            db.add(user)
            await db.commit()

            from src.scripts import create_statistic_for_user

            await create_statistic_for_user(user, date.today() - timedelta(days=1))
            await create_statistic_for_user(user, date.today())
            await message.approve()
        except Exception as e:
            print(e)
            db.rollback()
            await bot.send_message(
                chat_id=chat_id, text="Something went wrong please contact to admins"
            )
    else:
        await message.decline()


@dp.message_handler(commands=[""])
@dp.message_handler(commands=["test"])
async def test(message: types.Message):
    # query = select(User)
    # u = await db.execute(query)
    # x = u.scalars().first()
    # await get_solved_problems("dilshodbek_xojametov")
    # await bot.send_message(message.chat.id, "x")
    query = select(Statistic.date, func.count(Statistic.id)).group_by(Statistic.date)
    result = await db.execute(query)
    print(result.scalars().all())
