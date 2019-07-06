import requests
import time
import pymongo
import copy
from lxml import etree


class MongoContext(object):
    '''
    mogngodb数据库上下文管理器
    '''
    def __enter__(self):
        '''
        连接数据库
        :return:
        '''
        self.client = pymongo.MongoClient('localhost', 27017)
        self.db = self.client.taobao_spider
        return self
        pass

    def insert_goods(self, good_dict):
        '''
        插入商品简介
        :return:
        '''
        self.db.goods.insert_one(good_dict)
        pass

    def insert_detail(self, detail_dict):
        '''
        插入商品详情
        :return:
        '''
        self.db.detail.insert_one(detail_dict)
        pass

    def insert_set(self, detail_id):
        '''
        判断商品是已经否存在
        :return:
        '''
        result = self.db.set.find_one()
        if not result:
            self.db.set.insert_one({'detail_id': [detail_id]})
            return True
            pass
        old_len = len(result['detail_id'])
        result_add = copy.copy(result['detail_id'])
        result_add.append(detail_id)
        new_len = len(set(result_add))
        if new_len > old_len:
            my_query = {'detail_id': result['detail_id']}
            new_values = {'$set': {'detail_id': list(result_add)}}
            self.db.set.update_one(my_query, new_values)
            return True
            pass
        return False
        pass

    def get_goods(self, page=1):
        '''
        取出商品
        :return:
        '''
        try:
            result = self.db.goods.find()
            start = int((result.count() / 10 - page) * 10)
            end = int((result.count() / 10 - (page-1)) * 10)
            return result[start:end]
        except Exception as ex:
            return []
            pass
        pass

    def get_detail(self, good_id):
        '''
        取出商品的详情
        :return:
        '''
        result = self.db.detail.find_one({'auctionId': good_id})
        return result
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()
        pass
    pass


def get_detail(url, headers , detail_dict=None):
    '''
    解析详情页面
    :param url:
    :param headers:
    :return:
    '''
    data = requests.get(url, headers=headers)
    html = etree.HTML(data.text)
    # 解析页面，获取所需要的数据
    try:
        detail_dict['img_list'] = html.xpath('//div[@class="tb-thumb-content"]/ul/li/a/img/@src')
        if not detail_dict['img_list']:
            detail_dict['img_list'] = html.xpath('//ul[@id="J_UlThumb"]/li/div/a/img/@data-src')
            pass
        detail_dict['title'] = html.xpath('//div[@class="tb-detail-hd"]/h1/text()')
        if not detail_dict['title']:
            detail_dict['title'] = html.xpath('//div[@id="J_Title"]/h3/text()')
            pass
        detail_dict['sub_title'] = html.xpath('//div[@class="tb-detail-hd"]/p/text()')
        detail_dict['yardage'] = html.xpath('//ul[@class="tm-clear J_TSaleProp     "]/li/a/span/text()')
        if not detail_dict['yardage']:
            detail_dict['yardage'] = html.xpath('//ul[@class="J_TSaleProp tb-clearfix"]/li/a/span/text()')
            pass
        detail_dict['sub_img_list'] = html.xpath('//ul[@class="tm-clear J_TSaleProp tb-img     "]/li/a/@style')
        if not detail_dict['sub_img_list']:
            detail_dict['sub_img_list'] = html.xpath('//ul[@class="J_TSaleProp tb-img tb-clearfix"]/li/a/@style')
            pass
        detail_dict['sub_img_name_list'] = html.xpath('//ul[@class="tm-clear J_TSaleProp tb-img     "]/li/a/span/text()')
        if not detail_dict['sub_img_name_list']:
            detail_dict['sub_img_name_list'] = html.xpath('//ul[@class="J_TSaleProp tb-img tb-clearfix"]/li/a/span/text()')
            pass
    except Exception as ex:
        print(ex.args)
        pass
    pass


# 定时任务
def get_content(url):
    '''
    获取页面内容
    :param url:
    :return:
    '''
    headers = {
        'Referer': 'https://pub.alimama.com/promo/search/index.htm?floorId=19457&fn=hot',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',

    }
    data = requests.get(url, headers=headers)
    for item in data.json()['data']['pageList']:
        time.sleep(0.5)
        try:
            with MongoContext() as db:
                if db.insert_set(item['auctionId']):
                    good_dict = {
                        'leafCatId': item['leafCatId'],
                        'couponLeftCount': item['couponLeftCount'],
                        'reservePrice': item['reservePrice'],
                        'zkPrice': item['zkPrice'],
                        'tkCommonRate': item['tkCommonRate'],
                        'tkCommonFee': item['tkCommonFee'],
                        'couponAmount': item['couponAmount'],
                        'auctionId': item['auctionId'],
                        'auctionUrl': item['auctionUrl'],
                        'biz30day': item['biz30day'],
                        'shopTitle': item['shopTitle'],
                        'pictUrl': item['pictUrl'],
                        'title': item['title'],
                    }
                    db.insert_goods(good_dict)
                    detail_dict = {
                        'auctionId': item['auctionId'],
                        'reservePrice': item['reservePrice'],
                        'zkPrice': item['zkPrice'],
                        'pictUrl': item['pictUrl'],
                    }
                    get_detail(item['auctionUrl'], headers, detail_dict)
                    db.insert_detail(detail_dict)
                    pass
            pass
        except Exception as ex:
            print(ex.args)
            pass
        pass
    time.sleep(2)
    pass


def task():
    for i in range(1, 13):
        print('第{}页'.format(i))
        get_content('https://pub.alimama.com/items/search.json?toPage={}&pageSize=60'.format(i))
    pass







