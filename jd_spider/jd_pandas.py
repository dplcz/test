import json
import re
import requests
from threading import Thread
from requests.exceptions import ProxyError
import time
import pandas as pd
from pandas import DataFrame
from scrapy import Selector
from fake_useragent import UserAgent
# import get_cookie

# cookie = get_cookie.get_cookies('https://passport.jd.com/new/login.aspx')
ua = UserAgent()
search = ''

headers_orig = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36'}

headers_com_num = {
    'Cookie': 'shshshfpa=92782c4d-8ab6-bd36-f22d-2de9da3f434f-1617459630; __jdu=16174596296711566340432; '
              'shshshfpb=n34KPsHP3%20E6xwTo58KOsPQ%3D%3D; pinId=XtYy5vcfDs_VHK4jY9RVILV9-x-f3wj7; '
              'user-key=ccf69d2b-48c1-41d8-905d-4483bc941e0c; ipLoc-djd=12-978-4459-0; areaId=12; '
              'PCSYCityID=CN_320000_320400_320412; jwotest_product=99; '
              'unpl'
              '=V2_ZzNtbRJeSxNyWE9SLExUDGICGltKBxdFcQoSASsZVQdvBBAKclRCFnUURlVnGl0UZAIZXEdcQRFFCEdkeB5fA2AFEFlBZxBFLV0CFi9JH1c%2bbRRcRldFFXAOQWRLGlw1ZwIiXUVXRRBxAEFXcx5aBWcHFVpAUkIQdwt2ZHwpbDVuBBVdQlZzFEUJdhYvRVsCYwsQWg9XRBVzDUJcfBpUAmEDEllFUEEQdA1EV0sYbAY%3d; __jdv=76161171|baidu-search|t_262767352_baidusearch|cpc|705171476_0_a8976a87fd9840979aea53eda183963f|1634747187921; pin=jd_7af96c06f8b2f; unick=jd_7af96c06f8b2f; _tp=7KIqgJKVmtSv7UDkoUI%2Fl8b2bTfUyC0%2BlyC4W0C127s%3D; _pst=jd_7af96c06f8b2f; TrackID=1D-HEM47SduEt4Zq-dDsLtYO_DkeIdchRX9J2-GKS9Sr3o7GXNdvohEOukh2p1EB9G7QG3LMMasnYm7GYIWbzE-18QOWsyht4G0r5XXdUHMJ0wofMCH-q5V5g9-_TbOuy; __jdc=122270672; __jda=122270672.16174596296711566340432.1617459629.1634868612.1634917208.23; shshshfp=e3b04f00ac09d431c05c48093c970bec; token=8c757c41721af1b8a1326193852a19f9,2,908287; __tk=1813e891067185bc9291e217ba8a9d6b,2,908287; shshshsID=58e4cd9c5ca31b6e25387e88ecf24397_4_1634917474141; JSESSIONID=DCDA1B9649098E23095B8E91BE434127.s1; __jdb=122270672.7.16174596296711566340432|23.1634917208; 3AB9D23F7A4B3C9B=2F6NEY73JMUUDRUA6IKY7LGCXGEQ4CLDAGC5KGYD4BJ2AFPHKHCQFNKYZCLYZPR7GTZUGAUP3WISZ6KKQM3QZUTKR4',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36'}


def get_headers():
    headers = {
        'User-Agent': ua.random}
    return headers


def get_goods_id():
    global search
    search = input('输入要搜索的商品：')
    goods_id = []
    for i in range(1, 3):
        url_temp = 'https://search.jd.com/Search?keyword={}&enc=utf-8&page={}'.format(search, i)
        html = requests.get(url_temp, headers=get_headers()).text
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


def get_comment_tag(tag_id):
    flag = True
    url = 'https://club.jd.com/comment/productPageComments.action?productId={}&score=0&sortType=5&page=0&pageSize=10&isShadowSku=0&fold=1'.format(
        tag_id)
    proxy = get_proxy()
    temp = ''
    while flag:
        try:
            temp = requests.get(url, headers=get_headers(), proxies=proxy, timeout=3).text
            if len(temp) != 0:
                flag = False
            else:
                time.sleep(1)
                print('temp is []   sleep 1s')
                proxy = get_proxy()
        except ProxyError as e:
            print(e)
            time.sleep(1)
            print('sleep 1s')
            proxy = get_proxy()
            continue
    evaluate_json = json.loads(temp)
    statistics = evaluate_json['hotCommentTagStatistics']
    for i in statistics:
        goods_evaluate_summary.append([str(tag_id), i['name'], i['count']])

    t_list = []
    for i in range(1, 4):
        t = Thread(target=get_comment, args=(tag_id, proxy, i,))
        t.start()
        t_list.append(t)
    for i in t_list:
        i.join()


def get_comment(goods_id, proxies, score):
    comment_dict = {3: goods_evaluate_good, 2: goods_evaluate_general, 1: goods_evaluate_poor}
    url = 'https://club.jd.com/comment/skuProductPageComments.action?productId={}&score={}&sortType=5&page=0&pageSize=10&isShadowSku=0&fold=1'.format(
        goods_id, score)
    '''
    score = 3 good
    score = 2 general
    score = 1 poor
    '''
    temp = ''
    while len(temp) == 0:
        try:
            temp = requests.get(url, headers=get_headers(), proxies=proxies, timeout=3).text
        except ProxyError as e:
            print(e)
            time.sleep(1)
            pass
    if temp:
        evaluate_json = json.loads(temp)
        comment = evaluate_json['comments']
        for i in comment:
            id_temp = str(goods_id)
            user_name = get_comment_data(i, 'nickname')
            good_info = get_comment_data(i, 'productColor') + get_comment_data(i, 'productSize')
            evaluate_time = get_comment_data(i, 'creationTime')
            content = get_comment_data(i, 'content')
            star = get_comment_data(i, 'score')
            comment_num = get_comment_data(i, 'replyCount')
            press_num = get_comment_data(i, 'usefulVoteCount')
            comment_dict[score].append(
                [id_temp, user_name, good_info, evaluate_time, content, star, comment_num, press_num])
            '''
            '商品id', '用户名', '购买商品信息', '评论时间', '评论内容', '评分', '评论数', '点赞数'
            '''


def get_comment_num(temp):
    pattern = re.compile(r'\d+')
    if '+' in temp and '万' not in temp:
        return int(re.findall(pattern, temp)[0])
    elif '万' in temp:
        return int(re.findall(pattern, temp)[0]) * 10000


def pares_goods(goods_id):
    global goods_price
    goods_supplier = ''
    goods_name = ''

    # 获取商品信息
    url_temp = 'https://item.jd.com/{}.html'.format(goods_id)
    html = requests.get(url_temp, headers=get_headers()).text
    sel = Selector(text=html)
    goods_id_temp = str(goods_id)
    # 删去字符串中的空格和换行符
    try:
        goods_name = ''.join(sel.xpath('//*[@class="sku-name"]/text()').extract()[0]).strip()
    except IndexError:
        pass
    goods_url = url_temp
    # 轮播图
    image_list = []
    for i in sel.xpath('//*[@id="spec-list"]/ul/li/img/@src').extract():
        image_list.append('https:' + i)
    goods_image_list = image_list

    # 获取价格
    goods_info_temp = 'https://item-soa.jd.com/getWareBusiness?skuId={}'.format(goods_id)
    goods_info_text = requests.get(goods_info_temp, headers=get_headers()).text.strip()
    goods_info_json = json.loads(goods_info_text)
    if goods_info_json:
        # 价格
        goods_price = float(goods_info_json['price']['p'])
        # 供应商
        supplier = goods_info_json['stockInfo']['serviceInfo']
        if supplier:
            pattern = re.compile(r'(.*?)<span class=\'hl_red\'>(.*?)</span>(.*?)\.')
            goods_supplier = ''.join(list(re.findall(pattern, supplier)[0]))

    temp_url = 'https://club.jd.com/comment/productCommentSummaries.action?referenceIds={}'.format(goods_id)
    temp = requests.get(temp_url, headers=headers_com_num).text
    if temp:
        evaluate_json = json.loads(temp)
        summary = evaluate_json['CommentsCount'][0]
        # 评论统计

        goods_comment_num = get_comment_num(summary['CommentCountStr'])
        goods_image_comment_num = get_comment_num(summary['ShowCountStr'])
        goods_video_comment_num = get_comment_num(summary['VideoCountStr'])
        goods_good_comment_num = get_comment_num(summary['GoodCountStr'])
        goods_mid_comment_num = get_comment_num(summary['GeneralCountStr'])
        goods_bad_comment_num = get_comment_num(summary['PoorCountStr'])
        goods.append(
            [goods_id_temp, goods_name, goods_price, goods_supplier, goods_url, goods_image_list, goods_comment_num,
             goods_image_comment_num, goods_video_comment_num, goods_good_comment_num,
             goods_mid_comment_num, goods_bad_comment_num])
    get_comment_tag(goods_id)
    print('complete {}'.format(goods_id))


if __name__ == '__main__':
    writer = pd.ExcelWriter('jd_spider.xlsx')
    goods = []
    goods_evaluate_summary = []
    goods_evaluate_good = []
    goods_evaluate_general = []
    goods_evaluate_poor = []
    goods_id = get_goods_id()
    for i in goods_id:
        pares_goods(i)

    df_goods = DataFrame(data=goods,
                         columns=['商品id', '商品名', '价格', '供应商', '网址', '商品轮播图', '评论数', '晒图数', '视频数', '好评数', '中评数',
                                  '差评数'])
    df_summary = DataFrame(data=goods_evaluate_summary, columns=['商品id', '标签', '数量'])
    df_comment_good = DataFrame(data=goods_evaluate_good,
                                columns=['商品id', '用户名', '购买商品信息', '评论时间', '评论内容', '评分', '评论数', '点赞数'])
    df_comment_genera = DataFrame(data=goods_evaluate_general,
                                  columns=['商品id', '用户名', '购买商品信息', '评论时间', '评论内容', '评分', '评论数', '点赞数'])
    df_comment_poor = DataFrame(data=goods_evaluate_poor,
                                columns=['商品id', '用户名', '购买商品信息', '评论时间', '评论内容', '评分', '评论数', '点赞数'])
    df_goods = df_goods.set_index('商品id')
    df_summary = df_summary.set_index('商品id')
    df_comment_good = df_comment_good.set_index('商品id')
    df_comment_genera = df_comment_genera.set_index('商品id')
    df_comment_poor = df_comment_poor.set_index('商品id')
    df_goods.to_excel(writer, index=True, sheet_name='商品信息', encoding='utf-8')
    df_summary.to_excel(writer, index=True, sheet_name='商品标签统计', encoding='utf-8')
    df_comment_good.to_excel(writer, index=True, sheet_name='好评', encoding='utf-8')
    df_comment_genera.to_excel(writer, index=True, sheet_name='中评', encoding='utf-8')
    df_comment_poor.to_excel(writer, index=True, sheet_name='差评', encoding='utf-8')
    writer.save()
