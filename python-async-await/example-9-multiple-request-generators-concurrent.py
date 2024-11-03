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
