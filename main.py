import itertools
from multiprocessing import Queue
import datetime
import time
import logging
from typing import Literal

from logger import logger
from workers.wiki_worker import WikiWorker
from workers.yahoo_finance_worker import YahooFinancePriceScheduler
from workers.postgres_worker import PostgresMasterScheduler
from workers.done import DONE


def main() -> None:
    handler = logging.StreamHandler()
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    symbol_queue: Queue[str] = Queue()
    postgres_queue: Queue[tuple[str, float, datetime.datetime] | Literal["DONE"]] = Queue()
    start_time = time.time()

    wiki = WikiWorker()

    num_yahoo_schedulers = 3
    yahoo_scheduler_threads: list[YahooFinancePriceScheduler] = [YahooFinancePriceScheduler(symbol_queue, output_queues=postgres_queue) for _ in range(num_yahoo_schedulers)]

    num_postgres_schedulers = 5
    postgres_scheduler_threads = [PostgresMasterScheduler(postgres_queue) for _ in range(num_postgres_schedulers)]

    LIMIT = 5
    logger.debug("inserting sp500 symbols")
    for symbol in itertools.islice(wiki.get_sp_500_companies(), LIMIT):
        logger.debug(f"putting symbol: {symbol}")
        symbol_queue.put(symbol)
    logger.debug("finished inserting sp500 symbols")

    logger.debug("sending done signals to yahoo workers")
    for _ in yahoo_scheduler_threads:
        symbol_queue.put(DONE)

    for thread in yahoo_scheduler_threads:
        thread.join()

    for thread in postgres_scheduler_threads:
        thread.join()

    logging.info("Execution took:", time.time() - start_time)


if __name__ == "__main__":
    main()
