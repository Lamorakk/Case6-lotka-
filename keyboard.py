from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types
import constants as c


main_menu_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🎮 Play", callback_data="start_earning")],
        [InlineKeyboardButton(text="ℹ️ How it Works", callback_data="how_it_works")],
        [InlineKeyboardButton(text="🌐 Channel", url=c.SUBSCRIBE_CHANNEL_URL)],
        [InlineKeyboardButton(text="💬 Chat", url=c.SUBSCRIBE_CHAT_URL)],
    ]
)

subscribe_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🔔 Check Subscription", callback_data="check_subscription")]
    ]
)