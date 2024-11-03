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
