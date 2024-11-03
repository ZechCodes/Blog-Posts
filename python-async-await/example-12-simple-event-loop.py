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
        while self.tasks:
            task = self.tasks.pop(0)
            try:
                task.send(None)
                self.tasks.append(task)
            except StopIteration:
                pass

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
