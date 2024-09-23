from __future__ import annotations

from multiprocessing import Queue
from queue import Empty
import threading
import time
from typing import Literal
import bs4
import random
import requests
import datetime

from logger import logger
from workers.done import DONE, DONE_T

_OutputValue = tuple[str, float, datetime.datetime] | DONE_T;
_OutputQueue = Queue[_OutputValue]

class YahooFinancePriceScheduler(threading.Thread):
    def __init__(self, input_queue: Queue[str], output_queues: _OutputQueue | list[_OutputQueue] | None):
        super().__init__()
        self._input_queue = input_queue
        self._output_queues: list[_OutputQueue] = output_queues if isinstance(output_queues, list) else [output_queues] if output_queues is not None else []
        self.start()

    def run(self):
        while True:
            try:
                symbol = self._input_queue.get(timeout=10)
            except Empty:
                logger.info("yahoo queue empty. Stopping")
                break

            if symbol == DONE:
                logger.debug("yahoo: sending DONE to output queue")

                self._put_all(DONE)
                break

            yahoo = YahooFinanceWorker(symbol)
            price = yahoo.get_price()
            logger.debug(f"obtained price: {price}")

            if price is not None:
                output_values = (symbol, price, datetime.datetime.utcnow())
                logger.debug(f"adding values to queue: {output_values}")
                self._put_all(output_values)

            time.sleep(20 * random.random())

    def _put_all(self, value: _OutputValue) -> None:
        for queue in self._output_queues:
            queue.put(value)

class YahooFinanceWorker:
    def __init__(self, symbol: str):
        super().__init__()

        self._symbol = symbol
        self._url = f"https://finance.yahoo.com/quote/{self._symbol}"

    def get_price(self) -> float | None:
        logger.info(f"getting price for symbol: {self._symbol}")
        response = requests.get(self._url)

        if response.status_code != 200:
            return None

        soup = bs4.BeautifulSoup(response.text, "html.parser")

        price_element = soup.find('fin-streamer', class_="livePrice")
        return float(price_element.text.replace(",", "")) if price_element else None
