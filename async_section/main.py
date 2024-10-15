import asyncio
import multiprocessing
import typing


class _MultiprocessingAsync(multiprocessing.Process):
    def __init__(self, durations: typing.Sequence[float]) -> None:
        super().__init__()
        self._durations = durations

    def run(self) -> None:
        asyncio.run(self._consecutive_sleeps())
        print("process finished")

    @staticmethod
    async def _async_sleep(duration: float) -> float:
        await asyncio.sleep(duration)
        return duration

    async def _consecutive_sleeps(self) -> None:
        pending = set(
            asyncio.create_task(self._async_sleep(duration))
            for duration in self._durations
        )

        while len(pending) > 0:
            done, pending = await asyncio.wait(pending, timeout=1)
            for done_task in done:
                print(await done_task)


async def _main() -> None:
    durations = list(range(1, 100))
    processes = [
        _MultiprocessingAsync(durations[i * 5 : (i + 1) * 5]) for i in range(5)
    ]

    for p in processes:
        p.start()

    for p in processes:
        p.join()


if __name__ == "__main__":
    asyncio.run(_main())
