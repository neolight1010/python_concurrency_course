from __future__ import annotations

import os
import threading
from multiprocessing import Queue
from typing import Literal
import logging
from sqlalchemy import create_engine
from sqlalchemy.sql import text

from workers.done import DONE, DONE_T

class PostgresMasterScheduler(threading.Thread):
    def __init__(self, input_queue: Queue[tuple[str, float, int] | DONE_T]):
        super().__init__()
        self._input_queue = input_queue

        self.start()

    def run(self):
        while True:
            val = self._input_queue.get()
            if val == DONE:
                break

            symbol, price, extracted_time = val
            postgres_worker = PostgresWorker(symbol, price, extracted_time)
            postgres_worker.insert_into_db()

class PostgresWorker():
    def __init__(self, symbol: str, price: float, extracted_time: int) -> None:
        self._symbol = symbol
        self._price = price
        self._extracted_time = extracted_time

        self._PG_USER = os.environ.get("PG_USER", "postgres")
        self._PG_PW = os.environ.get("PG_PW", "postgres")
        self._PG_HOST = os.environ.get("PG_HOST", "localhost")
        self._PG_DB = os.environ.get("PG_DB", "postgres")

        self._engine = create_engine(f"postgresql://{self._PG_USER}:{self._PG_PW}@{self._PG_HOST}/{self._PG_DB}")

    def insert_into_db(self):
        logging.info("inserting into db")
        insert_query = self._create_import_query()

        with self._engine.connect() as conn:
            conn.execute(text (insert_query), { "symbol": self._symbol, "price": self._price, "extracted_time": self._extracted_time })

    def _create_import_query(self) -> str:
        return "INSERT INTO prices (symbol, price, extracted_time) VALUES (:symbol, :price, :extracted_time)"
