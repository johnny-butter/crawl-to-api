import aiohttp
import requests
from bs4 import BeautifulSoup

import asyncio
import threading
import multiprocessing
from queue import Queue, Empty

from db import Mongo, Elastic
from parsers import HouseParser


class HouseRentCrawler:
    """
    Crawl all houses data which in "TARGET_REGIONS"
    """

    TARGET_REGIONS = {
        '台北市': 1,
        '新北市': 3,
    }

    HOUSE_ID_QUEUE = Queue()
    HOUSE_DETAIL_QUEUE = multiprocessing.Queue()

    MONGO_DB = Mongo('192.168.99.100', 27017, 'rent591', 'houses')
    ES = Elastic('192.168.99.100', 9200, 'rent591', 'houses')

    def __init__(self, async_tasks_cnt=2):
        self.target_endpoint = 'https://rent.591.com.tw/'
        self.async_tasks_cnt = async_tasks_cnt

    def start(self):
        threading.Thread(target=self._start_get_house_ids).start()
        threading.Thread(target=self._start_get_house_detail).start()

        pool = multiprocessing.Pool(processes=3)
        while True:
            try:
                region_id, house_detail_info = self.HOUSE_DETAIL_QUEUE.get(block=True, timeout=60)

                pool.apply_async(self.save_house_data, args=(region_id, house_detail_info))
            except Empty:
                break
            except Exception:
                continue

    def _start_get_house_ids(self):
        tasks = []

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        for k in self.TARGET_REGIONS:
            tasks.append(
                asyncio.ensure_future(
                    self._get_house_ids(self.TARGET_REGIONS[k])
                )
            )

        loop.run_until_complete(asyncio.gather(*tasks))
        loop.close()

    def _start_get_house_detail(self):
        tasks = []

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        for i in range(self.async_tasks_cnt):
            tasks.append(self._get_house_detail())

        loop.run_until_complete(asyncio.gather(*tasks))
        loop.close()

    async def _get_house_ids(self, region_id):
        """
        Get "totalRows" at first cycle (without "firstRow" & "totalRows" in params),
        then get all data until "firstRow" grater than "totalRows"
        """
        prd = self._get_pre_request_data(region_id)

        cookies = prd['cookies']
        headers = {'X-CSRF-TOKEN': prd['csrf_token']}
        params = {'kind': 0, 'region': region_id, 'type': 1, 'searchtype': 1}

        async with aiohttp.ClientSession(cookies=cookies, headers=headers) as session:
            while (
                params.get('firstRow', 0) < int(params.get('totalRows', '0'))
                or not params.get('firstRow')
            ):
                try:
                    async with session.get(f'{self.target_endpoint}home/search/rsList', params=params) as response:
                        rslist = await response.json()

                        house_ids = [self._get_house_id(data) for data in rslist.get('data').get('data')]

                        for house_id in house_ids:
                            self.HOUSE_ID_QUEUE.put((region_id, house_id))

                        if params.get('firstRow'):
                            params['firstRow'] += 30
                        else:
                            params.update({
                                'firstRow': 30,
                                'totalRows': rslist.get('records', '0').replace(',', ''),
                            })
                except Exception:
                    print(f'error: {params}')
                    continue

    async def _get_house_detail(self):
        while True:
            try:
                region_id, house_id = self.HOUSE_ID_QUEUE.get(block=True, timeout=10)

                async with aiohttp.ClientSession() as session:
                    async with session.get(f'{self.target_endpoint}rent-detail-{house_id}.html') as response:
                        self.HOUSE_DETAIL_QUEUE.put((region_id, await response.text()))
            except Empty:
                break
            except Exception:
                print(f'error: {house_id}')
                continue

    @classmethod
    def save_house_data(cls, region_id, house_detail_info):
        data = HouseParser(house_detail_info, region_id).get_house_info()

        cls.MONGO_DB.save(data)
        cls.ES.save(data)

    def _get_pre_request_data(self, region_id):
        cookies = {'urlJumpIp': region_id}
        params = {'kind': 0, 'region': region_id}

        resp = requests.get(self.target_endpoint, params=params)
        soup = BeautifulSoup(resp.text, 'html.parser')

        csrf_token = soup.find("meta", attrs={"name": "csrf-token"}).get('content')
        cookies.update(resp.cookies)

        return {'csrf_token': csrf_token, 'cookies': cookies}

    def _get_house_id(self, data):
        return data.get('houseid')
