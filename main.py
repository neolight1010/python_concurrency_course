from multiprocessing import Queue
import threading
import time
import logging

from workers.wiki_worker import WikiWorker
from workers.yahoo_finane_worker import DONE, YahooFinancePriceScheduler


def main() -> None:
    symbol_queue: Queue[str] = Queue()
    start_time = time.time()
    
    wiki = WikiWorker()
    yahoo_scheduler_threads: list[threading.Thread] = []

    num_yahoo_schedulers = 10
    yahoo_scheduler_threads: list[threading.Thread] = [YahooFinancePriceScheduler(symbol_queue) for _ in range(num_yahoo_schedulers)]
    
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
