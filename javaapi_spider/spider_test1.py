import requests
import re
from scrapy import Selector
from peewee import Database, TextField, MySQLDatabase, Model, IntegerField

url = 'https://www.apiref.com/android-zh/index.html'
url_temp = 'https://www.apiref.com'
db = MySQLDatabase('spider', host='localhost', port=3306, user='root', password='dp20020620')


def create_name(model_class):
    return '安卓api'


class BaseModel(Model):
    class Meta:
        database = db
        table_function = create_name


class Data(BaseModel):
    url = TextField(default='')
    api_name = TextField(default='')
    text = TextField(default='')


def xpath_get_data(sel, xpath):
    if len(sel.xpath(xpath)) != 0:
        return sel.xpath(xpath).extract()[0]
    else:
        return ''


def parse_page():
    res = requests.get(url).text.encode(requests.get(url).encoding)
    sel = Selector(text=res)
    tag = sel.xpath('//*[@id="body-content"]/table/tbody/tr')
    data = []
    for i in range(1, len(tag) + 1):
        tag_name = xpath_get_data(sel, '//*[@id="body-content"]/table/tbody/tr[{}]/td[1]/a/text()'.format(i))
        tag_url = xpath_get_data(sel, '//*[@id="body-content"]/table/tbody/tr[{}]/td[1]/a/@href'.format(i))
        tag_url = re.sub(r'\.\.', url_temp, tag_url)
        tag_text = xpath_get_data(sel, '//*[@id="body-content"]/table/tbody/tr[{}]/td[2]/p/text()'.format(i))
        data.append(Data(url=tag_url, api_name=tag_name, text=tag_text))
    return data


if __name__ == '__main__':
    data = Data()
    data.create_table()
    data = parse_page()
    Data.bulk_create(data)
