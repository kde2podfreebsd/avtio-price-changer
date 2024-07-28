import os
from db import QuoteController
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv
import logging
from httpx import AsyncClient, HTTPStatusError
from typing import Any, Dict, Optional, List
from datetime import datetime, timedelta
from utils import Avitoitem, ItemStatus

logging.basicConfig(level=logging.INFO)

class AvitoCore:

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        load_dotenv()
        self.qc = QuoteController(os.getenv("DB_PATH"))
        self._auth_cert: Optional[str] = None
        self.scheduler = AsyncIOScheduler(job_defaults={'max_instances': 100})

    @property
    def auth_cert(self) -> Optional[str]:
        return self._auth_cert
    
    @auth_cert.setter
    def auth_cert(self, value: Optional[str]) -> None:
        self._auth_cert = value

    async def authenticate(self) -> datetime:
        async with AsyncClient() as client:
            data = {
                'grant_type': 'client_credentials',
                'client_id': f'{os.getenv("CLIENT_ID")}',
                'client_secret': f'{os.getenv("CLIENT_SECRET")}'
            }
            auth_token_url = 'https://api.avito.ru/token/'

            try:
                response = await client.post(auth_token_url, data=data)
                response.raise_for_status()
                self.auth_cert = response.json()['access_token']
                logging.info('Authentication successful')

                return True

            except Exception as e:
                logging.error('Failed to authenticate: %s', e)
                raise e
            

    async def update_quotes(self):
        async with AsyncClient() as client:
            page = 1
            quotes = list()
            while True:
                url = f'https://api.avito.ru/core/v1/items?page={page}'
                headers = {'Authorization': f'Bearer {self.auth_cert}'}
                response = await client.get(url, headers=headers)
                if len(response.json()['resources']) == 0:
                    break

                response.raise_for_status()
                quotes.extend(response.json()['resources'])
                page += 1
            
            items = list((
                Avitoitem(
                    address=item['address'],
                    category=item['category']['name'],
                    avito_id=item['id'],
                    price=item['price'],
                    status=ItemStatus(item['status']),
                    title=item['title'],
                    url=item['url'],
                    quote_status=True
                )
                for item in quotes
            ))

            self.qc.create_ads(items=items)
            logging.info(f"Quotes created!: {items}")
            return items
        
    async def update_price(self, item_id: int):
        async with AsyncClient() as client:
            try:
                price = self.qc.get_rub_price(item_id)
                url = f"https://api.avito.ru/core/v1/items/{item_id}/update_price"
                response = await client.post(url, headers={'Authorization': f'Bearer {self.auth_cert}', 'Content-Type': 'application/json'}, json={"price": int(price)})
                response.raise_for_status()
                return int(price)
            except HTTPStatusError as e:
                logging.error(f"Failed to update price: {e}")
                return e
        
    async def update_items_price(self):
        try:
            await self.authenticate()
            self.qc.update_prices()
            await self.update_quotes()
            quotes = self.qc.get_ads_by_status(status=True)
            [await self.update_price(item[0]) for item in quotes]
            logging.info("Prices updated!")
            return True
        except Exception as e:
            return False
        
    async def everyminute_task(self):
        await self.authenticate()
        await self.update_quotes()
        logging.info("Quotes updated!")

    async def scheduled_task(self):
        self.qc.update_last_time_update_for_all_quotes()
        await self.update_items_price()

    def run(self):
        self.scheduler.add_job(self.everyminute_task, CronTrigger(minute="*"))
        self.scheduler.add_job(self.scheduled_task, CronTrigger(hour=2, minute=0, second=0, timezone='Europe/Moscow'))
        self.scheduler.start()
        print("Scheduler started!")

        loop = asyncio.get_event_loop()
        loop.run_forever()
        


if __name__ == "__main__":
    import asyncio
    avito_core = AvitoCore()
    avito_core.run()