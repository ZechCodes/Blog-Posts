import asyncio


cycles = 0


class Sleep:
    def __init__(self, cycles):
        self.cycles = cycles

    def __await__(self):
        """Dropping into the async/await API to let us use a generator as a coroutine."""
        global cycles
        for _ in range(self.cycles):
            cycles += 1
            yield


async def coroutine_a():
    await Sleep(5)
    result = await coroutine_b()
    print(result)


async def coroutine_b():
    await Sleep(10)
    return "Hello World"


async def main():
    await coroutine_a()
    print(f"Waited for {cycles} cycles")


if __name__ == "__main__":
    asyncio.run(main())
