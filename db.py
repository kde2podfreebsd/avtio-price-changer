import aiosqlite
from typing import List, Optional
from datetime import datetime
from utils import Avitoitem, get_current_btc_price


class QuoteDAL:
    def __init__(self, db_path: str):
        self.db_path = db_path

    async def init_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS quote (
                    avito_id INTEGER PRIMARY KEY,
                    address TEXT,
                    category TEXT,
                    rub_price REAL,
                    price_ratio REAL,
                    status TEXT,
                    title TEXT,
                    url TEXT UNIQUE,
                    last_time_update TEXT,
                    quote_status BOOLEAN
                )
            """)
            await db.commit()

    async def create_ads(self, items: List[Avitoitem]) -> bool:
        try:
            btc_price = await get_current_btc_price()
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("SELECT avito_id FROM quote")
                existing_ids = {row[0] for row in await cursor.fetchall()}
                incoming_ids = {item.avito_id for item in items}

                ids_to_delete = existing_ids - incoming_ids
                if ids_to_delete:
                    await db.executemany(
                        "DELETE FROM quote WHERE avito_id = ?", [(avito_id,) for avito_id in ids_to_delete]
                    )

                for item in items:
                    price_ratio = item.price / btc_price
                    if item.avito_id not in existing_ids:
                        await db.execute(
                            """
                            INSERT INTO quote (
                                avito_id, address, category, rub_price, price_ratio,
                                status, title, url, last_time_update, quote_status
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                item.avito_id, item.address, item.category, item.price, price_ratio,
                                item.status.value, item.title, item.url, datetime.now(), True
                            )
                        )
                await db.commit()
            return True
        except Exception as e:
            print(f"Error creating ads: {e}")
            return False

    async def update_prices(self) -> bool:
        try:
            new_btc_price = await get_current_btc_price()
            print(new_btc_price)
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("SELECT avito_id, price_ratio FROM quote")
                quotes = await cursor.fetchall()

                for avito_id, price_ratio in quotes:
                    new_rub_price = new_btc_price * price_ratio
                    await db.execute(
                        "UPDATE quote SET rub_price = ?, last_time_update = ? WHERE avito_id = ?",
                        (new_rub_price, datetime.now(), avito_id)
                    )
                await db.commit()
            return True
        except Exception as e:
            print(f"Error updating BTC price: {e}")
            return False

    async def update_price(self, avito_id: int, new_price: float) -> bool:
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    "UPDATE quote SET rub_price = ?, last_time_update = ? WHERE avito_id = ?",
                    (new_price, datetime.now(), avito_id)
                )
                await db.commit()
            return True
        except Exception as e:
            print(f"Error updating price: {e}")
            return False

    async def update_quotes_status(self, avito_id: int) -> bool:
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("SELECT quote_status FROM quote WHERE avito_id = ?", (avito_id,))
                current_status = (await cursor.fetchone())[0]
                new_status = not current_status
                await db.execute(
                    "UPDATE quote SET quote_status = ? WHERE avito_id = ?",
                    (new_status, avito_id)
                )
                await db.commit()
            return True
        except Exception as e:
            print(f"Error updating quote status: {e}")
            return False

    async def get_rub_price(self, avito_id: int) -> Optional[float]:
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("SELECT rub_price FROM quote WHERE avito_id = ?", (avito_id,))
                result = await cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            print(f"Error getting RUB price: {e}")
            return None

    async def get_all_ads(self) -> List[dict]:
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute("SELECT * FROM quote")
                return [dict(row) for row in await cursor.fetchall()]
        except Exception as e:
            print(f"Error getting all ads: {e}")
            return []

    async def get_ads_by_status(self, status: bool) -> List[dict]:
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute("SELECT * FROM quote WHERE quote_status = ?", (status,))
                return [dict(row) for row in await cursor.fetchall()]
        except Exception as e:
            print(f"Error getting ads by status: {e}")
            return []

    async def get_ad_by_avito_id(self, avito_id: int) -> Optional[dict]:
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute("SELECT * FROM quote WHERE avito_id = ?", (avito_id,))
                row = await cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            print(f"Error getting ad by avito id: {e}")
            return None


if __name__ == "__main__":
    import asyncio

    async def main():
        qd = QuoteDAL('quotes.db')
        await qd.init_db()
        print(await qd.update_quotes_status(avito_id=4314080309))

    asyncio.run(main())

