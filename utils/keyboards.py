from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

def main_menu() -> ReplyKeyboardMarkup:
    """The main menu keyboard."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👤 پروفایل من"), KeyboardButton(text="🗺️ گشت و گذار")],
            [KeyboardButton(text="⚒️ کار و پیشه"), KeyboardButton(text="🍻 زندگی اجتماعی")],
            [KeyboardButton(text="💰 بازارچه"), KeyboardButton(text="🎒 کوله‌پشتی")],
            [KeyboardButton(text="🏆 قهرمانان"), KeyboardButton(text="🎁 پاداش روزانه")]
        ],
        resize_keyboard=True
    )

def profile_menu(has_skill_points: bool) -> InlineKeyboardMarkup:
    """Menu shown on the profile screen."""
    builder = InlineKeyboardBuilder()
    builder.button(text="📝 تغییر شرح حال", callback_data="profile:edit_bio")
    if has_skill_points:
        builder.button(text="✨ تخصیص امتیاز ✨", callback_data="profile:assign_points")
    builder.adjust(2)
    return builder.as_markup()

def stat_assignment_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="+1 قدرت 💪", callback_data="assign_point:strength")
    builder.button(text="+1 چابکی 🏃", callback_data="assign_point:agility")
    builder.button(text="+1 هوش 🧠", callback_data="assign_point:intelligence")
    builder.button(text="انصراف", callback_data="assign_point:cancel")
    builder.adjust(1)
    return builder.as_markup()

def yes_no(callback_prefix: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="آری", callback_data=f"{callback_prefix}:yes"),
        InlineKeyboardButton(text="نه", callback_data=f"{callback_prefix}:no")
    ]])

def locations_kb(connections: list) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=loc)] for loc in connections] +
                 [[KeyboardButton(text="➡️ بازگشت به منوی اصلی")]],
        resize_keyboard=True
    )

def jobs_kb(available_jobs: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for job in available_jobs:
        builder.button(text=job, callback_data=f"job:get:{job}")
    builder.adjust(1)
    return builder.as_markup()

def shop_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="خرید", callback_data="shop:buy")
    builder.button(text="فروش", callback_data="shop:sell")
    return builder.as_markup()

def inventory_kb(items: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for item_id, item_name in items:
        builder.button(text=f"استفاده از {item_name}", callback_data=f"inventory:use:{item_id}")
    builder.adjust(1)
    return builder.as_markup()
