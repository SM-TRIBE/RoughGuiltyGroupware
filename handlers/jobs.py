from aiogram import Router, types
from aiogram.filters import Text

router = Router()

@router.message(Text(equals="⚒️ کار و پیشه"))
async def jobs_menu(message: types.Message):
    await message.answer("بازار کار پر از فرصت‌های کثیف و شرافتمندانه است. دنبال چه کاری هستی؟")
```python
