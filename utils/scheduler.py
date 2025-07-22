from apscheduler.schedulers.asyncio import AsyncIOScheduler

async def setup_scheduler(bot):
    """Initializes and starts the scheduler."""
    scheduler = AsyncIOScheduler(timezone="Etc/UTC")
    # Example job:
    # scheduler.add_job(some_function, 'interval', hours=1, args=(bot,))
    scheduler.start()
    print("Scheduler started.")
