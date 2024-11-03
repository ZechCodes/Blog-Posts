import asyncio


async def do_stuff():
    await asyncio.sleep(1)
    print("Doing more stuff")
    result = await do_more_stuff()
    print(result)


async def do_more_stuff():
    await asyncio.sleep(2)
    return "Hello World"


async def countdown():
    for i in range(10, 0, -1):
        print(i)
        await asyncio.sleep(1)

    print("TAKE OFF!!!!!")


async def main():
    future = asyncio.get_running_loop().create_task(countdown())
    await asyncio.sleep(0.5)
    await do_stuff()
    await future
    print("Main is exiting")


if __name__ == "__main__":
    asyncio.run(main())
