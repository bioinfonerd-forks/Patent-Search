# -*- coding:utf8 -*-
import datetime, peewee, random, sys, time, tqdm, traceback

from biz.glgoo import search_by_company, search_by_company_eachpage
from biz.orm import initial_database, initial_table_company, Company
from biz.reload import load_company
from utils.common import ClassUtil, ConfigUtil, DateUtil, TypeUtil
from utils.log import getLogger

'''
Usage:

python main.py
'''


# 读取配置文件
config = ConfigUtil()


def get_basic_info():
    logger = getLogger()
    logger.info('method [get_basic_info] start')

    company_list = Company.select()
    if len(company_list):
        logger.info('No company exists')
        return

    for company in company_list:
        logger.info('begin to process company {0}'.format(company.company_name))
        current_page = 0
        total_num_pages, result_list = search_by_company(company.company_name)
        set_basic_info(result_list)
        while True:
            if current_page < (total_num_pages-1):
                current_page = current_page + 1
                result_list = search_by_company_eachpage(company.company_name, current_page)
                set_basic_info(result_list)
            else:
                logger.info('process company {0} end, wait 10 seconds to process next one'.format(company.company_name))
                time.sleep(10)
                break
    logger.info('method [get_basic_info] end')


def set_basic_info(result_list):
    count_total = len(result_list)
    count_current = 0
    while True:



# 登录Amazon，并把登录结果输出到log
def login_amazon(driver, user):

    logger = getLogger()
    logger.info('method [login_amazon] start')

    login_result = ''

    # 登录Amazon
    logger.info("user [{0}] try to login amazon.".format(user.email))
    login_result = login(driver, user.email, user.password)
    if login_result == 'failure':
        logger.info("user [{0}] login amazon failure.".format(user.email))
    elif login_result == 'success':
        logger.info("user [{0}] login amazon success.".format(user.email))
    elif login_result == 'otp':
        logger.info("user [{0}] login amazon success, but need input otp.".format(user.email))

    logger.info('method [login_amazon] end')

    return login_result


def create_order_record(order_info):
    order = Order.create(
        order_id=order_info.order_id,
        ship_date=order_info.ship_date,
        ship_address=order_info.ship_address,
        ship_state=order_info.ship_state,
        ship_region=order_info.ship_region,
        ship_zip_code=order_info.ship_zip_code,
        purchase_date=order_info.purchase_date,
        standard_time_zone=order_info.standard_time_zone,
        buyer_name=order_info.buyer_name,
        buyer_time_zone=order_info.buyer_time_zone,
        buyer_rating=order_info.buyer_rating,
        buyer_comment=order_info.buyer_comment,
        buyer_feedback=order_info.buyer_feedback
    )
    order_history = OrderHistory.create(
        order_id=order_info.order_id,
        ship_date=order_info.ship_date,
        ship_address=order_info.ship_address,
        ship_state=order_info.ship_state,
        ship_region=order_info.ship_region,
        ship_zip_code=order_info.ship_zip_code,
        purchase_date=order_info.purchase_date,
        standard_time_zone=order_info.standard_time_zone,
        buyer_name=order_info.buyer_name,
        buyer_time_zone=order_info.buyer_time_zone,
        buyer_rating=order_info.buyer_rating,
        buyer_comment=order_info.buyer_comment,
        buyer_feedback=order_info.buyer_feedback
    )
    return order


# 把符合条件的order插入到job表
def process_order():

    logger = getLogger()
    logger.info('method [process_order] start')

    # Job.truncate_table()
    shop_region = config.load_value('review', 'shop_region', 'US')

    day_after_shipped = int(config.load_value('order', 'day_after_shipped', '4'))

    # process all orders
    query = Order.select().where(
        (Order.refund == False) & (Order.buyer_feedback == True) & (Order.requested_review == False)
    )
    # logger.info("query result: {0}.".format(len(query)))

    if len(query) == 0:
        logger.info("no order need process")
        return

    for order in query:

        if order.ship_date == None:
            continue
        if order.ship_date < DateUtil.get_today_start_datetime(order.purchase_date):
            continue
        # logger.info("record info, id: {0}, ship_date: {1}".format(order.order_id, order.ship_date))
        now = DateUtil.get_now_for_pts(shop_region).replace(tzinfo=None)
        # logger.info("now pts: {0}".format(DateUtil.get_now_for_pts()))
        # logger.info("now no tz: {0}".format(DateUtil.get_now_for_pts().replace(tzinfo=None)))
        received_date = order.ship_date + datetime.timedelta(days=day_after_shipped)
        # ship_date = ship_date.replace(tzinfo=None)
        # logger.info("ship_date pts: {0}".format(ship_date))
        # logger.info("ship_date no tz: {0}".format(ship_date.replace(tzinfo=None)))
        # logger.info("datetime compare, now: {0}, ship_date: {1}".format(now, ship_date))
        if now > received_date:
            query = Job.select().where(Job.order==order.id)
            if len(query):
                pass
            else:
                Job.create(
                    order=order.id,
                    create_datetime=DateUtil.get_now_for_pts(shop_region).replace(tzinfo=None),
                    update_datetime=DateUtil.get_now_for_pts(shop_region).replace(tzinfo=None),
                    processed_status='pending',
                )

    logger.info('method [process_order] end')


def process_job(driver, request_review_start, request_review_end):

    logger = getLogger()
    logger.info('method [process_job] start')
    skip_request_review_action = config.load_value('review', 'skip_request_review_action', 'True')
    check_login_interval_default = int(config.load_value('review', 'check_login_interval', '100'))
    request_review_job_interval = int(config.load_value('review', 'request_review_job_interval', '30'))
    check_login_interval = 0
    request_review_by_customer_tz = config.load_value('review', 'request_review_by_customer_tz', 'False')
    shop_region = config.load_value('review', 'shop_region', 'EU')

    # process job
    query = Job.select().where(
        (Job.processed_status == 'pending') & \
        ((Job.process_datetime == None) | (Job.process_datetime < DateUtil.get_today_start_datetime(DateUtil.get_now_for_pts(shop_region).replace(tzinfo=None))))
    ).order_by(Job.process_datetime.asc())
    logger.info("all job count: {0}".format(len(query)))

    # process request review
    if len(query):
        for i, job in enumerate(tqdm.tqdm(query)):

            if check_login_interval == check_login_interval_default:
                user_name = config.load_value('user', 'email')
                user_password = config.load_value('user', 'password')
                user = User(user_name, user_password)
                login_result = login_amazon(driver, user)
                check_login_interval = 0
            else:
                check_login_interval += 1

            # index = random.randint(0, len(query) - 1)
            # logger.info("index: {0}".format(index))
            # job = query[index]
            if request_review_by_customer_tz == 'True':
                tz_full_info = DateUtil.get_tz_full_info(job.order.buyer_time_zone)
            else:
                tz_full_info = DateUtil.get_tz_full_info(shop_region)
            # 索评时间，根据request_review_by_customer_tz而取值不同
            tz_time = DateUtil.get_now_for_tz(tz=tz_full_info).strftime('%H%M')
            # tz_full_info = DateUtil.get_tz_full_info(job.order.buyer_time_zone)
            # tz_time = DateUtil.get_now_for_tz(tz=tz_full_info).strftime('%H%M')
            logger.info("pts time: {0}, tz_time: {1}".format(DateUtil.get_now_for_pts(shop_region).replace(tzinfo=None), DateUtil.get_now_for_tz(tz=tz_full_info)))
            logger.info("request_review_start: {0}, tz_time: {1}, request_review_end :{2}".format(request_review_start, tz_time, request_review_end))
            if request_review_start <= tz_time and tz_time <= request_review_end:
                logger.info("skip_request_review_action: {0}".format(skip_request_review_action))
                if skip_request_review_action == 'True':
                    request_result = 'test'
                else:
                    try:
                        request_result = request_review(driver, job.order.order_id)
                    except Exception as e:
                        request_result = 'exception'
                        logger.error(traceback.format_exc())
                logger.info("request_result: {0}".format(request_result))
                RequestReviewHistory.create(
                    order=job.order.id,
                    create_datetime=DateUtil.get_now_for_pts(shop_region).replace(tzinfo=None),
                    update_datetime=DateUtil.get_now_for_pts(shop_region).replace(tzinfo=None),
                    processed_status=request_result,
                )

                if request_result == 'not-eligible':
                    query = RequestReviewHistory.select().where(
                        (RequestReviewHistory.order == job.order.id) & (RequestReviewHistory.processed_status == 'not-eligible')
                    )
                    max_retry_times = int(config.load_value('review', 'max_retry_times', '0'))
                    if len(query) >= max_retry_times:
                        job.order.update_datetime = DateUtil.get_now_for_pts(shop_region).replace(tzinfo=None)
                        job.order.request_review_datetime = DateUtil.get_now_for_pts(shop_region).replace(tzinfo=None)
                        job.order.requested_review = True
                        job.order.save()
                        # job.process_datetime = None
                        job.processed_date = DateUtil.get_now_for_pts(shop_region).replace(tzinfo=None)
                        job.processed_status = 'expired'
                    job.process_datetime = DateUtil.get_now_for_pts(shop_region).replace(tzinfo=None) + datetime.timedelta(days=2)
                    job.save()
                elif request_result in ['completed', 'repeated']:
                    job.order.update_datetime = DateUtil.get_now_for_pts(shop_region).replace(tzinfo=None)
                    job.order.request_review_datetime = DateUtil.get_now_for_pts(shop_region).replace(tzinfo=None)
                    job.order.requested_review = True
                    job.order.save()
                    job.processed_date = DateUtil.get_now_for_pts(shop_region).replace(tzinfo=None)
                    job.processed_status = request_result
                    job.save()
                elif request_result == 'test':
                    job.order.update_datetime = DateUtil.get_now_for_pts(shop_region).replace(tzinfo=None)
                    job.order.request_review_datetime = DateUtil.get_now_for_pts(shop_region).replace(tzinfo=None)
                    job.order.requested_review = True
                    job.order.save()
                    job.processed_date = DateUtil.get_now_for_pts(shop_region).replace(tzinfo=None)
                    job.processed_status='test'
                    job.save()
            else:
                logger.info('wait for process next job.')
                time.sleep(request_review_job_interval)

    logger.info('method [process_job] end')


if __name__ == '__main__':

    if config.load_value('system', 'init_database', 'False') == 'True':
        initial_database()

    initial_table_company()
    load_company()




