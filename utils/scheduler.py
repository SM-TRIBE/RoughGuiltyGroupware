from apscheduler.schedulers.asyncio import AsyncIOScheduler
from db import database
import config

async def grant_daily_rewards(bot):
    """A function to be potentially run by the scheduler."""
    # This logic is now handled by the /daily command to be more interactive.
    # This function can be used for other global events.
    print("Checked for scheduled tasks.")

async def setup_scheduler(bot):
    """Initializes and starts the scheduler."""
    scheduler = AsyncIOScheduler(timezone="Etc/UTC")
    # Add any world-event jobs here. For example, resetting a world boss.
    scheduler.add_job(grant_daily_rewards, 'interval', hours=6, args=(bot,))
    scheduler.start()
    print("Scheduler started.")
```python
