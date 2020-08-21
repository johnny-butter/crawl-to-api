import re
from bs4 import BeautifulSoup


class HouseParser:

    def __init__(self, html, region_id):
        self.soup = BeautifulSoup(html, 'html.parser')
        self.region_id = region_id

    def get_landlord(self):
        return self.soup.find('div', attrs={"class": "avatarRight"}).find('i').text

    def get_landlord_type(self):
        landlord_type_desc = self.soup.find(
            'div', attrs={"class": "avatarRight"}).text

        try:
            landlord_type_desc = re.findall('\（(.*?)\）', landlord_type_desc)[0]
        except:
            landlord_type_desc = re.findall('\((.*?)\)', landlord_type_desc)[0]

        if landlord_type_desc.startswith('屋主'):
            return '屋主'
        elif landlord_type_desc.startswith('仲介'):
            return '仲介'
        elif landlord_type_desc.startswith('代理人'):
            return '代理人'

        return landlord_type_desc

    def get_phone(self):
        return self.soup.find('span', attrs={"class": "dialPhoneNum"}).get('data-value')

    def get_houses_detail(self, specific_info=None):
        all_info = self.soup.find(
            'div', attrs={"class": "detailInfo clearfix"}).find_all('li')

        if specific_info:
            for info in all_info:
                if specific_info in info.text:
                    return info.text.split('\xa0')[-1]
        else:
            return all_info

    def get_house_type(self):
        return self.get_houses_detail('型態')

    def get_house_status(self):
        return self.get_houses_detail('現況')

    def get_gender_limit(self):
        limit = self.soup.find('em', attrs={'title': '男女生皆可'}) or \
            self.soup.find('em', attrs={'title': '男生'}) or \
            self.soup.find('em', attrs={'title': '女生'})

        if limit:
            return limit.get('title')
        else:
            return '男女生皆可'

    def get_house_description(self):
        return self.soup.find('div', attrs={'class': 'houseIntro'}).text.replace('\xa0', ' ')

    def get_house_info(self):
        return {
            'landlord': self.get_landlord(),
            'landlord_type': self.get_landlord_type(),
            'phone': self.get_phone(),
            'house_type': self.get_house_type(),
            'house_status': self.get_house_status(),
            'gender_limit': self.get_gender_limit(),
            'house_description': self.get_house_description(),
            'region': self.region_id,
        }
