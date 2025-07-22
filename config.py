import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('7786508141:AAETbqJgSE7DI8QuCs7KT5GYx9ZqtI54W2c')
ADMIN_ID = os.getenv('6246979600')
WEB_APP_URL = os.getenv('https://roughguiltygroupware-2.onrender.com')
DATABASE_URL = os.getenv('postgres://avnadmin:AVNS_OosZVVpJZnW9bFAIE3i@infer-yolpak.f.aivencloud.com:23638/defaultdb?sslmode=require')

# --- Game Settings ---
STARTING_MONEY = 100
STARTING_LOCATION = "میدان اصلی"
XP_PER_LEVEL = 100
XP_PER_LEVEL_BASE = 100
XP_PER_LEVEL_FACTOR = 1.5
WORK_COOLDOWN_HOURS = 8
