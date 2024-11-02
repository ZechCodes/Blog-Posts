import asyncio
import httpx
import time


async def request_page(page):
    start_request = time.perf_counter()
    async with httpx.AsyncClient() as client:
        await client.get(page)
        end_request = time.perf_counter()

    return page.rsplit("/", 1)[1], end_request - start_request


async def main():
    pages = ["https://google.com", "https://facebook.com", "https://amazon.com", "https://apple.com", "https://netflix.com"]

    start = time.perf_counter()
    tasks = [asyncio.create_task(request_page(page)) for page in pages]
    total_duration = 0
    for next_result in asyncio.as_completed(tasks):
        site, duration = await next_result
        total_duration += duration
        print(f"Requested {site} in {duration:.2f} seconds")

    end = time.perf_counter()
    print(f"Runtime {end - start:0.2f} seconds, cumulative run time {total_duration:0.2f} seconds")


if __name__ == "__main__":
    asyncio.run(main())
