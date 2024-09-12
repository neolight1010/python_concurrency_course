import threading
import time

class SleepyWorker(threading.Thread):
    def __init__(self, seconds: float) -> None:
        self._seconds = seconds
        
        super().__init__()

        self.start()

    def run(self) -> None:
        self._sleep_a_little()

    def _sleep_a_little(self) -> None:
        time.sleep(self._seconds)
