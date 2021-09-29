"""
抓取
解析
存储
"""

import re
import threading
from queue import Queue
import requests
from bs4 import BeautifulSoup
from scrapy import Selector
import pymysql.cursors
import time
from selenium_test import get_cookie

begin_time = time.time()
http_url = 'https://www.52pojie.cn/'
cookie = get_cookie.get_cookies(http_url)
queue = Queue(3)
tag_temp = []
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='dp20020620',
                             database='spider',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36'
}
time_xpath_temp = []
for k in range(5, 7):
    for a in range(4, 7):
        time_xpath_temp.append(
            '/html/body/div[{}]/div[4]/div/div/div[{}]/div[2]/form/table/tbody/tr/td[4]/em/a/text()'.format(k,
                                                                                                            a))


def get_part_url():
    url_part = []
    n = 1
    while len(url_part) == 0:
        if n > 40:
            print('获取失败')
            exit(0)
        print('尝试第{}次'.format(n))
        n += 1
        url = http_url
        res = requests.get(url, cookies=cookie, headers=headers).text.encode('utf-8')
        bs = BeautifulSoup(res, 'html.parser')
        # print(bs.prettify())
        text = str(bs.find('div', id='category_1'))
        pattern = re.compile(r'<tr.*?<a href="(.*?)">.*?alt="(.*?)"', re.S)
        for result in pattern.findall(text):
            url_t, part = result
            url_part.append([url + url_t, part])
        time.sleep(0.5)
    print('获取成功！')
    return url_part


def get_part_data(url):
    tag_1 = []
    global queue, time_xpath_temp
    for m in range(1, 31):
        temp_url_1 = url.split('-')
        temp_url_2 = temp_url_1[2].split('.')
        temp_url = temp_url_1[0] + '-' + temp_url_1[1] + '-' + str(m) + '.' + temp_url_2[1]
        res = requests.get(temp_url, cookies=cookie).text.encode('utf-8')
        sel = Selector(text=res)
        count = 0
        temp = sel.xpath('//*[@class="s xst"]/text()').extract()
        href = sel.xpath('//*[@class="s xst"]/@href').extract()
        author = sel.xpath('//*[@id="threadlisttableid"]/tbody/tr/td[2]/cite/a/text()').extract()
        answer_num = sel.xpath('//*[@class="xi2"]/text()').extract()
        latest_time = []
        for k in time_xpath_temp:
            latest_time = sel.xpath(k).extract()
            if len(latest_time) != 0:
                break
        for k in answer_num:
            if k.isdigit():
                break
            else:
                count += 1
        for k in range(0, len(temp)):
            tag_1.append(
                [http_url + href[k], temp[k], author[1 + k if m == 1 else k], answer_num[count + k], latest_time[k]])
        time.sleep(0.3)
    # queue.put(tag_1)
    return tag_1


'''
    /html/body/div[6]/div[4]/div/div/div[4]/div[2]/form/table/tbody[2]/tr/th/a[3]
    /html/body/div[6]/div[4]/div/div/div[4]/div[2]/form/table/tbody[25]/tr/th/a[2]
    /html/body/div[6]/div[4]/div/div/div[4]/div[2]/form/table/tbody[2]/tr/th/a[3]/href
    https://www.52pojie.cn/forum-2-1.html
    https://www.52pojie.cn/forum-.*?-(.*?).html
'''


def queue_get():
    global tag_temp
    while True:
        tag_temp.append(queue.get())
        print(tag_temp)
        queue.task_done()


if __name__ == '__main__':
    url_part = get_part_url()
    with connection:
        with connection.cursor() as cursor:
            for i in url_part:
                sql = "INSERT INTO `Topic` (`url`, `title`) VALUES (%s, %s)"
                cursor.execute(sql, (i[0], i[1]))
            for i in url_part:
                tag_temp.append(get_part_data(str(i[0])))
            # print(tag_temp)
            for k in tag_temp:
                for i in k:
                    try:
                        sql = "INSERT IGNORE INTO `Passage` (`url`, `content`,`author`,`answer_num`,`latest_time`) " \
                              "VALUES (" \
                              "%s, %s, %s, %s, %s) "
                        cursor.execute(sql, (i[0], i[1], i[2], i[3], i[4]))
                        connection.commit()
                    except:
                        sql = "INSERT IGNORE INTO `Passage` (`url`, `content`,`author`,`answer_num`,`latest_time`) " \
                              "VALUES (" \
                              "%s, %s, %s, %s, %s) "
                        cursor.execute(sql, (i[0], i[1], i[2], 0, i[4]))
                        connection.commit()
            end_time = time.time()
            print('runtime:{}'.format(end_time - begin_time))
            cursor.close()
