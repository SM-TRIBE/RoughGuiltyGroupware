from aiogram import Router, types
from aiogram.filters import Text

router = Router()

@router.message(Text(equals="🗺️ گشت و گذار"))
async def explore_menu(message: types.Message):
    await message.answer("به کدام سمت می‌خواهی بروی؟ هر گوشه این شهر داستانی دارد...")
```python
