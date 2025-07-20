
<line_number>1</line_number>

from telegram import Update
from telegram.ext import ContextTypes
from utils.tools import load_json, save_json
from datetime import datetime
import asyncio

async def send_notification(context: ContextTypes.DEFAULT_TYPE, user_id: str, message: str, notification_type: str = "info"):
    """Send notification to user"""
    try:
        await context.bot.send_message(chat_id=int(user_id), text=message)
        
        # Log notification
        players = load_json("data/players.json")
        if user_id in players:
            if 'notifications' not in players[user_id]:
                players[user_id]['notifications'] = []
            
            players[user_id]['notifications'].append({
                'message': message,
                'type': notification_type,
                'timestamp': datetime.now().isoformat(),
                'read': False
            })
            
            # Keep only last 50 notifications
            players[user_id]['notifications'] = players[user_id]['notifications'][-50:]
            save_json("data/players.json", players)
            
    except Exception as e:
        print(f"Failed to send notification to {user_id}: {e}")

async def broadcast_notification(context: ContextTypes.DEFAULT_TYPE, message: str, notification_type: str = "broadcast"):
    """Send notification to all users"""
    players = load_json("data/players.json")
    
    for user_id, player_data in players.items():
        if player_data.get("approved"):
            await send_notification(context, user_id, message, notification_type)
            await asyncio.sleep(0.1)  # Small delay to avoid rate limiting

async def show_notifications(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user notifications"""
    user = update.effective_user
    players = load_json("data/players.json")
    uid = str(user.id)
    
    if uid not in players or not players[uid].get("approved"):
        await update.message.reply_text("لطفاً ابتدا /start کنید.")
        return
    
    notifications = players[uid].get('notifications', [])
    unread_notifications = [n for n in notifications if not n.get('read', True)]
    
    if not notifications:
        await update.message.reply_text("🔕 هیچ اعلانی ندارید.")
        return
    
    text = f"🔔 اعلان‌ها ({len(unread_notifications)} خوانده نشده):\n\n"
    
    # Show last 10 notifications
    for notification in notifications[-10:]:
        status = "🔴" if not notification.get('read', True) else "⚪"
        timestamp = notification.get('timestamp', '')
        try:
            dt = datetime.fromisoformat(timestamp)
            time_str = dt.strftime("%m/%d %H:%M")
        except:
            time_str = "نامشخص"
        
        text += f"{status} {notification['message']}\n"
        text += f"   📅 {time_str}\n\n"
    
    # Mark all as read
    for notification in players[uid]['notifications']:
        notification['read'] = True
    
    save_json("data/players.json", players)
    
    await update.message.reply_text(text)

async def send_daily_rewards_reminder(context: ContextTypes.DEFAULT_TYPE):
    """Send daily reminder for daily rewards"""
    players = load_json("data/players.json")
    
    for user_id, player_data in players.items():
        if not player_data.get("approved"):
            continue
        
        last_daily = player_data.get('last_daily')
        if not last_daily:
            continue
        
        try:
            last_daily_time = datetime.fromisoformat(last_daily)
            hours_since = (datetime.now() - last_daily_time).total_seconds() / 3600
            
            # Send reminder if it's been 22+ hours since last daily
            if hours_since >= 22:
                await send_notification(
                    context, 
                    user_id, 
                    "🎁 یادآوری: جایزه روزانه شما آماده است! /daily",
                    "reminder"
                )
        except:
            continue
        
        await asyncio.sleep(0.1)

