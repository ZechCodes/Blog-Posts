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
