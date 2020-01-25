# -*- coding:utf8 -*-
from peewee import MySQLDatabase, SqliteDatabase
from peewee import Model
from peewee import BooleanField, CharField, DateTimeField, ForeignKeyField, IntegerField, PrimaryKeyField
from playhouse.migrate import SqliteMigrator, migrate
import datetime

from utils.common import ConfigUtil
from utils.orm import BaseModel, TimeZone, database, Region
from utils.log import getLogger


# 读取配置文件
config = ConfigUtil()


'''
用户信息
email不可修改
'''
class Order(BaseModel):

    id = PrimaryKeyField()
    # 邮箱地址
    order_id = CharField(null=False, unique=True, index=True)
    order_date = DateTimeField(null=True)
    buyer_name = CharField(null=True)
    purchase_date = DateTimeField(null=True)
    standard_time_zone = CharField(null=True, default='PST')
    buyer_time_zone = CharField(null=True)
    customer_option = CharField(null=True)
    ship_address = CharField(null=True)
    ship_state = CharField(null=True, default='US')
    ship_region = CharField(null=True)
    ship_city = CharField(null=True)
    ship_date = DateTimeField(null=True)
    ship_service = CharField(null=True)
    ship_zip_code = CharField(null=True)
    sales_channel = CharField(null=True)
    latest_request_review_status = CharField(null=True)
    latest_request_review_datetime = DateTimeField(null=True)
    buyer_rating = IntegerField(null=True, default=0)
    buyer_comment = CharField(null=True)
    buyer_feedback = BooleanField(null=True, default=True)
    requested_review = BooleanField(null=True, default=False)
    request_review_datetime = DateTimeField(null=True)
    refund = BooleanField(null=True, default=False)

    stckcd
    company
    publication-number
    worldwide
    inventor
    company2
    priority
    filed
    published

    class Meta:
        order_by = ('id',)
        db_table = 'order'





def initial_database():

    logger = getLogger('')
    logger.info('method [initial_database] start')

    database.drop_tables(
        [
            Job,
            RequestReviewHistory,
            Order,
            OrderHistory,
            TimeZone,
            BlackOrderId,
            Region,
        ]
    )
    database.create_tables(
        [
            Job,
            RequestReviewHistory,
            Order,
            OrderHistory,
            TimeZone,
            BlackOrderId,
            Region,
        ]
    )

    logger.info('method [initial_database] end')


def initial_table_blackorderid():

    logger = getLogger('')
    logger.info('method [initial_table_blackorderid] start')

    BlackOrderId.truncate_table()

    logger.info('method [initial_table_blackorderid] end')


def initial_test_data():

    pass


if __name__ == '__main__':

    initial_database()



