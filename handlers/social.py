from aiogram import Router, types
from aiogram.filters import Text

router = Router()

@router.message(Text(equals="🍻 زندگی اجتماعی"))
async def social_menu(message: types.Message):
    await message.answer("می‌خواهی با دیگران دمخور شوی، پیمان ببندی یا دشمنی کنی؟")
```python
