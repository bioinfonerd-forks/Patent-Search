# -*- coding:utf8 -*-
import datetime, peewee, random, sys, time, tqdm, traceback

from biz.common import PatentDetailInfo
from biz.glgoo import search_by_company, search_by_company_eachpage, search_by_patent
from biz.orm import initial_database, initial_table_company, Company, PatentBasic
from biz.reload import load_company
from utils.common import ConfigUtil, DateUtil, TypeUtil
from utils.log import getLogger


# 读取配置文件
config = ConfigUtil()


def get_basic_info():
    logger = getLogger()
    logger.info('method [get_basic_info] start')

    # 取得企业信息
    company_list = Company.select()
    if len(company_list) == 0:
        logger.info('No company exists')
        return
    search_company_page_interval = int(config.load_value('search', 'search_company_page_interval', '10'))
    search_company_date_interval = int(config.load_value('search', 'search_company_date_interval', '10'))
    search_month_interval = int(config.load_value('search', 'search_month_interval', '4'))
    # 按企业名称循环查询
    for company in company_list:
        logger.info('begin to process company {0}'.format(company.company_name))
        date_begin = config.load_value('search', 'date_begin', '20000101')

        # 根据开始和截至日期循环查询
        while True:
            time.sleep(search_company_date_interval)
            # 获取截止日期
            date_end = DateUtil.get_date(date_begin, search_month_interval)
            if date_end == '':
                logger.info('process company {0} end, wait 5 seconds to process next one'.format(company.company_name))
                time.sleep(5)
                break
            current_page = 0
            total_num_pages, result_list = search_by_company(company.company_name, date_begin, date_end)
            logger.info('process company {0} , total_num_pages is {1}'.format(company.company_name, total_num_pages))
            # 查询结果不为空
            if len(result_list):
                set_basic_info(result_list, company)
                # 查询结果为多个页面
                while True:
                    if current_page < (total_num_pages-1):
                        time.sleep(search_company_page_interval)
                        current_page = current_page + 1
                        result_list = search_by_company_eachpage(company.company_name, date_begin, date_end, current_page)
                        set_basic_info(result_list, company)
                    else:
                        break
            # 重置开始日期
            date_begin = DateUtil.get_next_day(date_end)
    logger.info('method [get_basic_info] end')


# 将basic信息插入数据库
def set_basic_info(result_list, company):
    logger = getLogger()
    logger.info('method [set_basic_info] start')

    for result in result_list:
        patent = result['patent']

        publication_number = patent['publication_number']
        query = PatentBasic.select().where(PatentBasic.publication_number == publication_number)
        if len(query):
            continue
        # company2 格式：深圳市<b>中兴通讯股份有限公司</b>
        company2 = patent['assignee'].replace('<b>', '')
        company2 = company2.replace('</b>', '')

        # 取得country_status信息，对应表中的worldwide字段
        family_metadata = patent['family_metadata']
        aggregated = family_metadata['aggregated']
        worldwide = ''
        if len(aggregated):
            country_status = aggregated['country_status']
            worldwide_list = []
            for worldwide in country_status:
                worldwide_list.append(worldwide['country_code'])
            worldwide = ' '.join(worldwide_list)

        priority = ''
        if 'priority_date' in patent:
            priority = patent['priority_date']
        PatentBasic.create(
            stckcd=company.stckcd,
            company=company.company_name,
            publication_number=publication_number,
            worldwide=worldwide,
            inventor=patent['inventor'],
            company2=company2,
            priority=priority,
            filed=patent['filing_date'],
            published=patent['publication_date']
        )
    logger.info('method [set_basic_info] end')


def get_patent_detail():
    logger = getLogger()
    logger.info("method [get_patent_detail] start")

    patent_list = PatentBasic.select()
    for patent in patent_list:
        result = search_by_patent(patent)

        set_patent_detail(result)

    logger.info("method [get_patent_detail] end")


def set_patent_detail(result):
    logger = getLogger()
    logger.info("method [get_patent_detail] start, patent is {0}".format(result.publication_number))


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
    load_company('data/company.csv')
    get_basic_info()






