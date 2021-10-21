import json
import re
import requests
from requests.exceptions import ProxyError
import time
from scrapy import Selector
from model import Goods, GoodsEvaluate, GoodsEvaluateSummary
from fake_useragent import UserAgent
import get_cookie

cookie = get_cookie.get_cookies('https://passport.jd.com/new/login.aspx')
ua = UserAgent()
id = 1


def get_headers():
    headers = {
        'User-Agent': ua.random}
    return headers


def get_goods_id():
    search = input('输入要搜索的商品：')
    goods_id = []
    for i in range(1, 2):
        url_temp = 'https://search.jd.com/Search?keyword={}&enc=utf-8&page={}'.format(search, i)
        html = requests.get(url_temp, headers=get_headers(), cookies=cookie).text
        sel = Selector(text=html)

        goods_temp = sel.xpath('//*[@id="J_goodsList"]/ul/li/div/div[1]/a/@href').extract()
        '''
        //item.jd.com/68827454951.html
        '''
        for i in goods_temp:
            pattern = re.compile(r'\d+')
            goods_id.append(re.findall(pattern, i)[0])
    return list(set(goods_id))


def get_proxy():
    temp = requests.get(
        'http://api.tianqiip.com/getip?secret=732kzp0t7w0rf8ii&type=json&num=1&time=3&port=2').text.strip()
    proxy_json = json.loads(temp)
    proxyHost = proxy_json['data'][0]['ip']
    proxyPort = proxy_json['data'][0]['port']
    proxyMeta = "http://%(host)s:%(port)s" % {
        "host": proxyHost,
        "port": proxyPort,
    }
    proxies = {
        "http": proxyMeta,
        "https": proxyMeta
    }
    return proxies


def get_comment_data(i, tag_name):
    try:
        temp = i[tag_name]
        return temp
    except KeyError:
        return ''


def pares_goods(goods_id):
    global id
    flag = True
    statistics = {}
    max_page = 1
    summary = {}
    comments = {}
    comments_save = []

    # 获取商品信息
    url_temp = 'https://item.jd.com/{}.html'.format(goods_id)
    html = requests.get(url_temp, headers=get_headers(), cookies=cookie).text
    sel = Selector(text=html)
    # 规格包装
    # temp = sel.xpath('//*[@id="detail"]/div[2]/div[2]/div[1]/div')
    # for i in temp:
    #     goods.size_box = ''.join(temp.xpath('./'))
    goods.id = goods_id
    # 删去字符串中的空格和换行符
    goods.name = ''.join(sel.xpath('//*[@class="sku-name"]/text()').extract()[0]).strip()
    goods.url = url_temp
    # 轮播图
    image_list = []
    for i in sel.xpath('//*[@id="spec-list"]/ul/li/img/@src').extract():
        image_list.append('https:' + i)
    goods.image_list = image_list

    # 获取价格
    goods_info_temp = 'https://item-soa.jd.com/getWareBusiness?skuId={}'.format(goods_id)
    goods_info_text = requests.get(goods_info_temp, headers=get_headers(), cookies=cookie).text.strip()
    goods_info_json = json.loads(goods_info_text)
    if goods_info_json:
        # 价格
        goods.price = float(goods_info_json['price']['p'])
        # 供应商
        supplier = goods_info_json['stockInfo']['serviceInfo']
        if supplier:
            pattern = re.compile(r'(.*?)<span class=\'hl_red\'>(.*?)</span>(.*?)\.')
            goods.supplier = ''.join(list(re.findall(pattern, supplier)[0]))

    # 获取商品评价
    evaluate_url = 'https://club.jd.com/comment/productPageComments.action?productId={}&score=0&sortType=5&page={}&pageSize=10&isShadowSku=0&fold=1'.format(
        goods_id, 0)
    proxy = get_proxy()
    temp = ''
    while flag:
        try:
            temp = requests.get(evaluate_url, headers=get_headers(), cookies=cookie, proxies=proxy).text
            if len(temp) != 0:
                flag = False
            else:
                time.sleep(1)
                print('sleep 1s')
                proxy = get_proxy()
        except ProxyError:
            time.sleep(1)
            print('sleep 1s')
            proxy = get_proxy()
            continue
    if temp:
        evaluate_json = json.loads(temp)
        max_page = evaluate_json['maxPage']
        summary = evaluate_json['productCommentSummary']
        # 性能统计
        statistics = evaluate_json['hotCommentTagStatistics']
        comments = evaluate_json['comments']

        goods.comment_num = summary['commentCountStr']
        goods.image_comment_num = summary['showCountStr']
        goods.video_comment_num = summary['videoCountStr']
        goods.add_comment_num = summary['afterCountStr']
        goods.good_comment_num = summary['goodCountStr']
        goods.mid_comment_num = summary['generalCountStr']
        goods.bad_comment_num = summary['poorCountStr']
    exist = goods.select().where(goods.id == Goods.id)
    if exist:
        goods.save()
    else:
        goods.save(force_insert=True)

    # 获取商品标签

    for i in statistics:
        goods_evaluate_summary.tag_id = i['id'] + '_' + str(goods_id)
        goods_evaluate_summary.goods = goods
        goods_evaluate_summary.tag = i['name']
        goods_evaluate_summary.num = i['count']
        exist = goods_evaluate_summary.select().where(
            goods_evaluate_summary.tag_id == GoodsEvaluateSummary.tag_id)
        if exist:
            goods_evaluate_summary.save()
        else:
            goods_evaluate_summary.save(force_insert=True)

    # 获取评价
    if temp:
        for num in range(0, int(max_page)):
            for i in comments:
                goods_evaluate = {}
                goods_evaluate['id'] = id
                goods_evaluate['goods'] = goods
                goods_evaluate['user_head_url'] = (
                        'https://' + get_comment_data(i, 'userImageUrl')) if get_comment_data(i,
                                                                                              'userImageUrl') else ''
                goods_evaluate['user_name'] = get_comment_data(i, 'nickname')
                goods_evaluate['good_info'] = get_comment_data(i, 'productColor') + get_comment_data(i, 'productSize')
                goods_evaluate['evaluate_time'] = get_comment_data(i, 'creationTime')
                goods_evaluate['content'] = get_comment_data(i, 'content')
                goods_evaluate['star'] = get_comment_data(i, 'score')
                goods_evaluate['comment_num'] = get_comment_data(i, 'replyCount')
                goods_evaluate['press_num'] = get_comment_data(i, 'usefulVoteCount')

                image_temp = []
                for k in get_comment_data(i, 'images'):
                    image_temp.append(
                        ('https:' + get_comment_data(k, 'imgUrl')) if len(get_comment_data(k, 'imgUrl')) else '')
                goods_evaluate['image_list'] = image_temp

                video_temp = []
                for k in get_comment_data(i, 'videos'):
                    video_temp.append(get_comment_data(k, 'mainUrl'))
                goods_evaluate['video_list'] = video_temp
                comments_save.append(goods_evaluate)
                # exist = goods_evaluate.select().where(goods_evaluate.id == GoodsEvaluate.id)
                # if exist:
                #     goods_evaluate.save()
                # else:
                #     goods_evaluate.save(force_insert=True)
                id += 1
            # print(num)
            if num == 0:
                continue
            evaluate_url = 'https://club.jd.com/comment/productPageComments.action?productId={}&score=0&sortType=5&page={}&pageSize=10&isShadowSku=0&fold=1'.format(
                goods_id, num)
            time.sleep(0.1)
            temp = requests.get(evaluate_url, headers=get_headers(), cookies=cookie).text.encode(
                'utf-8')
            if temp:
                evaluate_json = json.loads(temp)
                comments = evaluate_json['comments']
        GoodsEvaluate.insert_many(comments_save[0:]).execute()
    else:
        print(temp)
    print('complete {}'.format(goods_id))


if __name__ == '__main__':
    goods = Goods()
    # goods_evaluate = GoodsEvaluate()
    # goods_evaluate = {}
    goods_evaluate_summary = GoodsEvaluateSummary()
    goods_id = get_goods_id()
    for i in goods_id:
        pares_goods(i)
