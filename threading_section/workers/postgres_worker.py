from __future__ import annotations

import os
import datetime
import threading
from multiprocessing import Queue
from sqlalchemy import create_engine
from sqlalchemy.sql import text
from queue import Empty
from typing import TYPE_CHECKING, Any

from logger import logger
from workers.done import DONE, DONE_T


class PostgresMasterScheduler(threading.Thread):
    def __init__(self, input_queue: Queue[tuple[str, float, datetime.datetime] | DONE_T] | None, output_queues: list[Queue[Any]] | None, *, input_values: list[str] = []):
        super().__init__()
        self._input_queue = input_queue

        self._output_queues = output_queues
        self._input_values = input_values

        self.start()

    def run(self):
        if self._input_queue is None:
            logger.info("no input queues defined. Stopping")
            return

        while True:
            try:
                val = self._input_queue.get(timeout=10)
            except Empty:
                logger.info("postgres scheduler queue timed out. Stopping")
                break

            logger.debug(f"postgres: received values from queue: {val}")

            if val == DONE:
                break

            symbol, price, extracted_time = val
            postgres_worker = PostgresWorker(symbol, price, extracted_time)
            postgres_worker.insert_into_db()

class PostgresWorker():
    def __init__(self, symbol: str, price: float, extracted_time: datetime.datetime) -> None:
        self._symbol = symbol
        self._price = price
        self._extracted_time = extracted_time

        self._PG_USER = os.environ.get("PG_USER", "postgres")
        self._PG_PW = os.environ.get("PG_PW", "postgres")
        self._PG_HOST = os.environ.get("PG_HOST", "localhost")
        self._PG_DB = os.environ.get("PG_DB", "postgres")

        self._engine = create_engine(f"postgresql://{self._PG_USER}:{self._PG_PW}@{self._PG_HOST}/{self._PG_DB}")

    def insert_into_db(self):
        logger.debug("inserting into db")
        insert_query = self._create_import_query()

        with self._engine.connect() as conn:
            conn.execute(text(insert_query), { "symbol": self._symbol, "price": self._price, "extracted_time": str(self._extracted_time) })
            conn.commit()

        logger.debug("finished inserting into db")

    def _create_import_query(self) -> str:
        return "INSERT INTO prices (symbol, price, extracted_time) VALUES (:symbol, :price, :extracted_time);"


# Check that the classes implement the required protocols for yaml_reader
if TYPE_CHECKING:
    from yaml_reader import WorkerFactory

    factory: WorkerFactory = PostgresMasterScheduler
