import threading

class SquaredSumWorker(threading.Thread):
    def __init__(self, n: int):
        self._n = n
        super().__init__()
        self.start()

    def run(self) -> None:
        self._calculate_sum_squares()

    def _calculate_sum_squares(self) -> None:
        sum_squares = 0
        for i in range(self._n):
            sum_squares += i ** 2

        print(sum_squares)
