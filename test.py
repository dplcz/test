import requests
import re
from selenium import webdriver
from scrapy import Selector
import time
from datetime import datetime
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from peewee import *

db = MySQLDatabase('spider', host='localhost', port=3306,
                   user='root', password='dp20020620')


def getStrName():
    name = '重庆'
    if name.isspace():
        name = input('\n输入城市名:')
        return name
    else:
        return name


def getStrSearch():
    search = 'ios'
    if search.isspace():
        search = input('\n输入要搜索的职位:')
        return search
    else:
        return search


cityname = getStrName()

search = getStrSearch()


def make_table_name(model_class):
    model_name = model_class.__name__
    return model_name.lower() + '_' + search


class BaseModel(Model):
    class Meta:
        database = db
        table_function = make_table_name


class Boss(BaseModel):
    url = TextField(default='')
    content = TextField(default='')
    primary = TextField(default='')
    needs = TextField(default='')
    place = TextField(default='')
    company = TextField(default='')
    welfare = TextField(default='')
    create_data = DateTimeField(default=datetime.now(), verbose_name="添加时间")


def get_boss_info():
    city_url = 'https://www.zhipin.com/wapi/zpgeek/common/data/citysites.json'
    res = requests.get(city_url).text
    pattern = re.compile(r'"name":"(.*?)","code":(.*?),')
    datas = re.findall(pattern, res)
    # print(datas)
    data_dict = {}
    for i in datas:
        name, code = i
        data_dict[name] = code
        print(i[0] + '\t', end='')
    print(data_dict)
    print('\n' + cityname)
    print('\n' + data_dict[cityname])
    url_temp = 'https://www.zhipin.com/c{}/?query={}'.format(
        data_dict[cityname], search)
    return url_temp


def xpath_get_data(sel, xpath):
    if len(sel.xpath(xpath)) != 0:
        return sel.xpath(xpath).extract()[0]
    else:
        return ''


# 创建表
def create_table(table):
    if not table.table_exists():
        table.create_table()


# 删除表


def drop_table(table):
    if table.table_exists():
        table.drop_table()


if __name__ == '__main__':
    url_temp = get_boss_info()
    begin_time = time.time()
    # db.create_tables([Data])
    create_table(Boss)
    url_temp_head = 'https://www.zhipin.com'
    tag = []
    StopFlag = True
    # 不显示浏览器
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument(
        'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36')
    browser = webdriver.Chrome(executable_path='E:\py_code\webdriver/chromedriver.exe', options=chrome_options)
    i = 1
    while StopFlag:
        if i == 1:
            print(url_temp)
            browser.get(url_temp)
        else:
            normal_window = browser.current_window_handle
        time.sleep(0.5)
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
                url.append(xpath_get_data(sel,
                                          '//*[@id="main"]/div/div[3]/ul/li[{}]/div/div[1]/div[1]/div/div[1]/span[1]/a/@href'.format(
                                              k)))
                content.append(xpath_get_data(sel,
                                              '//*[@id="main"]/div/div[3]/ul/li[{}]/div/div[1]/div[1]/div/div[1]/span['
                                              '1]/a/text()'.format(
                                                  k)))
                primary.append(xpath_get_data(sel,
                                              '//*[@id="main"]/div/div[3]/ul/li[{}]/div/div[1]/div[1]/div/div[2]/span/text()'.format(
                                                  k)))
                needs.append(
                    xpath_get_data(sel,
                                   '//*[@id="main"]/div/div[3]/ul/li/div/div[1]/div[1]/div/div[2]/p/text()'.format(k)))
                place.append(xpath_get_data(sel,
                                            '//*[@id="main"]/div/div[3]/ul/li[{}]/div/div[1]/div[1]/div/div[1]/span['
                                            '2]/span/text()'.format(
                                                k)))
                company.append(
                    xpath_get_data(sel,
                                   '//*[@id="main"]/div/div[3]/ul/li[{}]/div/div[1]/div[2]/div/h3/a/text()'.format(k)))
                welfare.append(
                    xpath_get_data(sel, '//*[@id="main"]/div/div[3]/ul/li[{}]/div/div[2]/div[2]/text()'.format(k)))
        else:
            for k in range(1, 31):
                temp_url = xpath_get_data(sel,
                                          '//*[@id="main"]/div/div[2]/ul/li[{}]/div/div[1]/div[1]/div/div[1]/span[1]/a/@href'.format(
                                              k))
                if len(temp_url) == 0:
                    StopFlag = False
                    break
                url.append(temp_url)
                content.append(xpath_get_data(sel,
                                              '//*[@id="main"]/div/div[2]/ul/li[{}]/div/div[1]/div[1]/div/div[1]/span['
                                              '1]/a/text()'.format(
                                                  k)))
                primary.append(xpath_get_data(sel,
                                              '//*[@id="main"]/div/div[2]/ul/li[{}]/div/div[1]/div[1]/div/div[2]/span/text()'.format(
                                                  k)))
                needs.append(
                    xpath_get_data(sel,
                                   '//*[@id="main"]/div/div[2]/ul/li/div/div[1]/div[1]/div/div[2]/p/text()'.format(k)))
                place.append(xpath_get_data(sel,
                                            '//*[@id="main"]/div/div[2]/ul/li[{}]/div/div[1]/div[1]/div/div[1]/span['
                                            '2]/span/text()'.format(
                                                k)))
                company.append(
                    xpath_get_data(sel,
                                   '//*[@id="main"]/div/div[2]/ul/li[{}]/div/div[1]/div[2]/div/h3/a/text()'.format(k)))
                welfare.append(
                    xpath_get_data(sel, '//*[@id="main"]/div/div[2]/ul/li[{}]/div/div[2]/div[2]/text()'.format(k)))
        for n in range(0, len(url)):
            # tag.append([url_temp_head + url[n], content[n], primary[n],
            #            needs[n], place[n], company[n], welfare[n]])
            tag.append(
                Boss(url=url_temp_head + url[n], content=content[n], primary=primary[n], needs=needs[n], place=place[n],
                     company=company[n], welfare=welfare[n],
                     create_data=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
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
    with db.atomic():
        Boss.delete().execute()
        Boss.bulk_create(tag)
        end_time = time.time()
        print('runtime:{}'.format(end_time - begin_time))
