import multiprocessing
import time


def _main() -> None:
    start_time = time.time()

    num_cpus_to_use = max(1, multiprocessing.cpu_count() - 1)
    print("Number of CPUs:", num_cpus_to_use)

    with multiprocessing.Pool(num_cpus_to_use) as pool:
        result = pool.map(_square, [1, 2, 3])

    print("Result:", result)

    print("everything took:", time.time() - start_time, "seconds")


def _square(x: int) -> int:
    return x * x


if __name__ == "__main__":
    _main()
