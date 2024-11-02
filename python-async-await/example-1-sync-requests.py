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
    print(f"Runtime {end - start:0.2f} seconds, cumulative run time {total_duration:0.2f} seconds")


if __name__ == "__main__":
    main()
