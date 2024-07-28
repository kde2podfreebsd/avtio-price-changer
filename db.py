import sqlite3
import requests
from typing import Optional, List
from utils import Avitoitem, ItemStatus
from datetime import datetime

class QuoteController:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_quote_table()

    def create_quote_table(self):
        try:
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS quote (
                                avito_id INTEGER PRIMARY KEY,
                                address TEXT,
                                category TEXT,
                                rub_price FLOAT,
                                price_ratio FLOAT,
                                status TEXT,
                                title TEXT,
                                url TEXT UNIQUE,
                                last_time_update DATETIME
                                )''')
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error creating quote table: {e}")
            return e

    def create_ads(self, items: List[Avitoitem]):
        try:
            btc_price = self.get_current_btc_price()
            existing_ids = {row[0] for row in self.cursor.execute('SELECT avito_id FROM quote').fetchall()}
            incoming_ids = {item.avito_id for item in items}

            ids_to_delete = existing_ids - incoming_ids
            if ids_to_delete:
                self.cursor.executemany('DELETE FROM quote WHERE avito_id = ?', [(id_,) for id_ in ids_to_delete])

            for item in items:
                price_ratio = item.price / btc_price
                if item.avito_id not in existing_ids:
                    self.cursor.execute('''INSERT INTO quote (avito_id, address, category, rub_price, price_ratio, status, title, url, last_time_update)
                                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                                        (item.avito_id, item.address, item.category, item.price, price_ratio, item.status.value, item.title, item.url, datetime.now()))

            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error creating ads: {e}")
            return e

    def update_prices(self):
        try:
            new_btc_price = self.get_current_btc_price()
            self.cursor.execute('SELECT avito_id, price_ratio FROM quote')
            quotes = self.cursor.fetchall()

            for quote in quotes:
                avito_id, price_ratio = quote
                new_rub_price = new_btc_price * price_ratio
                self.cursor.execute('''UPDATE quote 
                                    SET rub_price = ?, price_ratio = ?, last_time_update = ?
                                    WHERE avito_id = ?''', 
                                    (new_rub_price, price_ratio, datetime.now(), avito_id))
            self.conn.commit()

            return True
        except sqlite3.Error as e:
            print(f"Error updating BTC price: {e}")
            return e

    def get_rub_price(self, avito_id):
        try:
            self.cursor.execute('SELECT rub_price FROM quote WHERE avito_id = ?', (avito_id,))
            return self.cursor.fetchone()[0]
        except sqlite3.Error as e:
            print(f"Error getting RUB price: {e}")
            return e

    def get_current_btc_price(self):
        url = 'https://garantex.org/api/v2/depth?market=btcrub' 
        response = requests.get(url=url).json() 
        return float(response['asks'][0]['price'])

    def get_status(self, avito_id):
        try:
            self.cursor.execute('SELECT status FROM quote WHERE avito_id = ?', (avito_id,))
            return self.cursor.fetchone()[0]
        except sqlite3.Error as e:
            print(f"Error getting status: {e}")
            return e

    def get_all_ads(self):
        try:
            self.cursor.execute('SELECT * FROM quote')
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting all ads: {e}")
            return []

    def get_ads_by_status(self, status: ItemStatus):
        try:
            self.cursor.execute('SELECT * FROM quote WHERE status = ?', (status.value,))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting ads by status: {e}")
            return []

    def get_ad_by_avito_id(self, avito_id):
        try:
            self.cursor.execute('SELECT * FROM quote WHERE avito_id = ?', (avito_id,))
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Error getting ad by avito id: {e}")
            return None

if __name__ == "__main__":
    db_path = 'ads.db'
    qc = QuoteController(db_path)
    qc.update_prices()
