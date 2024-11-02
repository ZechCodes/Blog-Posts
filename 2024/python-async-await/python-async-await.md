# Understanding Async/Await in Python

Async/Await is a powerful tool available to you, so it is important to understand how and when you can utilize it. In this post we're going to explore the high level of how Async/Await works and then dive a bit deeper into the more fundamental implementation. We'll also explore the differences between Async/Await and threads.

## Why Use Async/Await

Async/Await allows functions to release control so other functions can run. This is very helpful when a function needs to wait on something which typically blocks the application until a response is received. 

### The Problem - Blocking Functions

When a function has to wait on something slow it blocks the running thread, stopping all code from running. This often is the result of some kind of network request: database query, web request, etc. Let's look at an example requesting multiple web pages using the `requests` package.

```py
import requests
import time

def request_page(page):
    start_request = time.perf_counter()
    requests.get(page)
    end_request = time.perf_counter()
    return page.rsplit("/", 1)[1], end_request - start_request

def main():
    pages = ["https://google.com", "https://facebook.com", "https://amazon.com", "https://apple.com", "https://netflix.com"]

    start = time.perf_counter()
    total_duration = 0
    for page in pages:
        name, duration = request_page(page)
        total_duration += duration
        print(f"Requested {name} in {duration:.2f} seconds")

    end = time.perf_counter()
    print(f"Runtime {end - start:0.2f} seconds, cumulative runtime {total_duration:0.2f} seconds")

if __name__ == "__main__":
    main()
```

You'll notice that the total runtime is roughly the same as the cumulative runtime of each request. So its apparent that the requests are being made in sequence and the code is stopping as it waits for each request response.

It would be much faster if the requests didn't block each other and could run concurrently, this is where Async/Await comes in.

### A Solution - Async/Await

Async/Await lets functions release control when they block, allowing other functions to run in that downtime. This makes it possible to run some code concurrently and maximize how much of the time code is running. Let's look at the same example but using the `httpx` package so the requests can be done concurrently. 

```py
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
    print(f"Runtime {end - start:0.2f} seconds, cumulative runtime {total_duration:0.2f} seconds")

if __name__ == "__main__":
    asyncio.run(main())
```

This code is a bit more complex, but when we run it we see that the runtime is always less than the cumulative runtime. We can even see that the runtime is only a little longer than the slowest request. This tells us that each request is running concurrently and that no request is blocking the others while waiting for the response. 

## What Even Is Async/Await

### Iterators & Generators

### Coroutines: Generators by a different name

### The Event Loop

## How Threads Differ

## Async/Await & Parallelism
