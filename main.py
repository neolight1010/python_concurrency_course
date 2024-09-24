import itertools
from multiprocessing import Queue
import logging

from logger import logger
from workers.done import DONE
from workers.wiki_worker import WikiWorker
from yaml_reader import YamlPipelineExecutor


def main() -> None:
    handler = logging.StreamHandler()
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    pipeline = YamlPipelineExecutor("wiki_yahoo_scraper_pipeline.yaml")
    pipeline.process_pipeline()

    wiki = WikiWorker()
    symbol_queue: Queue[str] = Queue()
    pipeline.add_queue("SymbolQueue", symbol_queue)

    logger.debug("inserting sp500 symbols")
    for symbol in itertools.islice(wiki.get_sp_500_companies(), 5):
        logger.debug(f"putting symbol: {symbol}")
        symbol_queue.put(symbol)
    logger.debug("finished inserting sp500 symbols")

    for _ in range(20):
        symbol_queue.put(DONE)

    pipeline.join()


if __name__ == "__main__":
    main()
