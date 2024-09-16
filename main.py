import time

from workers.wiki_worker import WikiWorker
from workers.yahoo_finane_worker import YahooFinanceWorker

def main() -> None:
    start_time = time.time()
    
    wiki = WikiWorker()

    current_workers: list[YahooFinanceWorker] = []
    for symbol in wiki.get_sp_500_companies():
        yahoo = YahooFinanceWorker(symbol)
        current_workers.append(yahoo)

    for worker in current_workers:
        worker.join()

    print("Execution took:", time.time() - start_time)


if __name__ == "__main__":
    main()
