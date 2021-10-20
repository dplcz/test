import json
import requests
from scrapy import Selector
from model import Goods, GoodsEvaluate, GoodsEvaluateSummary
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36'}


def get_goods_id():
    search = input('输入要搜索的商品：')
    goods_id = []
    for i in range(1, 5):
        url_temp = 'https://search.jd.com/Search?keyword={}&enc=utf-8&page={}'.format(search, i)
        html = requests.get(url_temp, headers=headers).text
        sel = Selector(text=html)

        goods_temp = sel.xpath('//*[@id="J_goodsList"]/ul/li/div/div[1]/a/@href').extract()
        '''
        //item.jd.com/68827454951.html
        '''
        for i in goods_temp:
            pattern = re.compile(r'\d+')
            goods_id.append(re.findall(pattern, i)[0])
    return list(set(goods_id))


def pares_goods(goods_id):
    statistics = {}
    id = 1
    max_page = 1
    summary = {}
    comments = {}
    goods = Goods()
    goods_evaluate = GoodsEvaluate()
    goods_evaluate_summary = GoodsEvaluateSummary()

    # 获取商品信息
    url_temp = 'https://item.jd.com/{}.html'.format(goods_id)
    html = requests.get(url_temp, headers=headers).text
    sel = Selector(text=html)
    # 规格包装
    # temp = sel.xpath('//*[@id="detail"]/div[2]/div[2]/div[1]/div')
    # for i in temp:
    #     goods.size_box = ''.join(temp.xpath('./'))
    goods.id = goods_id
    # 删去字符串中的空格和换行符
    goods.name = ''.join(sel.xpath('//*[@class="sku-name"]/text()').extract()[0]).strip()
    # 轮播图
    image_list = []
    for i in sel.xpath('//*[@id="spec-list"]/ul/li/img/@src').extract():
        image_list.append('https:' + i)
    goods.image_list = image_list

    # 获取价格
    goods_info_temp = 'https://item-soa.jd.com/getWareBusiness?skuId={}'.format(goods_id)
    goods_info_text = requests.get(goods_info_temp, headers=headers).text.strip()
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
    temp = requests.get(evaluate_url, headers=headers).text
    if temp:
        evaluate_json = json.loads(requests.get(evaluate_url, headers=headers).text)
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
    # exist = goods.select().where(goods.id == goods.id)
    # if exist:
    #     goods.save()
    # else:
    goods.save(force_insert=True)

    # 获取商品标签

    for i in statistics:
        goods_evaluate_summary.tag_id = i['id']
        goods_evaluate_summary.goods = goods
        goods_evaluate_summary.tag = i['name']
        goods_evaluate_summary.num = i['count']
        # exist = goods_evaluate_summary.select().where(
        #     goods_evaluate_summary.tag_id == goods_evaluate_summary.tag_id)
        # if exist:
        #     goods_evaluate_summary.save()
        # else:
        goods_evaluate_summary.save(force_insert=True)

    # 获取评价
    if temp:
        for num in range(0, max_page):
            for i in comments:
                goods_evaluate.id = id
                goods_evaluate.goods = goods
                goods_evaluate.user_head_url = 'https://' + i['userImageUrl']
                goods_evaluate.user_name = i['nickname']
                goods_evaluate.good_info = i['productColor'] + i['productSize']
                goods_evaluate.evaluate_time = i['creationTime']
                goods_evaluate.content = i['content']
                goods_evaluate.star = i['score']
                goods_evaluate.comment_num = i['replyCount']
                goods_evaluate.press_num = i['usefulVoteCount']
                try:
                    image_temp = []
                    for k in i['images']:
                        image_temp.append('https:' + k['imgUrl'])
                    goods_evaluate.image_list = image_temp
                except KeyError:
                    pass
                try:
                    video_temp = []
                    for k in i['videos']:
                        video_temp.append(k['mainUrl'])
                    goods_evaluate.video_list = video_temp
                except KeyError:
                    pass
                exist = goods_evaluate.select().where(goods_evaluate.id == goods_evaluate.id)

                goods_evaluate.save(force_insert=True)
                id += 1
            # print(num)
            if num == 0:
                continue
            evaluate_url = 'https://club.jd.com/comment/productPageComments.action?productId={}&score=0&sortType=5&page={}&pageSize=10&isShadowSku=0&fold=1'.format(
                goods_id, num)
            temp = requests.get(evaluate_url, headers=headers).text.encode('utf-8')
            if temp:
                evaluate_json = json.loads(temp)
                comments = evaluate_json['comments']


if __name__ == '__main__':
    goods_id = get_goods_id()
    for i in goods_id:
        pares_goods(i)
