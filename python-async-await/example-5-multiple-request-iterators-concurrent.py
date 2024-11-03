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
