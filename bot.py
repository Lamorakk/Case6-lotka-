import asyncio
import logging

from aiogram import Bot, Dispatcher, Router, F, types
from aiogram.enums import ChatMemberStatus, ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    FSInputFile, CallbackQuery, ChatMemberUpdated, InlineKeyboardButton,
    InlineKeyboardMarkup, Message, WebAppInfo
)
from aiogram.utils.deep_linking import create_start_link
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.payload import decode_payload

import constants as c
import keyboard as k
from request_data_server import post_new_user, get_user_data_by_tgid
from requests_main_server import post_user_to_main_server

# Initialize Dispatcher and Bot
bot = Bot(token=c.BOT_TOKEN)
dp = Dispatcher()

# Create Routers
message_router = Router()
callback_router = Router()
membership_router = Router()

# Set up logging
logging.basicConfig(level=logging.INFO)
DELIMITER = "?"

# ------------------------ COMMAND HANDLERS --------------------------------- #
@message_router.message(CommandStart(deep_link=True))
async def handler(message: Message, command: CommandObject, state: FSMContext):
    photo = FSInputFile('poster.jpg')
    welcome_message = (
        "👋 Welcome to [Your Lottery Name]! 🎉\n\n"
        "Join us in this exciting lottery and stand a chance to win amazing prizes!\n"
        "To get started, please [subscribe to our channel](https://t.me/+vb6dW4V4UDY1NDJi)."
    )
    user_data = await state.get_data()
    args = command.args.split()
    if not args:
        await message.answer("No payload found. Referral link is damaged or this referral is not registered")
        return

    referral_login = args[0]
    response = get_user_data_by_tgid(referral_login)
    if response is None:
        await message.answer(
            "Referral data could not be retrieved. Referral link might be incorrect or the user is not registered.")
        return

    if response["login"] == referral_login:
        user_reg = {
            "login": str(message.from_user.id),
            "password": "random_password",
        }

        try:
            login_data = post_new_user(user_reg)
            if login_data is None:
                raise Exception("Failed to create new user.")
            login, password = login_data['login'], login_data['password']


            await message.answer_photo(
                photo=photo,
                caption=welcome_message,
                reply_markup=k.subscribe_keyboard,
                parse_mode=ParseMode.MARKDOWN
            )
            refdata = str(message.from_user.id)
            reflink = await create_start_link(bot, refdata, encode=True)
            user_data = {
                "login": login,
                "password": password,
                "name": message.from_user.first_name,
                "username": message.from_user.username,
                "referralLogin": referral_login,
                "reflink": reflink
            }
            post_user_to_main_server(user_data)

        except Exception as e:
            logging.error(e)
            await message.answer_photo(
                photo=photo,
                caption=welcome_message,
                reply_markup=k.subscribe_keyboard,
                parse_mode=ParseMode.MARKDOWN
            )

@message_router.message(Command("start"))
async def start_handler(message: Message,command: CommandObject):
    args = check_if_any_payload(command)
    referral_login = 7021930058
    response = get_user_data_by_tgid(args[0])
    if args is None:
        await message.answer("No payload found. Referral link is damaged or this referral is not registered")
    elif response is None:
        await message.answer("Referral data could not be retrieved. Referral link might be incorrect or the user is not registered.")
    elif response["login"] == referral_login:
        user_reg = {
            "login": str(message.from_user.id),
            "password": "random_password",
        }

    photo = FSInputFile('poster.jpg')
    welcome_message = (
        "👋 Welcome to [Your Lottery Name]! 🎉\n\n"
        "Join us in this exciting lottery and stand a chance to win amazing prizes!\n"
        "To get started, please [subscribe to our channel](https://t.me/+vb6dW4V4UDY1NDJi)."
    )

    await message.answer_photo(
        photo=photo,
        caption=welcome_message,
        reply_markup=k.subscribe_keyboard,
        parse_mode=ParseMode.MARKDOWN
    )
    user_reg = {
        "login": str(message.from_user.id),
        "password": "random_password",
    }

    try:
        login_data = post_new_user(user_reg)
        if login_data is None:
            raise Exception("Failed to create new user.")
        login, password = login_data['login'], login_data['password']

        await message.answer_photo(
            photo=photo,
            caption=welcome_message,
            reply_markup=k.subscribe_keyboard,
            parse_mode=ParseMode.MARKDOWN
        )
        refdata = str(message.from_user.id)
        reflink = await create_start_link(bot, refdata, encode=True)
        user_data = {
            "login": login,
            "password": password,
            "name": message.from_user.first_name,
            "username": message.from_user.username,
            "referralLogin": referral_login,
            "reflink": reflink
        }
        post_user_to_main_server(user_data)
    except Exception as e:
        logging.error(e)
        await message.answer_photo(
            photo=photo,
            caption=welcome_message,
            reply_markup=k.subscribe_keyboard,
            parse_mode=ParseMode.MARKDOWN
        )


# ------------------------ CALLBACK QUERY HANDLERS --------------------------------- #

@callback_router.callback_query(F.data == "check_subscription")
async def check_subscription(callback: CallbackQuery):
    user_id = callback.from_user.id
    try:
        member = await bot.get_chat_member(chat_id=c.SUBSCRIBE_CHANNEL_ID, user_id=user_id)
        if member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]:
            await callback.answer("🎉 Thank you for subscribing!", show_alert=True)
            await callback.message.edit_caption(
                caption="You can now access the main menu.",
                reply_markup=k.main_menu_keyboard
            )
        else:
            await callback.answer("❌ Please subscribe to the channel first!", show_alert=True)
    except TelegramBadRequest as e:
        logging.error(f"Error checking subscription: {e}")
        await callback.answer("Some error occurred. Please try again later.", show_alert=True)


@callback_router.callback_query(F.data == "play")
async def play_handler(callback: CallbackQuery):
    await callback.answer("Let's play the lottery! 🎲", show_alert=True)

@callback_router.callback_query(F.data == "how_it_works")
async def how_it_works_handler(callback: CallbackQuery):
    how_it_works_message = (
        "📜 *How the Lottery Works:*\n\n"
        "1. Buy a ticket.\n"
        "2. Wait for the draw.\n"
        "3. Check if you won!\n\n"
        "Good luck! 🍀"
    )
    await callback.message.edit_caption(
        caption=how_it_works_message,
        reply_markup=k.main_menu_keyboard,
        parse_mode=ParseMode.MARKDOWN
    )



@dp.callback_query(F.data == "start_earning")
async def start_earning(callback: CallbackQuery, state: FSMContext):
    # user_data = await state.get_data()
    await open_web_app(callback, state)
    #
    # if user_data.get("terms_confirmed"):
    #     await open_web_app(callback, state)
    # else:
        # await send_terms_and_conditions(callback)


async def open_web_app(callback: types.CallbackQuery, state: FSMContext):
    photo = FSInputFile('poster.jpg')  # Use FSInputFile instead of InputFile
    CAPTION = 'welcome'
    try:
        # Retrieve user data
        login_data = get_user_data_by_tgid(callback.from_user.id)
        if login_data is None:
            await callback.answer("User data could not be retrieved. Please try again later.", show_alert=True)
            return

        login, password = login_data['login'], login_data['password']

        localization = 'en'

        web_app_url = f"{c.URL_TO_WEBSITE}?data={login}&pmain={password}&lang={localization}"
        web_app_info = WebAppInfo(url=web_app_url)

        builder = InlineKeyboardBuilder()
        builder.button(text="🎮 Play", web_app=web_app_info)
        builder.button(text="ℹ️ How it Works", callback_data="how_it_works")
        builder.button(text="🌐 Channel", url=c.SUBSCRIBE_CHANNEL_URL)
        builder.button(text="💬 Chat", url=c.SUBSCRIBE_CHAT_URL)
        builder.adjust(1)
        new_markup = builder.as_markup()

        await callback.message.delete()
        # await callback.message.edit_text("Welcome!", reply_markup=new_markup)
        await bot.send_photo(callback.message.chat.id, photo=photo, caption=CAPTION,
                             reply_markup=new_markup, parse_mode='HTML')

    except Exception as e:
        logging.error(f"Error in open_web_app: {e}")
        await callback.answer("Some unexpected error occurred", show_alert=True)

# ------------------------ UTIL FUNCTIONS --------------------------------- #

async def is_user_subscribed(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=c.SUBSCRIBE_CHANNEL_ID, user_id=user_id)
        return member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]
    except TelegramBadRequest:
        return False

def check_if_any_payload(command: CommandObject):
    args = command.args
    if args is not None:
        args_decoded = decode_payload(args).split(DELIMITER)
        if len(args_decoded) >= 2:
            return args_decoded[0], args_decoded[1]
    return None, None

# ------------------------ MAIN FUNCTIONS --------------------------------- #

async def main():
    dp.include_router(message_router)
    dp.include_router(callback_router)
    dp.include_router(membership_router)

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
