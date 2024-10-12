import asyncio


async def _main() -> None:
    async for i in _sleep(5):
        print(i)


async def _sleep(n: int):
    print("before sleep", n)

    for i in range(n):
        yield i
        await asyncio.sleep(1)

    print("after sleep", n)


async def _hello() -> None:
    print("hello!")


if __name__ == "__main__":
    asyncio.run(_main())
