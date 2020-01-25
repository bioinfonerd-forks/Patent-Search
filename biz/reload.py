# -*- coding:utf8 -*-
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from playhouse.shortcuts import model_to_dict, dict_to_model
import logging, os, pandas

from biz.orm import Job, Order
from biz.orm import initial_database, BlackOrderId
from utils.common import ConfigUtil
from utils.orm import Region, TimeZone
from utils.log import getLogger


# 读取配置文件
config = ConfigUtil()


'''
读取各地区时区信息
'''
def load_region_utc(file_path):

    logger = getLogger()
    logger.info('method [load_region_utc] start.')

    if os.path.exists(file_path) and os.path.isfile(file_path):

        df_state_time = pandas.read_excel(file_path, sheet_name=0, header=0)
        logger.info("input file [{0}], shape [{1}]".format(file_path, df_state_time.shape))

        for index, row in df_state_time.iterrows():

            state = row['state'].upper()
            abbreviation = row['abbreviation'].upper()
            standard_time = row['standard_time'].upper()
            utc = row['utc'].upper()
            usage = str(row['usage']).upper()

            if len(state):
                Region.create(
                    state=state,
                    abbreviation=abbreviation,
                    standard_time=standard_time,
                    utc=utc,
                    usage=usage,
                )
    else:
        logger.info("input file [{0}] not exists.".format(file_path))

    logger.info('method [load_region_utc] end')


'''
读取各时区代表城市
'''
def load_time_zone(file_path):

    logger = getLogger()
    logger.info('method [load_time_zone] start.')

    if os.path.exists(file_path) and os.path.isfile(file_path):

        df_state_time = pandas.read_excel(file_path, sheet_name=0, header=0)
        logger.info("input file [{0}], shape [{1}]".format(file_path, df_state_time.shape))

        for index, row in df_state_time.iterrows():

            utc = row['utc'].upper()
            city = row['city'].upper()

            TimeZone.create(
                utc=utc,
                city=city,
            )
    else:
        logger.info("input file [{0}] not exists.".format(file_path))

    logger.info('method [load_time_zone] end')


'''
读取已索评过的order_id信息
'''
def load_black_order_id(file_path):

    logger = getLogger()
    logger.info('method [load_black_order_id] start.')

    if os.path.exists(file_path) and os.path.isfile(file_path):

        df_state_time = pandas.read_excel(file_path, sheet_name=0, header=0)
        logger.info("input file [{0}], shape [{1}]".format(file_path, df_state_time.shape))

        for index, row in df_state_time.iterrows():

            black_order_id = row['blackorderid'].upper()

            if len(black_order_id):
                BlackOrderId.create(
                    order_id=black_order_id,
                )
    else:
        logger.info("input file [{0}] not exists.".format(file_path))

    logger.info('method [load_black_order_id] end')


if __name__ == '__main__':

    initial_database()
    load_state_time('data/State.Time.xlsx')

