from __future__ import annotations

import itertools
from multiprocessing import Queue
import threading
from typing import TYPE_CHECKING, Generator
from typing_extensions import Any
import requests
import logging
import bs4

class WikiWorkerMasterScheduler(threading.Thread):
    def __init__(self, input_queue: Queue[Any] | None, output_queues: list[Queue[str]] | None, input_values: list[str] = []):
        super().__init__()

        self._urls = input_values
        self._output_queues = output_queues or []
        self._input_queue = input_queue

        self.start()

    def run(self) -> None:
        for url in self._urls:
            wiki_worker = _WikiWorker(url)

            # Only pass 5 symbols for debugging
            for symbol in itertools.islice(wiki_worker.get_sp_500_companies(), 5):
                self._put_all(symbol)

    def _put_all(self, value: str) -> None:
        for queue in self._output_queues:
            queue.put(value)

class _WikiWorker:
    def __init__(self, url: str) -> None:
        self._url = url

    def get_sp_500_companies(self) -> Generator[str, None, None]:
        response = requests.get(self._url)

        if response.status_code != 200:
            logging.warning("couldn't get wikipedia article")
            return None

        yield from self._extract_company_symbols(response.text)

    @staticmethod
    def _extract_company_symbols(page_html: str) -> Generator[str, None, None]:
        soup = bs4.BeautifulSoup(page_html, "html.parser")

        table = soup.find(id="constituents")
        if not isinstance(table, bs4.Tag):
            logging.warning("table is not a tag")
            return (_ for _ in ())

        table_rows = table.find_all("tr")
        return (table_row.find("td").text.strip("\n") for table_row in table_rows[1:])

if TYPE_CHECKING:
    from yaml_reader import WorkerFactory

    factory: WorkerFactory = WikiWorkerMasterScheduler
