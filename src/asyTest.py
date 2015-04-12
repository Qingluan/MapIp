import asyncio
import random
import time

@asyncio.coroutine
def get_url(url):
    wait_time = random.randint(3, 6)
    print('Create: URL {} '.format(url))
    yield from asyncio.sleep(wait_time)
    print('Done: URL {} took {}s to get!'.format(url, wait_time))
    return url, wait_time


@asyncio.coroutine
def process_as_results_come_in():
    coroutines = [get_url(url) for url in ['URL1', 'URL2', 'URL3', 'URL4']]
    for coroutine in asyncio.as_completed(coroutines):
        url, wait_time = yield from coroutine
        print('Coroutine for {} is done'.format(url))


@asyncio.coroutine
def process_once_everything_ready():
    coroutines = [get_url(url) for url in ['URL1', 'URL2', 'URL3','URL4']]
    results = yield from asyncio.gather(*coroutines)
    print(results)


def main():
    st = time.time()
    loop = asyncio.get_event_loop()
    print("First, process results as they come in:")
    loop.run_until_complete(process_as_results_come_in())
    et = time.time() -st
    print("use : ",et)
    print("\nNow, process results once they are all ready:")
    loop.run_until_complete(process_once_everything_ready())
    et = time.time() -st
    print("use : ",et)

if __name__ == '__main__':
    main()