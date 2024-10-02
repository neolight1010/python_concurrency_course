# Run this code in Python 3.8 to see the race conditions
from __future__ import annotations

import threading

counter = 0
lock = threading.Lock()

def increment() -> None:
    global counter

    for _ in range(10**5):
        with lock:
            counter += 1

threads: list[threading.Thread] = [threading.Thread(target=increment) for _ in range(8)]

for thread in threads:
    thread.start()

for thread in threads:
    thread.join()

print("Counter value:", counter)
