from multiprocessing import Queue
import threading
import time
import logging
import sys
from typing import Literal

from workers.wiki_worker import WikiWorker
from workers.yahoo_finane_worker import YahooFinancePriceScheduler
from workers.postgres_worker import PostgresMasterScheduler
from workers.done import DONE


def main() -> None:
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    symbol_queue: Queue[str] = Queue()
    postgres_queue: Queue[tuple[str, float, int] | Literal["DONE"]] = Queue()
    start_time = time.time()

    wiki = WikiWorker()

    num_yahoo_schedulers = 10
    yahoo_scheduler_threads: list[threading.Thread] = [YahooFinancePriceScheduler(symbol_queue, output_queue=postgres_queue) for _ in range(num_yahoo_schedulers)]

    num_postgres_schedulers = 2
    postgres_scheduler_threads = [PostgresMasterScheduler(postgres_queue) for _ in range(num_postgres_schedulers)]

    for symbol in wiki.get_sp_500_companies():
        logging.debug(f"inserting symbol: {symbol}")
        symbol_queue.put(symbol)

    for _ in yahoo_scheduler_threads:
        symbol_queue.put(DONE)

    for thread in yahoo_scheduler_threads:
        thread.join()

    logging.info("Execution took:", time.time() - start_time)


if __name__ == "__main__":
    main()
