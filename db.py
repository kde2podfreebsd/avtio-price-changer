import sqlite3
import requests


class QuoteController:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_quote_table()

    def create_quote_table(self):
        try:
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS quote (
                                avito_id INTEGER PRIMARY KEY,
                                rub_price FLOAT,
                                btc_price FLOAT,
                                price_ratio FLOAT,
                                status BOOLEAN
                                )''')
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error creating quote table: {e}")
            return e

    def create_ad(self, avito_id, rub_price, btc_price, status):
        try:
            price_ratio = rub_price / btc_price
            self.cursor.execute('''INSERT INTO quote (avito_id, rub_price, btc_price, price_ratio, status)
                                VALUES (?, ?, ?, ?, ?)''', 
                                (avito_id, rub_price, btc_price, price_ratio, status))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error creating ad: {e}")
            return e

    def update_btc_price(self):
        try:
            new_btc_price = self.get_current_btc_price()
            self.cursor.execute('SELECT avito_id, price_ratio FROM quote')
            quotes = self.cursor.fetchall()

            for quote in quotes:
                avito_id, price_ratio = quote
                new_rub_price = new_btc_price * price_ratio
                self.cursor.execute('''UPDATE quote 
                                    SET btc_price = ?, rub_price = ? 
                                    WHERE avito_id = ?''', 
                                    (new_btc_price, new_rub_price, avito_id))
            self.conn.commit()

            return True
        except sqlite3.Error as e:
            print(f"Error updating BTC price: {e}")
            return e

    def get_btc_price(self, avito_id):
        try:
            self.cursor.execute('SELECT btc_price FROM quote WHERE avito_id = ?', (avito_id,))
            return self.cursor.fetchone()[0]
        except sqlite3.Error as e:
            print(f"Error getting BTC price: {e}")
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
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Error getting status: {e}")
            return e

    def update_status(self, avito_id, new_status):
        try:
            self.cursor.execute('UPDATE quote SET status = ? WHERE avito_id = ?', (new_status, avito_id))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error updating status: {e}")
            return e

    def get_all_ads(self):
        try:
            self.cursor.execute('SELECT * FROM quote')
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting all ads: {e}")
            return []

    def get_ads_by_status(self, status):
        try:
            self.cursor.execute('SELECT * FROM quote WHERE status = ?', (status,))
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
    qc.update_btc_price()

