# flask_apscheduler_spider
## flask框架开启定时任务 定时爬取淘宝联盟商品信息flask_apscheduler

* 项目目录

  ![1562406042744](C:\Users\黄自卫\AppData\Roaming\Typora\typora-user-images\1562406042744.png)

  

  app.py  运行

  factory.py 配置任务

  requirements.txt 所需要的包

  tasks.py 具体的任务

  content.html 前端展示

* factory.py配置定时任务

  ```python
  from flask_apscheduler import APScheduler
  from flask import Flask
  scheduler = APScheduler()
  
  
  def create_app():
      app = Flask(__name__)
      # 配置任务，不然无法启动
      app.config.update(
          {"SCHEDULER_API_ENABLED": True,
           "JOBS": [{"id": "my_job",  # 任务ID
                     "func": "tasks:task",  # 任务位置
                     "trigger": "interval",  # 触发器
                     "seconds": 600,  # 时间间隔
                     }
                    ]}
      )
      scheduler.init_app(app)
      scheduler.start()
      return app
      pass
  ```

  JOBS可以指定多个任务，，每个任务的trigger参数，他管理者任务的调度方式。他可以为

  ​		date：当你想再某个时间点之运行一次作业时使用

  ​		interval：当您想在固定的时间间隔内运行作业时使用

  ​		corn：当您希望在一天的特定时间定期运行作业时使用

* tasks.py 具体任务

  类MongoContext时用来管理数据库的连接和释放数据库的，

  方法task是具体的是的任务

  ```python
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
          self.client = pymongo.MongoClient('localhost', 27017)  # 连接本地数据库
          self.db = self.client.taobao_spider  # 指定数据库
          return self
          pass
  
      def insert_goods(self, good_dict):
          '''
          插入商品简介
          :return:
          '''
          self.db.goods.insert_one(good_dict)
          pass
  
      def insert_set(self, detail_id):
          '''
          判断商品是已经否存在，去重
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
  
      def __exit__(self, exc_type, exc_val, exc_tb):
          self.client.close()
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
  ```



​		
