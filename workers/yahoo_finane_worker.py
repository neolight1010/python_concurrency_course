from __future__ import annotations

import logging
from multiprocessing import Queue
import threading
from typing import Literal
import bs4
import random
import requests
import time

from workers.done import DONE, DONE_T

class YahooFinancePriceScheduler(threading.Thread):
    def __init__(self, input_queue: Queue[str], output_queue: Queue[tuple[str, float, int] | DONE_T] | None):
        super().__init__()
        self._input_queue = input_queue
        self._output_queue = output_queue
        self.start()

    def run(self):
        while True:
            symbol = self._input_queue.get()
            if symbol == DONE:
               if self._output_queue is not None:
                   self._output_queue.put(DONE)
               break

            yahoo = YahooFinanceWorker(symbol)
            price = yahoo.get_price()
            logging.debug(f"obtained price: {price}")

            if self._output_queue is not None and price is not None:
                output_values = (symbol, price, int(time.time()))
                self._output_queue.put(output_values)

            time.sleep(20 * random.random())

class YahooFinanceWorker():
    def __init__(self, symbol: str):
        super().__init__()

        self._symbol = symbol
        self._url = f"https://finance.yahoo.com/quote/{self._symbol}"

    def get_price(self) -> float | None:
        logging.info(f"getting price for symbol: {self._symbol}")
        response = requests.get(self._url)

        if response.status_code != 200:
            return None

        soup = bs4.BeautifulSoup(response.text, "html.parser")

        price_element = soup.find('fin-streamer', class_="livePrice")
        return float(price_element.text.replace(",", "")) if price_element else None
