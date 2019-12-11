import asyncio
import aiohttp
import threading
import multiprocessing
from queue import Queue, Empty
from bs4 import BeautifulSoup
from db import Mongo, Elastic
from house_parser import HouseParser
from time import time
from multiprocessing import Pool


house_id_queue = Queue()
house_detail_queue = multiprocessing.Queue()

mongo = Mongo('192.168.99.100', 27017, 'rent591', 'houses')
es = Elastic('192.168.99.100', 9200, 'rent591', 'houses')

region_name_mapping = {
    '台北市': 1,
    '新北市': 3,
}


async def get_house_ids(region, house_id_queue=None):
    cookies = {'urlJumpIp': region}
    headers = {}

    params = {'kind': 0, 'region': region}
    async with aiohttp.ClientSession(cookies=cookies) as session:
        async with session.get('https://rent.591.com.tw/', params=params) as response:
            soup = BeautifulSoup(await response.text(), 'html.parser')
            csrf_token = soup.find(
                "meta", attrs={"name": "csrf-token"}).get('content')
            headers.update({'X-CSRF-TOKEN': csrf_token})
            cookies.update(response.cookies)

    params.update({'type': 1, 'searchtype': 1, })
    async with aiohttp.ClientSession(cookies=cookies, headers=headers) as session:
        async with session.get('https://rent.591.com.tw/home/search/rsList', params=params) as response:
            rslist = await response.json()

            house_ids = map(get_house_id, rslist.get('data').get('data'))
            for house_id in house_ids:
                house_id_queue.put((region, house_id))

            params.update({
                'firstRow': 30,
                'totalRows': rslist.get('records', '0').replace(',', ''),
            })

        while params.get('firstRow') < int(params.get('totalRows')):
            try:
                async with session.get("https://rent.591.com.tw/home/search/rsList", params=params) as response:
                    params['firstRow'] += 30
                    rslist = await response.json()
                    house_ids = map(
                        get_house_id, rslist.get('data').get('data'))
                    for house_id in house_ids:
                        house_id_queue.put((region, house_id))
            except:
                print('error: {}'.format(params))
                continue


def get_house_id(data):
    return data.get('houseid')


async def get_house_detail(house_id_queue=None, house_detail_queue=None):
    while True:
        try:
            region, house_id = house_id_queue.get(block=True, timeout=10)
            async with aiohttp.ClientSession() as session:
                async with session.get("https://rent.591.com.tw/rent-detail-{}.html".format(house_id)) as response:
                    house_detail_queue.put((region, await response.text()))
        except Empty:
            break

        except:
            print('error: {}'.format(house_id))
            continue


def save_house_data(region, house_detail_info):
    data = HouseParser(house_detail_info).get_house_info()
    data.update({'region': region})

    es.save(data)
    mongo.save(data)


def func_in_thread(func, pool_size=1, mapping_args=None, *args, **kwargs):
    tasks = []

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    for index in range(0, pool_size):
        if mapping_args:
            tasks.append(asyncio.ensure_future(func(*mapping_args[index])))
        else:
            tasks.append(asyncio.ensure_future(func(*args, **kwargs)))

    loop.run_until_complete(asyncio.gather(*tasks))
    loop.close()


t1_kwargs = {
    'pool_size': 2,
    'mapping_args': [
        (region_name_mapping['台北市'], house_id_queue),
        (region_name_mapping['新北市'], house_id_queue)
    ],
}

t2_kwargs = {
    'pool_size': 2,
    'house_id_queue': house_id_queue,
    'house_detail_queue': house_detail_queue,
}

t1 = threading.Thread(target=func_in_thread, args=(
    get_house_ids,), kwargs=t1_kwargs)

t2 = threading.Thread(target=func_in_thread, args=(
    get_house_detail,), kwargs=t2_kwargs)


if __name__ == '__main__':
    print('start: {}'.format(time()))

    t1.start()
    t2.start()

    p = Pool(processes=3)
    while True:
        try:
            region, house_detail_info = house_detail_queue.get(
                block=True, timeout=60)

            p.apply_async(save_house_data, args=(region, house_detail_info))
        except Empty:
            break
        except:
            continue

    print('end: {}'.format(time()))
