import multiprocessing
import time


def _main() -> None:
    start_time = time.time()

    num_cpus_to_use = max(1, multiprocessing.cpu_count() - 1)
    print("Number of CPUs:", num_cpus_to_use)

    comparison_list = [1, 2, 3]
    lower_and_upper_bounds = [
        (0, 25 * 10**6),
        (25, 50 * 10**6),
        (50, 75 * 10**6),
        (75, 100 * 10**6),
    ]

    with multiprocessing.Pool(num_cpus_to_use) as pool:
        result = pool.starmap(
            _check_number_of_values_in_range,
            ((comparison_list, *bound) for bound in lower_and_upper_bounds),
        )

    print("Result:", result)

    print("everything took:", time.time() - start_time, "seconds")


def _check_number_of_values_in_range(
    comparison_list: list[int], lower: int, upper: int
) -> int:
    return sum((1 for i in range(lower, upper) if i in comparison_list))


if __name__ == "__main__":
    _main()
