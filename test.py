# -*- coding:utf8 -*-
from peewee import fn
from playhouse.shortcuts import model_to_dict, dict_to_model
from selenium import webdriver
import datetime, peewee, random, sys, time

# from biz.amazon import login, check_home_page, get_orders, check_refund, check_feedback, request_review, get_order_detail
# from biz.common import User, OrderInfo
# from biz.orm import Job, Order
# from biz.orm import initial_database
# from biz.reload import load_state_time
# from main import login_amazon, check_home_page, get_order_detail, process_order, process_job
# from utils.common import ClassUtil, ConfigUtil, DateUtil, TimeZoneUtil, TypeUtil
from utils.log import getLogger

'''
Usage:

python test.py
python test.py main
python test.py process_job
python test.py switch_proxy
python test.py search_click
python test.py timezone
'''


# 读取配置文件
config = ConfigUtil()


'''
ok
'''
def test_get_order_detail():

    logger = getLogger()
    logger.info('method [test_get_order_detail] start')

    user_name = config.load_value('user', 'email')
    user_password = config.load_value('user', 'password')
    user = User(user_name, user_password)
    request_review_time = config.load_work_time('review', 'request_review_time', '0830:1730')
    request_review_start = request_review_time[0]
    request_review_end = request_review_time[1]

    driver = webdriver.Chrome()        
    driver.implicitly_wait(2)

    try:
        login_result = login_amazon(driver, user)
        max_retry_times = 8
        current_retry_times = 1

        if login_result == 'failure':
            time.sleep(10)

        if login_result == 'otp':
            while current_retry_times < max_retry_times:
                current_retry_times += 1
                if check_home_page(driver):
                    login_result = 'success'
                    break
                else:
                    logger.info("sleep {0} seconds.".format(10*current_retry_times))
                    time.sleep(10*current_retry_times)

        logger.info("start get order info with detail")
        if login_result == 'success':
            order_info = OrderInfo()
            # rating
            order_info.order_id = '111-3087908-1283446'
            # refund
            order_info.order_id = '113-8986262-5581040'
            order_info = get_order_detail(driver, order_info)
            logger.info(order_info.order_id)
            logger.info(order_info.buyer_rating)
            logger.info(order_info.buyer_comment)
            logger.info(order_info.refund)
        
    except Exception as e:
        logger.info(e)
        raise e
    finally:
        driver.quit()

    logger.info('method [test_get_order_detail] end')


def test_amazon_request_review():

    logger = getLogger()
    logger.info('method [test_amazon_request_review] start')

    user_name = config.load_value('user', 'email')
    user_password = config.load_value('user', 'password')
    user = User(user_name, user_password)
    request_review_time = config.load_work_time('review', 'request_review_time', '0830:1730')
    request_review_start = request_review_time[0]
    request_review_end = request_review_time[1]

    driver = webdriver.Chrome()        
    driver.implicitly_wait(2)

    try:
        login_result = login_amazon(driver, user)
        max_retry_times = 8
        current_retry_times = 1

        if login_result == 'failure':
            time.sleep(10)

        if login_result == 'otp':
            while current_retry_times < max_retry_times:
                current_retry_times += 1
                if check_home_page(driver):
                    login_result = 'success'
                    break
                else:
                    logger.info("sleep {0} seconds.".format(10*current_retry_times))
                    time.sleep(10*current_retry_times)

        logger.info("start request review")
        if login_result == 'success':
            order_info = OrderInfo()
            # rating 5 stars
            order_info.order_id = '111-3087908-1283446'
            url = "https://sellercentral.amazon.com/orders-v3/order/{0}".format(order_info.order_id)
            driver.get(url)
            time.sleep(8)
            result = request_review(driver)
            logger.info(order_info.order_id)
            logger.info(result)
        
    except Exception as e:
        logger.info(e)
        raise e
    finally:
        driver.quit()

    logger.info('method [test_amazon_request_review] end')


'''
ok
'''
# def test_process_job():

#     logger = getLogger()
#     logger.info('method [test_process_job] start')
#     request_review_start = '0830'
#     request_review_end = '2300'
#     Job.truncate_table()
#     process_order()
#     process_job(request_review_start, request_review_end)
#     logger.info('method [test_process_job] end')

def test_process_job():

    logger = getLogger()
    logger.info('method [test_process_job] start')

    user_name = config.load_value('user', 'email')
    user_password = config.load_value('user', 'password')
    user = User(user_name, user_password)
    request_review_time = config.load_work_time('review', 'request_review_time', '0830:1730')
    request_review_start = request_review_time[0]
    request_review_end = request_review_time[1]

    for order in Order.select():
        # order.update_datetime = datetime.datetime.now() - datetime.timedelta(days=4)
        order.request_review_datetime = None
        order.requested_review = None
        order.save()
    for job in Job.select():
        job.process_datetime = datetime.datetime.now() - datetime.timedelta(days=4)
        job.processed_date = None
        job.processed_status = 'pending'
        job.save()

    driver = webdriver.Chrome()        
    driver.implicitly_wait(2)

    try:
        login_result = login_amazon(driver, user)
        max_retry_times = 20
        current_retry_times = 0

        if login_result == 'failure':
            time.sleep(10)

        if login_result == 'otp':
            while current_retry_times < max_retry_times:
                current_retry_times += 1
                if check_home_page(driver):
                    login_result = 'success'
                    break
                else:
                    logger.info("sleep {0} seconds.".format(10*current_retry_times))
                    time.sleep(10*current_retry_times)

        logger.info("start request review")
        if login_result == 'success':
            process_job(driver, request_review_start, request_review_end)

    except Exception as e:
        logger.info(e)
        raise e
    finally:
        driver.quit()

    logger.info('method [test_process_job] end')

'''
ok
'''
def test_search_click():

    search_click(None, 'pure water', 1, 2, 3, 4)


'''
ok
'''
def test_process_order():

    logger = getLogger()
    logger.info('method [test_process_order] start')
    Job.truncate_table()
    process_order()
    logger.info('method [test_process_order] end')


'''
ok
'''
def test_request_user_review():
    
    driver = webdriver.Chrome()        
    driver.implicitly_wait(2)

    try:
        request_user_review(driver)
    except Exception as e:
        logger.info(e)
        # raise e
    finally:
        driver.quit()


'''
ok
'''
def test_log():

    logger = getLogger()
    logger.info('I am a.py')
    # 日志输出
    logger.debug('debug message')
    logger.info('info message')
    logger.warning('warn message')
    logger.error('error message')
    logger.critical('critical message')


'''
ok
'''
def test_show():

    for order in Order.select():
        print(order.order_id, order.buyer_rating)


'''
python test.py config
'''
def test_config():

    config = ConfigUtil()
    result = config.load_value('order', 'day_after_shipped')
    print(result)
    result = config.load_value('order', 'day_after_shipped1', '3')
    print(result)
    result = config.load_value('order1', 'day_after_shipped')
    print(result)

    result = config.load_value('review', 'skip_request_review_action', 'True')
    print(TypeUtil.str_to_bool(result))
    print(result)


def test_timezone():

    result = DateUtil.get_now()
    print("local now datetime: {0}".format(result))

    result = DateUtil.get_now_for_tz()
    print("local now time: {0}".format(result))

    result = DateUtil.get_now_for_pts()
    print("PTS datetime: {0}".format(result))
    print("PTS datetime no_inzo: {0}".format(result.replace(tzinfo=None)))

    pts = DateUtil.get_now_for_pts()
    result = DateUtil.convert_datetime(pts, 'BJS')
    print("BJS datetime: {0}".format(result))
    print("BJS datetime no_inzo: {0}".format(result.replace(tzinfo=None)))


if __name__ == '__main__':
    test_log()

    # if config.load_value('system', 'init_database') == 'True':
    #     initial_database()
    #     load_state_time('data/State.Time.xlsx')
    #
    # if len(sys.argv) == 2:
    #     if sys.argv[1] == 'main':
    #         test_main()
    #     elif sys.argv[1] == 'process_order':
    #         test_process_order()
    #     elif sys.argv[1] == 'process_job':
    #         test_process_job()
    #     elif sys.argv[1] == 'search_click':
    #         test_search_click()
    #     elif sys.argv[1] == 'get_order_detail':
    #         test_get_order_detail()
    #     elif sys.argv[1] == 'amazon_request_review':
    #         test_amazon_request_review()
    #     # elif sys.argv[1] == 'main_request_user_review':
    #     #     test_main_request_user_review()
    #     elif sys.argv[1] == 'log':
    #         test_log()
    #     elif sys.argv[1] == 'show':
    #         test_show()
    #     elif sys.argv[1] == 'config':
    #         test_config()
    #     elif sys.argv[1] == 'timezone':
    #         test_timezone()
    #
    # else:
    #     pass

