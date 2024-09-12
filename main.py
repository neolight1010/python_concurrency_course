import time
import threading

from workers.sleepy_workers import SleepyWorker
from workers.squared_sum_workers import SquaredSumWorker

def main() -> None:
    calc_start_time = time.time()
    
    current_threads: list[threading.Thread] = []
    for seconds in range(5):
        maximum_value = (seconds+ 1) * 1000000
        squared_sum_worker = SquaredSumWorker(maximum_value)
        current_threads.append(squared_sum_worker)

    for thread in current_threads:
        thread.join()

    print("calculating sum of squares took:", round(time.time() - calc_start_time, 2))

    sleep_start_time = time.time()
            
    current_threads: list[threading.Thread] = []
    for seconds in range(1, 6):
        sleepy_worker = SleepyWorker(seconds)
        current_threads.append(sleepy_worker)

    for thread in current_threads:
        thread.join()

    print("sleeping took:", round(time.time() - sleep_start_time, 2))


if __name__ == "__main__":
    main()
