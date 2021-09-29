import requests
import re
from selenium import webdriver
from scrapy import Selector
import pymysql.cursors
import time
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from peewee import MySQLDatabase, Model, TextField

db = MySQLDatabase('spider', host='192.168.31.21', port=3306, user='dp', password='dp20020620')
# 'spider', host='localhost', port=3306, user='root', password='dp20020620'

class BaseModel(Model):
    class Meta:
        database = db
        table_name = 'spider'


class Data(BaseModel):
    url = TextField(default='')
    content = TextField(default='')
    primary = TextField(default='')
    needs = TextField(default='')
    place = TextField(default='')
    company = TextField(default='')
    welfare = TextField(default='')


connection = pymysql.connect(host='192.168.31.21',
                             user='dp',
                             password='dp20020620',
                             database='spider',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
'''
host='localhost',
user='root',
password='dp20020620',
database='spider',
charset='utf8mb4',
cursorclass=pymysql.cursors.DictCursor
'''

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
# print(url_temp)

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument(
    'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36')
begin_time = time.time()


def xpath_get_data(sel, xpath):
    if len(sel.xpath(xpath)) != 0:
        return sel.xpath(xpath).extract()[0]
    else:
        return ''


if __name__ == '__main__':
    db.create_tables([Data])
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
            tag.append([url_temp_head + url[n], content[n], primary[n], needs[n], place[n], company[n], welfare[n]])
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

    with connection:
        with connection.cursor() as cursor:
            sql = "INSERT INTO `data` (`url`, `content`, `primary`,`needs`,`place`,`company`,`welfare`) VALUES (%s, %s, " \
                  "%s, %s, %s, %s, %s) "
            for i in tag:
                cursor.execute(sql, (i[0], i[1], i[2], i[3], i[4], i[5], i[6]))
                connection.commit()
            cursor.close()
            end_time = time.time()
            print('runtime:{}'.format(end_time - begin_time))
