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

    result = ""
    while not result:
        result = process(request_1)

    print(result)

    result = ""
    while not result:
        result = process(request_2)

    print(result)


if __name__ == "__main__":
    main()
