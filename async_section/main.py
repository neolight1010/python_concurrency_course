import asyncio


async def _main() -> None:
    pending = set(asyncio.create_task(_sleep(i)) for i in range(10))

    while len(pending) > 0:
        done, pending = await asyncio.wait(pending, return_when="FIRST_COMPLETED")

        for task in done:
            print(await task)

        print("pending:", len(pending))


async def _sleep(n: int):
    print("waiting", n)
    await asyncio.sleep(n)
    print("waited", n)

    return n


if __name__ == "__main__":
    asyncio.run(_main())
