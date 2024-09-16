import threading
import bs4
import random
import requests
import time


class YahooFinanceWorker(threading.Thread):
    def __init__(self, symbol: str):
        super().__init__()
        
        self._symbol = symbol
        self._url = f"https://finance.yahoo.com/quote/{self._symbol}"
        
        self.start()

    def get_price(self) -> float | None:
        response = requests.get(self._url)

        if response.status_code != 200:
            return None
        
        soup = bs4.BeautifulSoup(response.text, "html.parser")

        price_element = soup.find('fin-streamer', class_="livePrice")
        return float(price_element.text) if price_element else None

    def run(self):
        time.sleep(20 * random.random())
        print(self.get_price())

