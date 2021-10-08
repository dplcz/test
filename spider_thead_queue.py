from threading import Thread, Lock
import requests
import re
from selenium import webdriver
from scrapy import Selector
import time
from peewee import Database, TextField, MySQLDatabase, Model, IntegerField
from selenium.webdriver.chrome.options import Options
from queue import Queue

# 无头浏览器设置
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument(
    'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36')

# 解析城市代码
city_url = 'https://www.zhipin.com/wapi/zpgeek/common/data/citysites.json'
res = requests.get(city_url).text
pattern = re.compile(r'"name":"(.*?)","code":(.*?),')
datas = re.findall(pattern, res)
data_dict = {}
for i in datas:
    name, code = i
    data_dict[name] = code
    print(i[0] + '\t', end='')

# 构造搜索网址
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

# 创建全局变量和队列
# page_source_list = []
page_source_queue = Queue(3)
end_num = 0
tag = []

# 连接数据库
db = MySQLDatabase('spider', host='localhost', port=3306, user='root', password='dp20020620')


# 动态创建表名函数
def create_name(model_class):
    return name + search


class BaseModel(Model):
    class Meta:
        database = db
        table_function = create_name


# 模板class
class Data(BaseModel):
    url = TextField(default='')
    content = TextField(default='')
    primary = TextField(default='')
    needs = TextField(default='')
    place = TextField(default='')
    company = TextField(default='')
    welfare = TextField(default='')


# 页面分析线程
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
            page_source_queue.put(browser.page_source)
            sel_temp = Selector(text=browser.page_source)
            if len(sel_temp.xpath('//*[@class="next"]')):
                click_ele = browser.find_element_by_xpath('//*[@class="next"]')
                click_ele.click()
                normal_window = browser.current_window_handle
                print('get page source {}'.format(count))
            else:
                print('get page source {}'.format(count))
                break
            count += 1
        end_num = count


# 页面元素分析线程
class ParseDataThread(Thread):

    def run(self):
        global sel
        StopFlag = True
        # print(count_data)
        count_data = 0
        while StopFlag:
            count_num = 0
            if count_num == 10:
                StopFlag = False
                break
            sel = Selector(text=page_source_queue.get())
            if count_data == 0:
                count_data += 1
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
                    tag.append(Data(url=url_temp_head + url, content=content, primary=primary, needs=needs, place=place,
                                    company=company, welfare=welfare))

            else:
                count_data += 1
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
                    tag.append(Data(url=url_temp_head + url, content=content, primary=primary, needs=needs, place=place,
                                    company=company, welfare=welfare))
                if count_data == end_num:
                    StopFlag = False


# 元素获取
def xpath_get_data(sel, xpath):
    if len(sel.xpath(xpath)) != 0:
        return sel.xpath(xpath).extract()[0]
    else:
        return ''


if __name__ == '__main__':
    data = Data()
    data.create_table()
    page_thread = ParsePageThread()
    data_thread = ParseDataThread()
    begin_time = time.time()
    page_thread.start()
    data_thread.start()

    data_thread.join()
    page_thread.join()
    Data.bulk_create(tag)
    end_time = time.time()
    print('runtime:{}'.format(end_time - begin_time))
