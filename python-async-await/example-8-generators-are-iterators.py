def generator():
    for i in range(5):
        print(f"Yielding {i}")
        yield i


def main():
    for i in generator():
        print(f"main got {i}")


if __name__ == "__main__":
    main()
