import multiprocessing
import queue
import time
from typing import Literal

_DONE_T = Literal["DONE"]
_DONE: _DONE_T = "DONE"


def _main() -> None:
    num_processes = 4
    comparison_list = [1, 2, 3]
    queue_: multiprocessing.Queue[tuple[int, int, int] | _DONE_T] = (
        multiprocessing.Queue()
    )

    start_time = time.time()
    processes = [
        multiprocessing.Process(
            target=_check_value_in_list,
            args=(comparison_list, i, num_processes, queue_),
        )
        for i in range(num_processes)
    ]

    for process in processes:
        process.start()

    for process in processes:
        process.join()

    queue_.put(_DONE)

    while (v := queue_.get()) != _DONE:
        lower, upper, number_of_hits = v
        print(
            f"Between {lower} and {upper}, we have {number_of_hits} values in the list."
        )

    print("everything took:", time.time() - start_time, "seconds")


def _check_value_in_list(
    x: list[float],
    i: int,
    number_of_processes: int,
    queue: queue.Queue[tuple[int, int, int]],
) -> None:
    max_number_to_check_to = 10**8
    lower = int(i * max_number_to_check_to / number_of_processes)
    upper = int((i + 1) * max_number_to_check_to / number_of_processes)

    hits = [n for n in range(lower, upper) if (n in x)]

    queue.put((lower, upper, len(hits)))


if __name__ == "__main__":
    _main()
