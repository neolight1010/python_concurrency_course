import multiprocessing
import time

def main() -> None:
    num_threads = 4
    comparison_list = [1, 2, 3]

    start_time = time.time()
    processes = [multiprocessing.Process(target=check_value_in_list, args=(comparison_list,)) for _ in range(num_threads)]

    for process in processes:
        process.start()

    for process in processes:
        process.join()

    print("everything took:", time.time() - start_time, "seconds")

def check_value_in_list(x: list[float]) -> None:
    for i in range(10**8):
        if i in x:
            print(f"{i} is in {x}")


if __name__ == "__main__":
    main()
