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
