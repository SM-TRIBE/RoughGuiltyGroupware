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
            [KeyboardButton(text="💰 بازارچه"), KeyboardButton(text="🎒 کوله‌پشتی")]
        ],
        resize_keyboard=True
    )

def profile_menu() -> InlineKeyboardMarkup:
    """Menu shown on the profile screen."""
    builder = InlineKeyboardBuilder()
    builder.button(text="📝 تغییر شرح حال", callback_data="profile:edit_bio")
    builder.button(text="📊 تخصیص امتیاز", callback_data="profile:assign_points")
    builder.adjust(2)
    return builder.as_markup()

def yes_no(callback_prefix: str) -> InlineKeyboardMarkup:
    """A generic Yes/No inline keyboard."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="آری", callback_data=f"{callback_prefix}:yes"),
                InlineKeyboardButton(text="نه", callback_data=f"{callback_prefix}:no")
            ]
        ]
    )

def locations_kb(connections: list) -> ReplyKeyboardMarkup:
    """Keyboard for showing connected locations."""
    builder = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=loc)] for loc in connections] +
                 [[KeyboardButton(text="➡️ بازگشت به منوی اصلی")]],
        resize_keyboard=True
    )
    return builder

def jobs_kb(available_jobs: list) -> InlineKeyboardMarkup:
    """Keyboard for showing available jobs."""
    builder = InlineKeyboardBuilder()
    for job in available_jobs:
        builder.button(text=job, callback_data=f"job:get:{job}")
    builder.adjust(1)
    return builder.as_markup()

def shop_kb() -> InlineKeyboardMarkup:
    """Keyboard for the shop menu."""
    builder = InlineKeyboardBuilder()
    builder.button(text="خرید", callback_data="shop:buy")
    builder.button(text="فروش", callback_data="shop:sell")
    return builder.as_markup()
```python
