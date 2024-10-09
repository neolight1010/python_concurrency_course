import multiprocessing
import functools
import time


def _main() -> None:
    start_time = time.time()

    num_cpus_to_use = max(1, multiprocessing.cpu_count() - 1)
    print("Number of CPUs:", num_cpus_to_use)

    with multiprocessing.Pool(num_cpus_to_use) as pool:
        result = pool.map(functools.partial(_power, 2), [1, 2, 3])

    print("Result:", result)

    print("everything took:", time.time() - start_time, "seconds")


def _power(power: int, base: int) -> int:
    return base**power


if __name__ == "__main__":
    _main()
