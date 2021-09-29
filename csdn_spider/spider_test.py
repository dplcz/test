"""
抓取
解析
存储
"""

import re
import requests
from bs4 import BeautifulSoup
from scrapy import Selector
import time
from selenium_test import get_cookie
from my_models import Topic, Passage

begin_time = time.time()
http_url = 'https://www.52pojie.cn/'
cookie = get_cookie.get_cookies(http_url)
tag_temp = []
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
        id = []
        pattern = re.compile(r'thread-(.*?)-')
        temp = sel.xpath('//*[@class="s xst"]/text()').extract()
        href = sel.xpath('//*[@class="s xst"]/@href').extract()
        for k in href:
            id.append(re.findall(pattern, k)[0])
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
            # tag_1.append(
            #     [http_url + href[k], temp[k], author[1 + k if m == 1 else k], answer_num[count + k], latest_time[k]])
            passage.id = id[k]
            passage.url = http_url + href[k]
            passage.content = temp[k]
            passage.author = author[1 + k if m == 1 else k]
            passage.answer_num = answer_num[count + k]
            passage.latest_time = latest_time[k]
            exist_passage = passage.select().where(Passage.id == passage.id)
            if exist_passage:
                passage.save()
            else:
                passage.save(force_insert=True)
        time.sleep(0.3)
    # queue.put(tag_1)
    # return tag_1


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
    topic = Topic()
    passage = Passage()
    url_part = get_part_url()
    for i in url_part:
        topic.url = i[0]
        topic.title = i[1]
        topic.save()
        get_part_data(str(i[0]))
