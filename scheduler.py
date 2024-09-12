import logging
import asyncio
from avito.quotes import AvitoQuotes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from avito.core import quotesdal

logging.basicConfig(level=logging.INFO)


class AvitoScheduler(AvitoQuotes):

    def __init__(self):
        super().__init__()
        self.scheduler = AsyncIOScheduler(job_defaults={'max_instances': 100})


    async def everyminute_task(self):
        await quotesdal.init_db()
        await self.authenticate()
        await self.get_quotes()
        logging.info("Quotes updated!")

    async def scheduled_task(self):
        await self.update_items_price()

    def run(self):
        self.scheduler.add_job(self.everyminute_task, CronTrigger(minute="*"))
        self.scheduler.add_job(self.scheduled_task, CronTrigger(hour=6, minute=0, second=0, timezone='Europe/Moscow'))
        self.scheduler.add_job(self.scheduled_task, CronTrigger(hour=18, minute=0, second=0, timezone='Europe/Moscow'))
        self.scheduler.start()
        print("Scheduler started!")

        loop = asyncio.get_event_loop()
        loop.run_forever()


if __name__ == "__main__":
    scheduler = AvitoScheduler()
    scheduler.run()

