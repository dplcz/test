import requests
import re
from selenium import webdriver
from scrapy import Selector
import time
from peewee import Database, TextField, MySQLDatabase, Model, IntegerField
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options

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

db = MySQLDatabase('spider', host='localhost', port=3306, user='root', password='dp20020620')

tag = []


def create_name(model_class):
    return name + search


class BaseModel(Model):
    class Meta:
        database = db
        table_function = create_name


class Data(BaseModel):
    url = TextField(default='')
    content = TextField(default='')
    primary = TextField(default='')
    needs = TextField(default='')
    place = TextField(default='')
    company = TextField(default='')
    welfare = TextField(default='')


def xpath_get_data(sel, xpath):
    if len(sel.xpath(xpath)) != 0:
        return sel.xpath(xpath).extract()[0]
    else:
        return ''


def save_to_mysql(url, content, primary, need, place, company, welfare):
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


if __name__ == '__main__':
    data = Data()
    data.create_table()
    url_temp = 'https://www.zhipin.com/c{}/?query={}'.format(data_dict[name], search)
    # print(url_temp)

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument(
        'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36')
    begin_time = time.time()
    id = 1

    url_temp_head = 'https://www.zhipin.com'
    tag = []
    StopFlag = True
    browser = webdriver.Chrome(executable_path='E:\py_code\webdriver/chromedriver.exe', options=chrome_options)
    browser.implicitly_wait(10)
    i = 1
    while StopFlag:
        if i == 1:
            browser.get(url_temp)
            time.sleep(0.5)
        else:
            normal_window = browser.current_window_handle
        temp = browser.page_source
        sel = Selector(text=temp)
        url = []
        content = []
        primary = []
        needs = []
        place = []
        company = []
        welfare = []
        if i == 1:
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
                welfare = xpath_get_data(sel, '//*[@id="main"]/div/div[3]/ul/li[{}]/div/div[2]/div[2]/text()'.format(k))
                tag.append(Data(url=url_temp_head + url, content=content, primary=primary, needs=needs, place=place,
                                company=company, welfare=welfare))

        else:
            for k in range(1, 31):
                temp_url = xpath_get_data(sel,
                                          '//*[@id="main"]/div/div[2]/ul/li[{}]/div/div[1]/div[1]/div/div[1]/span[1]/a/@href'.format(
                                              k))
                if len(temp_url) == 0:
                    StopFlag = False
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
                welfare = xpath_get_data(sel, '//*[@id="main"]/div/div[2]/ul/li[{}]/div/div[2]/div[2]/text()'.format(k))
                tag.append(Data(url=url_temp_head + url, content=content, primary=primary, needs=needs, place=place,
                                company=company, welfare=welfare))
        if StopFlag == False:
            print('complete {}'.format(i))
            break
        try:
            click_ele = browser.find_element_by_xpath('//*[@class="next"]')
            click_ele.click()
        except NoSuchElementException as e:
            StopFlag = False
            break
        finally:
            print('complete {}'.format(i))
        i += 1
    browser.close()
    Data.bulk_create(tag)
    end_time = time.time()
    print('runtime:{}'.format(end_time - begin_time))
