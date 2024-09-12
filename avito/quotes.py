from avito.core import AvitoCore, quotesdal
import logging
from httpx import AsyncClient, HTTPStatusError
from utils import Avitoitem, ItemStatus

logging.basicConfig(level=logging.INFO)


class AvitoQuotes(AvitoCore):

    def __init__(self):
        super().__init__()

    async def get_quotes(self):
        async with AsyncClient() as client:
            await self.authenticate()
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

        await quotesdal.create_ads(items=items)

        return items

    async def update_price(self, item_id: int):
        price = await quotesdal.get_rub_price(item_id)

        async with AsyncClient() as client:
            await self.authenticate()
            try:
                url = f"https://api.avito.ru/core/v1/items/{item_id}/update_price"
                response = await client.post(url, headers={'Authorization': f'Bearer {self.auth_cert}',
                                                           'Content-Type': 'application/json'},
                                             json={"price": int(price)})
                response.raise_for_status()
                return int(price)
            except HTTPStatusError as e:
                logging.error(f"Failed to update price: {e}")
                return e

    async def update_items_price(self):
        try:
            await self.authenticate()
            await self.get_quotes()
            await quotesdal.update_prices()
            quotes = await quotesdal.get_ads_by_status(status=True)
            [await self.update_price(item['avito_id']) for item in quotes]
            logging.info("Prices updated!")
            return True
        except Exception as e:
            return False


if __name__ == "__main__":
    import asyncio

    async def main():
        a = AvitoQuotes()
        await a.authenticate()
        # return await a.get_quotes()
        await a.update_items_price()
        #await a.update_price(item_id=4314080309)
    print(asyncio.run(main()))
