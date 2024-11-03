WAIT = object()
request = [WAIT, WAIT, WAIT, "Hello World from Request One!!!"]
for next_iteration in request:
    match next_iteration:
        case str() as result:
            print(f"The result is {result!r}")
        case _:
            pass
