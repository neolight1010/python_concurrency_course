from typing import Generator
import requests
import logging
import bs4

class WikiWorker():
    def __init__(self):
        self._url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

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
