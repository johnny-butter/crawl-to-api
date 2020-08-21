from time import time
from crawlers import HouseRentCrawler

if __name__ == '__main__':
    print(f'start: {time()}')

    HouseRentCrawler().start()

    print(f'end: {time()}')
