# Understanding Async/Await in Python

Async/Await is a powerful tool available to you, so it is important to understand how and when you can utilize it. In this post we're going to explore the high level of how Async/Await works and then dive a bit deeper into the more fundamental implementation. We'll also explore the differences between Async/Await and threads.

### A Quick Aside About This Article

All the examples are available to run on my GitHub. Just clone my [Blog Posts](https://github.com/ZechCodes/Blog-Posts/) repository, open the "python-async-await" directory, run the example you're interested in using [uv](https://docs.astral.sh/uv/getting-started/). 

```shell
git clone https://github.com/ZechCodes/Blog-Posts/
cd Blog-Posts/python-async-await
uv run example-1-sync-requests.py
```

## Why Use Async/Await

Async/Await allows functions to release control so other functions can run. This is very helpful when a function needs to wait on something which typically blocks the application until a response is received. 

### The Problem - Blocking Functions

When a function has to wait on something slow it blocks the running thread, stopping all code from running. This often is the result of some kind of network request: database query, web request, etc. Let's look at an example requesting multiple web pages using the `requests` package.

[Example 1](example-1-sync-requests.py)
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
    print(f"Run time {end - start:0.2f} seconds, cumulative run time {total_duration:0.2f} seconds")

if __name__ == "__main__":
    main()
```

You'll notice that the total run time is roughly the same as the cumulative run time of each request. So its apparent that the requests are being made in sequence and the code is stopping as it waits for each request response.

It would be much faster if the requests didn't block each other and could run concurrently, this is where Async/Await comes in.

### A Solution - Async/Await

Async/Await lets functions release control when they block, allowing other functions to run in that downtime. This makes it possible to run some code concurrently and maximize how much of the time code is running. Let's look at the same example but using the `httpx` package so the requests can be done concurrently. 

[Example 2](example-2-async-requests.py)
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
    print(f"Run time {end - start:0.2f} seconds, cumulative run time {total_duration:0.2f} seconds")

if __name__ == "__main__":
    asyncio.run(main())
```

This code is a bit more complex, but when we run it we see that the run time is always less than the cumulative run time. We can even see that the run time is only a little longer than the slowest request. This tells us that each request is running concurrently and that no request is blocking the others while waiting for the response. 

## What Even Is Async/Await

Async/Await can seem a bit intimidating and magical, at its core though it is actually quite simple. So lets dive in and get a better understanding of how an async runtime can accept control back from a function when it needs to block and coordinate running other functions in that downtime.

### Iterators

Let's imagine that when we request a web page we get back an iterable, like a list. In this iterable we get `WAIT` until the response is received, at which point the iterable gives the response.

[Example 3](example-3-single-request-iterator.py)
```py
WAIT = object()
request = [WAIT, WAIT, WAIT, "Hello World from Request One!!!"]
for next_iteration in request:
    match next_iteration:
        case str() as result:
            print(f"The result is {result!r}")
        case _:
            pass
```

Next lets imagine we have a second request iterable. We could process the first request and then the second. This would block on the first request and then run the second request.

[Example 4](example-4-multiple-request-iterators-blocking.py)
```py
WAIT = object()

def process(request_iterator):
    match request_iterator.pop(0):
        case str() as result:
            return result
        case _:
            return ""

def main():
    request_1 = [WAIT, WAIT, WAIT, "Request One!!!"]
    request_2 = [WAIT, "Request Two!!!"]
    result = process(request_1)
    while not result:
        result = process(request_1)

    print(result)

    result = process(request_2)
    while not result:
        result = process(request_2)

    print(result)

if __name__ == "__main__":
    main()
```

Running this we see that the first request finishes before the second because it is started first and "blocks" until it is done.

Now lets try interleaving these iterators to get a form of concurrency.

[Example 5](example-5-multiple-request-iterators-concurrent.py)
```py
WAIT = object()

def process(request_iterator):
    match request_iterator.pop(0):
        case str() as result:
            return result
        case _:
            return ""

def main():
    request_1 = [WAIT, WAIT, WAIT, "Request One!!!"]
    request_2 = [WAIT, "Request Two!!!"]
    request_iterators = [request_1, request_2]
    while request_iterators:
        for i, request_iterator in enumerate(request_iterators):
            if result := process(request_iterator):
                print(result)
                del request_iterators[i]

if __name__ == "__main__":
    main()
```
Here we're creating a stack of iterators and iterating through that over and over. When we reach the end of an iterator it is removed from the stack. This results in request 1 being processed, then request 2, then request 1 again, and so on until we get a result from one of them. At that point we remove it from the stack and continue with the other.

When we run this code we see that request 2 finishes first because it has less waits before the result.

This is interesting but not entirely useful. Lists are great for sequences of data but there's no way to add any logic to it.

### Generators: Iterators that run code

Enter generators. Generators are functions that behave has iterators using the `yield` statement. When they run, their code acts like code in a function. When a `yield` is used though the function pauses and a value is sent back to the code that invoked the generator. The generator function can then be reactivated and it will pick back up at the yield and run like a normal function again.

Let's take a quick crash course through generators by looking at a couple of examples.

[Example 6](example-6-generator-example.py)
```py
def example_generator():
    print("Hello")
    yield
    print("World")
    return "Result"

def main():
    example = example_generator()
    print("Starting")
    try:
        example.send(None)
        print("Paused")
        example.send(None)
    except StopIteration as err:
        print(f"Finished with {err.value}")

if __name__ == "__main__":
    main()
```

Let's make this more clear by walking through it step by step:

1. `main` creates the `example_generator`, no code in the generator runs at this point.
2. `main` prints "Starting"
3. `main` calls `send` on the generator `example`, this runs the code in the generator function
4. `example_generator` prints "Hello" and then yields, pausing the generator function, giving control back to `main`
5. `main` runs and prints "Paused"
6. `main` calls `send` on the generator `example`, this runs the code in the generator function, picking up where it paused
7. `example_generator` prints "World" and then returns `"Result"`, this raises a `StopIteration` error
8. `main` catches the raised error, captures the return from the `value` property of the exception, and prints "Finished with Result" before exiting

Now let's try something a bit crazier.

[Example 7](example-7-generator-yield-from.py)
```py
def generator_a():
    returned_value = yield from generator_b()
    print(f"A got {returned_value!r}")
    return "Return From A"

def generator_b():
    yield "Yielded From B"
    return "Return From B"

def main():
    gen = generator_a()
    try:
        print(f"Main got {gen.send(None)!r}")
        print(f"Main got {gen.send(None)!r}")  # This print causes StopIteration and doesn't print
    except StopIteration as err:
        print(f"Main got {err.value!r}")

if __name__ == "__main__":
    main()
```

Here we're using `yield from` to start a generator from within a generator passing control downwards. A generator started with `yield from` will `yield` into the function that called `send` on the top level generator. Let's walk through this to try and make that clearer:

1. `main` creates `generator_a`
2. `main` calls `send` on `gen` running its code
3. `generator_a` then yields from `generator_b`
4. `generator_b` then yields `"Yielded From B"`
5. `main` prints "Main got 'Yielded From B'"
6. `main` calls `send` on `gen`
7. `generator_b` returns `"Return From B"`
8. `generator_a` prints "A got 'Return From B'"
9. `generator_a` returns `"Return From A"`
10. `main` prints "Main got 'Return From A'"
11. The program exits

Ok, everyone got ok? Everyone got that? No? Yeah, it's a lot to process. Don't worry about it too much, the only takeaway you need is the idea that a generator is an iterator that can also run code. Here's a very simple example showing that a generator is just a very complex iterator that runs code in between values:

[Example 8](example-8-generators-are-iterators.py)
```py
def generator():
    for i in range(5):
        print(f"Yielding {i}")
        yield i

def main():
    for i in generator():
        print(f"main got {i}")
        
if __name__ == "__main__":
    main()
```

That means we can take [Example 5](example-5-multiple-request-iterators-concurrent.py) and rewrite it as generators:

[Example 9](example-9-multiple-request-generators-concurrent.py)
```py
def process(request_iterator):
    try:
        request_iterator.send(None)
    except StopIteration as err:
        return err.value
    else:
        return

def request_1_generator():
    for i in range(3):
        yield

    return "Request One!!!"

def request_2_generator():
    for i in range(1):
        yield

    return "Request Two!!!"

def main():
    request_1 = request_1_generator()
    request_2 = request_2_generator()
    request_iterators = [request_1, request_2]
    while request_iterators:
        for i, request_iterator in enumerate(request_iterators):
            if result := process(request_iterator):
                print(result)
                del request_iterators[i]

if __name__ == "__main__":
    main()
```

That is functionally the same as [Example 5](example-5-multiple-request-iterators-concurrent.py) but it's using `yield` to indicate a "wait" and generators instead of lists.

I think at this point if you squint at that code you can start to see how this is going to turn into async/await. 

### Coroutines: Generators by a different name

That was a lot to take in but I think the fundamental structure of async functions and awaits is starting to come together. This is probably a good time to introduce "coroutines." A coroutine is an async function that is implemented as a generator. A coroutine uses `yield` to pass control back upwards to the code that owns the top level generator object, this is how coroutines pause when they have to wait on something that is blocking. 

A coroutine can also use `yield from` to wait on another coroutine, passing control downwards to that new coroutine. You can think of this as calling that coroutine and letting it take control. Any yields in the new coroutine will appear to be coming from the calling coroutine. Here's a simple example:

[Example 10](example-10-simple-yield-from.py)
```py
def coroutine_a():
    for _ in range(5):
        yield

    result = yield from coroutine_b()
    print(result)

def coroutine_b():
    for _ in range(10):
        yield

    return "Hello World"

def main():
    wait_counter = 0
    routine = coroutine_a()
    while True:
        try:
            routine.send(None)
            wait_counter += 1
        except StopIteration:
            break

    print(f"Waited {wait_counter} times")

if __name__ == "__main__":
    main()
```

When this is run we see that it says it waited 15 times. There are 5 waits in `coroutine_a` and another 10 waits in `coroutine_b`. So our `main` function is seeing the waits in `coroutine_b` even thought it only ran `coroutine_a`.

We also see that when `coroutine` used `yield from` to run `coroutine_b` it was able to capture the return the same as if `coroutine_b` had been a standard function that it had called.

There's no real magic to coroutines, they're just a specific use of generators that leverages pretty every single generator feature that Python offers.

### Translating This to Async/Await

Alright, we've covered a lot of stuff and built up to coroutines. At this point we've implemented async/await just using generator syntax. Python has special syntax for it's native coroutines just to make it easier to tell when you're writing a generator and when you're writing a coroutine. Ultimately async/await in Python is syntactic sugar for a special kind of generator.

So let's look at a rough and quick translation of the `coroutine_a` and `coroutine_b` to async/await syntax.

```py
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
```

There's not a way to implement sleeping for a set number of cycles, so here I've implemented a simple `Sleep` type that uses a generator as a coroutine to sleep for a given number of cycles. Which brings us to event loops, which is what's causing the `Sleep` coroutine to iterate and update the `cycles` counter.

### The Event Loop

The event loop is what coordinates all the running coroutines, taking control when one yields and iterates all the others in turn giving them each control. In many of the earlier examples there's a `while` loop in the `main` function, it is a very rudimentary "event loop" managing each of the coroutines.

A more fully featured event loop should provide a way to add new top level tasks, stop all running tasks, and offer futures. For the sake of exercise lets look at a simple event loop implementation using generators.

[Example 12](example-12-simple-event-loop.py)
```py
import time

class Future:
    def __init__(self):
        self.finished = False
        self.value = None

    def close(self):
        self.finished = True

    def send(self, _):
        if self.finished:
            err = StopIteration()
            err.value = self.value
            raise err

    def __iter__(self):
        return self

    def __next__(self):
        return self.send(None)

class Task(Future):
    def __init__(self, coro):
        super().__init__()
        self.coro = coro

    def send(self, value):
        try:
            return self.coro.send(value)
        except StopIteration as e:
            self.value = e.value
            self.finished = True
            raise e

    def close(self):
        self.coro.close()
        super().close()

class EventLoop:
    running_loop = None
    def __init__(self):
        self.tasks = []

    def create_task(self, coro):
        future = Task(coro)
        self.tasks.append(future)
        return future

    def run_until_complete(self):
        EventLoop.running_loop = self
        try:
            while True:
                while self.tasks:
                    task = self.tasks.pop(0)
                    try:
                        task.send(None)
                        self.tasks.append(task)
                    except StopIteration:
                        pass
                else:
                    break
        finally:
            self.stop()

    def stop(self):
        for task in self.tasks:
            task.close()

        self.tasks.clear()
        EventLoop.running_loop = None

    @classmethod
    def run(cls, coro):
        loop = cls()
        loop.create_task(coro)
        loop.run_until_complete()
        loop.stop()

def sleep(delay):
    start_time = time.time()
    while time.time() < start_time + delay:
        yield

def do_stuff():
    yield from sleep(1)
    print("Doing more stuff")
    result = yield from do_more_stuff()
    print(result)

def do_more_stuff():
    yield from sleep(2)

    return "Hello World"

def countdown():
    for i in range(10, 0, -1):
        print(i)
        yield from sleep(1)

    print("TAKE OFF!!!!!")

def main():
    future = EventLoop.running_loop.create_task(countdown())
    yield from sleep(0.5)
    yield from do_stuff()
    yield from future
    print("Main is exiting")

if __name__ == "__main__":
    EventLoop.run(main())
```

This implements a basic loop with the ability to create tasks and stop running tasks. It provides a `Future` type for awaiting a value and a `Task` type that wraps a coroutine in a future. It also has a basic `sleep` function that yields until a given delay has passed.

Running this starts the `main` coroutine which in turn creates a new top level task for the `countdown` coroutine. This `countdown` coroutine then runs in "parallel" with `main` and the coroutines it yields from. `main` even yields from the `countdown` future to wait for it to finish before exiting.

This is a very basic event loop, but it shows how you can use generators to implement a simple event loop. At the most basic level this is doing what Python's `asyncio` package is doing under the hood.

You can check out [Example 13](example-13-event-loop-asyncio.py) to see how these coroutines would be written using Python's `asyncio` and async/await.

## How Threads Differ

Now that we've gone through how async/await works and implemented our own basic version using generators, you're probably wondering how this is different from using threads.

Async/await lets functions yield back control to the event loop. So async/await only works with functions and relies on the functions themselves to handle task switching. Everything happens within the runtime of the application since the event loop is part of the application code. This makes it great for IO bound tasks, as the function knows when it is waiting on an IO task.

Threads on the other hand are an OS level construct that allows code to run in parallel, not just functions. Concurrency comes from running threads on separate CPU threads giving true parallelism. In cases where there aren't enough CPU threads the OS can pause threads in an application and switch to another thread, this happens entirely outside the application code.

Because threads can work without regard for what is happening in the code, they are excellent for CPU bound tasks. They can run code in parallel and take advantage of multiple CPU cores. This is why threads are often used for image processing, machine learning, and other computation heavy tasks.

## Async/Await & Parallelism

Python's async/await is not parallelism, it is concurrency. The event loop can keep multiple tasks working towards completion but only one task is running at a time. In other languages it is possible to run tasks in multiple threads to get parallel async/await tasks but because of Python's GIL this is not currently possible.

Future versions of Python may be free threaded, allowing for parallel async/await tasks. Until then, if you need parallelism you'll need to use threads or processes. `asyncio` actually has tools to run functions in a thread that you can await a result from, check out [run_in_executor](https://docs.python.org/3/library/asyncio-eventloop.html#asyncio.loop.run_in_executor) for more information.

## Conclusion

Async/await is a powerful tool that can help you write more effective code. It can seem a bit magical but at its core it is actually quite simple. Iteration, generators, and a clever application of fairly common syntax is all it bools down to.

I hope you found this article useful for improving your understanding of how async/await works and that it gave you a better understanding of how to use it in your own code.
