# -*- coding:utf-8 -*-

import datetime
import peewee
import requests
import logging
from time import sleep

from bs4 import BeautifulSoup
from bs4.element import Tag

from model import nyaa_magnet, DoesNotExist, OperationalError

logging.basicConfig(
    format='[%(asctime)s] - %(levelname)s - %(module)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO,
    handlers=[logging.FileHandler("/root/cron/nyaa-crawler/run.log"), logging.StreamHandler()]
)

def crawler_nyaa(html):
    soup = BeautifulSoup(html, 'html5lib')
    all_td = soup.find_all('td')
    create_count = 0
    update_count = 0
    for i in range(0, len(all_td), 8):
        saved = dict()
        for title_test in all_td[1+i].contents:
            if isinstance(title_test, Tag):
                # print(type(title_test), i)
                try:
                    saved['title'] = title_test['title']
                except KeyError:
                    pass
        try:
            saved['magnet'] = all_td[2+i].contents[3]['href']
            saved['size']        = all_td[3+i].contents[0]
            saved['upload_time'] = datetime.datetime.strptime(all_td[4+i].contents[0], '%Y-%m-%d %H:%M')
            saved['seeders']     = int(all_td[5+i].contents[0])
            saved['downloaders'] = int(all_td[6+i].contents[0])
            saved['comleted']    = int(all_td[7+i].contents[0])
        except IndexError:
            logging.warning('index error {}'.format(str(saved)))
            continue
        if saved['comleted'] == 0 or saved['seeders'] < 10:
            continue
        try:
            item = nyaa_magnet.get((nyaa_magnet.magnet == saved['magnet']) or (nyaa_magnet.title == saved['title']))
            if item.seeders == saved['seeders'] or item.downloaders == saved['downloaders'] or item.comleted == saved['comleted']:
                item.seeders = saved['seeders']
                item.downloaders = saved['downloaders']
                item.comleted = saved['comleted']
                item.save()
                update_count += 1
        except DoesNotExist:
            for _ in range(5):
                try:
                    nyaa_magnet.create(**saved)
                    create_count += 1
                    break
                except OperationalError as e:
                    logging.warning('OperationalError: {}  retry: {}'.format(e, _+1))
                    sleep(1)
        except IndexError:
            continue
    logging.info('收录{}个种子, 更新{}个种子'.format(create_count, update_count))

if __name__ == '__main__':
    
    for page in range(1, 6):
        # 爬取第page页
        try:
            nyaa = requests.get('https://sukebei.nyaa.si/?c=2_2&s=leechers&o=desc&p={}'.format(page))
            logging.info('开始爬取第{}页...'.format(page))
            crawler_nyaa(nyaa.text)
        except Exception as e:
            logging.error(e)
        sleep(3)
    
    
    
    
