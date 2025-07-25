LOCATIONS = {
    "میدان اصلی": {
        "description": "قلب تپنده شهرستان. جایی که شایعات مثل طاعون پخش می‌شوند و معاملات در سایه‌ها انجام می‌گیرد.",
        "connections": ["بازار", "میکده", "کوچه های تاریک"],
        "events": ["npc_encounter", "find_coin", "nothing"]
    },
    "بازار": {
        "description": "بازاری شلوغ و پر از هیاهو. بوی ادویه‌های غریب و صدای چانه‌زنی فروشندگان در هم آمیخته است.",
        "connections": ["میدان اصلی", "آهنگری"],
        "events": ["pickpocket", "good_deal", "nothing"]
    },
    "میکده": {
        "description": "میکده‌ای پر از دود و قهقهه‌های مستانه. مکانی برای شنیدن داستان‌های ناگفته و پیدا کردن دردسر.",
        "connections": ["میدان اصلی"],
        "events": ["brawl", "get_quest", "nothing"]
    },
    "کوچه های تاریک": {
        "description": "شبکه‌ای از کوچه‌های تنگ و تاریک که نور ماه به سختی به آن می‌رسد. هر سایه‌ای می‌تواند یک دوست یا یک خنجر باشد.",
        "connections": ["میدان اصلی"],
        "events": ["ambush", "find_hidden_item", "nothing"]
    },
    "آهنگری": {
        "description": "صدای پتک بر سندان در تمام محله می‌پیچد. بوی زغال و فلز گداخته در هوا موج می‌زند.",
        "connections": ["بازار"],
        "events": ["commission_work", "nothing"]
    }
}
```python
