from __future__ import annotations

import logging
from multiprocessing import Queue
import threading
import bs4
import random
import requests
import time

DONE = "DONE"

class YahooFinancePriceScheduler(threading.Thread):
    def __init__(self, input_queue: Queue[str]):
        super().__init__()
        self._input_queue = input_queue
        self.start()

    def run(self):
        while True:
            symbol = self._input_queue.get()
            if symbol == DONE:
                break

            yahoo = YahooFinanceWorker(symbol)
            price = yahoo.get_price()
            print(price)
            time.sleep(20 * random.random())

class YahooFinanceWorker(threading.Thread):
    def __init__(self, symbol: str):
        super().__init__()
        
        self._symbol = symbol
        self._url = f"https://finance.yahoo.com/quote/{self._symbol}"
        
        self.start()

    def get_price(self) -> float | None:
        logging.info(f"getting price for symbol: {self._symbol}")
        response = requests.get(self._url)

        if response.status_code != 200:
            return None
        
        soup = bs4.BeautifulSoup(response.text, "html.parser")

        price_element = soup.find('fin-streamer', class_="livePrice")
        return float(price_element.text.replace(",", "")) if price_element else None

    def run(self):
        print(self.get_price())

