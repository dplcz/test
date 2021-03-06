from threading import Thread, Lock
import requests
import re
from selenium import webdriver
from scrapy import Selector
import time
from selenium.webdriver.chrome.options import Options
from pachong.boss_spider.boss_models import Data

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument(
    'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36')
city_url = 'https://www.zhipin.com/wapi/zpgeek/common/data/citysites.json'
res = requests.get(city_url).text
pattern = re.compile(r'"name":"(.*?)","code":(.*?),')
datas = re.findall(pattern, res)
data_dict = {}
for i in datas:
    name, code = i
    data_dict[name] = code
    print(i[0] + '\t', end='')
name = input('\n输入城市名:')
while True:
    try:
        _temp = data_dict[name]
        break
    except KeyError:
        name = input('未找到相关城市，请重新输入:')

search = input('输入要搜索的职位:')
url_temp = 'https://www.zhipin.com/c{}/?query={}'.format(data_dict[name], search)
url_temp_head = 'https://www.zhipin.com'
id = 1
page_source_list = []
end_num = 0
Lock = Lock()


class ParsePageThread(Thread):
    def run(self):
        browser = webdriver.Chrome(executable_path='E:\py_code\webdriver/chromedriver.exe', options=chrome_options)
        browser.implicitly_wait(10)
        count = 1
        global end_num
        if count == 1:
            time.sleep(1)
        browser.get(url_temp)
        while 1:
            page_source_list.append(browser.page_source)
            sel_temp = Selector(text=browser.page_source)
            if len(sel_temp.xpath('//*[@class="next"]')):
                print('get page source {}'.format(count))
                click_ele = browser.find_element_by_xpath('//*[@class="next"]')
                click_ele.click()
                normal_window = browser.current_window_handle
            else:
                print('get page source {}'.format(count))
                break
            count += 1
        end_num = count


class ParseDataThread(Thread):
    def __init__(self, url, count_data):
        super().__init__()
        self.url = url
        self.count_data = count_data

    def run(self):
        sel = Selector(text=self.url)

        if self.count_data == 0:
            for k in range(1, 31):
                url = xpath_get_data(sel,
                                     '//*[@id="main"]/div/div[3]/ul/li[{}]/div/div[1]/div[1]/div/div[1]/span[1]/a/@href'.format(
                                         k))
                content = xpath_get_data(sel,
                                         '//*[@id="main"]/div/div[3]/ul/li[{}]/div/div[1]/div[1]/div/div[1]/span['
                                         '1]/a/text()'.format(
                                             k))
                primary = xpath_get_data(sel,
                                         '//*[@id="main"]/div/div[3]/ul/li[{}]/div/div[1]/div[1]/div/div[2]/span/text()'.format(
                                             k))
                needs = xpath_get_data(sel,
                                       '//*[@id="main"]/div/div[3]/ul/li/div/div[1]/div[1]/div/div[2]/p/text()'.format(
                                           k))
                place = xpath_get_data(sel,
                                       '//*[@id="main"]/div/div[3]/ul/li[{}]/div/div[1]/div[1]/div/div[1]/span['
                                       '2]/span/text()'.format(
                                           k))
                company = xpath_get_data(sel,
                                         '//*[@id="main"]/div/div[3]/ul/li[{}]/div/div[1]/div[2]/div/h3/a/text()'.format(
                                             k))
                welfare = xpath_get_data(sel,
                                         '//*[@id="main"]/div/div[3]/ul/li[{}]/div/div[2]/div[2]/text()'.format(k))
                save_to_mysql(url_temp_head + url, content, primary, needs, place, company, welfare)

        else:
            for k in range(1, 31):
                temp_url = xpath_get_data(sel,
                                          '//*[@id="main"]/div/div[2]/ul/li[{}]/div/div[1]/div[1]/div/div[1]/span[1]/a/@href'.format(
                                              k))
                if len(temp_url) == 0:
                    break
                url = temp_url
                content = xpath_get_data(sel,
                                         '//*[@id="main"]/div/div[2]/ul/li[{}]/div/div[1]/div[1]/div/div[1]/span['
                                         '1]/a/text()'.format(
                                             k))
                primary = xpath_get_data(sel,
                                         '//*[@id="main"]/div/div[2]/ul/li[{}]/div/div[1]/div[1]/div/div[2]/span/text()'.format(
                                             k))
                needs = xpath_get_data(sel,
                                       '//*[@id="main"]/div/div[2]/ul/li/div/div[1]/div[1]/div/div[2]/p/text()'.format(
                                           k))
                place = xpath_get_data(sel,
                                       '//*[@id="main"]/div/div[2]/ul/li[{}]/div/div[1]/div[1]/div/div[1]/span['
                                       '2]/span/text()'.format(
                                           k))
                company = xpath_get_data(sel,
                                         '//*[@id="main"]/div/div[2]/ul/li[{}]/div/div[1]/div[2]/div/h3/a/text()'.format(
                                             k))
                welfare = xpath_get_data(sel,
                                         '//*[@id="main"]/div/div[2]/ul/li[{}]/div/div[2]/div[2]/text()'.format(k))
                save_to_mysql(url_temp_head + url, content, primary, needs, place, company, welfare)
        print('complete {}'.format(self.count_data + 1))


def save_to_mysql(url, content, primary, need, place, company, welfare):
    Lock.acquire()
    global id
    data.id = id
    data.url = url
    data.content = content
    data.primary = primary
    data.needs = need
    data.place = place
    data.company = company
    data.welfare = welfare
    id_exist = data.select().where(Data.id == data.id)
    if id_exist:
        data.save()
    else:
        data.save(force_insert=True)
    id += 1
    Lock.release()


def xpath_get_data(sel, xpath):
    if len(sel.xpath(xpath)) != 0:
        return sel.xpath(xpath).extract()[0]
    else:
        return ''


if __name__ == '__main__':
    StopFlag = True
    data = Data()
    page_thread = ParsePageThread()

    begin_time = time.time()
    page_thread.start()
    count = 0
    t = []
    while StopFlag:
        try:
            data_thread = ParseDataThread(page_source_list.pop(), count)
            t.append(data_thread)
        except IndexError:
            continue
        count += 1
        time.sleep(0.05)
        data_thread.start()
        if count == end_num:
            StopFlag = False

    for i in t:
        i.join()
    page_thread.join()

    end_time = time.time()
    print('runtime:{}'.format(end_time - begin_time))
