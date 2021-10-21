import dpspider

if __name__ == '__main__':
    spider = dpspider.Spider()
    res = spider.request('https://www.apiref.com/android-zh/index.html')
    spider.get_len('//*[@id="body-content"]/table/tbody/tr')
    name = []
    for i in range(1, spider.lenth + 1):
        name.append(spider.select_by_scrapy(temp='//*[@id="body-content"]/table/tbody/tr[{}]/td[1]/a/text()'.format(i)))
    print(name)
