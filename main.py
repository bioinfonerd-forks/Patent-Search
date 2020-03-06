# -*- coding:utf8 -*-
import time
from biz.glgoo import search_by_company, search_by_company_eachpage, search_report_detail
from biz.orm import initial_database, initial_table_company, Company, PatentBasic, ReportDetail
from biz.reload import load_company
from utils.common import ConfigUtil, DateUtil
from utils.log import getLogger
import datetime

# 读取配置文件
config = ConfigUtil()


def get_company_info():
    logger = getLogger()
    logger.info('method [get_company_info] start')
    company_list = Company.select()
    normal_interval = int(config.load_value('search', 'normal_interval', '5'))
    if len(company_list) == 0:
        logger.info('No company exists')
        return
    for company in company_list:
        logger.info('begin to process company {0}'.format(company.company_name))
        date_begin = config.load_value('search', 'date_begin', '20000101')
        current_page = 0
        date_end = datetime.datetime.now().strftime('%Y%m%d')
        total_num_pages, result_list, result_count = search_by_company(company.company_name, date_begin, date_end)
        company.patent_count = result_count
        company.update_datetime = datetime.datetime.now()
        company.save()
        time.sleep(normal_interval)


# 取得basic.csv所需信息
def get_basic_info():
    logger = getLogger()
    logger.info('method [get_basic_info] start')

    # 取得企业信息 专利数>0
    company_list = Company.select().where(Company.patent_count > 0, Company.finished == 0)
    if len(company_list) == 0:
        logger.info('No company exists')
        return
    normal_interval = int(config.load_value('search', 'normal_interval', '5'))
    search_company_page_interval = int(config.load_value('search', 'search_company_page_interval', '10'))
    search_company_date_interval = int(config.load_value('search', 'search_company_date_interval', '10'))
    search_to_date = config.load_value('search', 'search_to_date')
    if search_to_date:
        search_to_date = datetime.datetime.strptime(search_to_date, "%Y%m%d")
    else:
        search_to_date = datetime.datetime.now()
    # 按企业名称循环查询
    for company in company_list:
        logger.info('begin to process company {0}'.format(company.company_name))
        temp_day_interval = int(config.load_value('search', 'search_day_interval', '4'))
        date_begin = config.load_value('search', 'date_begin', '20000101')

        # 根据开始和截至日期循环查询
        while True:
            time.sleep(search_company_date_interval)
            # 根据总专利数 设定每次查询间隔月
            if company.patent_count < 300:
                date_end = datetime.datetime.now().strftime("%Y%m%d")
                total_num_pages, result_list, result_count = search_by_company(company.company_name, date_begin,
                                                                               date_end)
            else:
                while True:
                    # 获取截止日期
                    date_end = DateUtil.get_date_by_day(date_begin, temp_day_interval, search_to_date)
                    total_num_pages, result_list, result_count = search_by_company(company.company_name, date_begin,
                                                                                   date_end)
                    time.sleep(normal_interval)
                    if result_count >= 300:
                        temp_day_interval = temp_day_interval / 3
                        continue
                    else:
                        break

            current_page = 0

            logger.info('process company {0} , total_num_pages is {1}'.format(company.company_name, total_num_pages))
            # 查询结果不为空
            if len(result_list):
                set_basic_info(result_list, company)
                # 查询结果为多个页面
                while True:
                    if current_page < (total_num_pages - 1):
                        time.sleep(search_company_page_interval)
                        current_page = current_page + 1
                        result_list = search_by_company_eachpage(company.company_name, date_begin, date_end,
                                                                 current_page)
                        set_basic_info(result_list, company)
                    else:
                        break
            # 重置开始日期
            date_begin = DateUtil.get_next_day(date_end)
            if date_begin >= search_to_date:
                break
            date_begin = date_begin.strftime("%Y%m%d")
        # 更新company的flag
        company.finished = 1
        company.update_datetime = datetime.datetime.now()
        company.save()
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
            published=patent['publication_date'],
            finished=0
        )
    logger.info('method [set_basic_info] end')


# 取得detail.csv所需信息
def get_patent_detail():
    logger = getLogger()
    logger.info("method [get_patent_detail] start")
    normal_interval = int(config.load_value('search', 'normal_interval', '5'))

    patent_list = PatentBasic.select().where(PatentBasic.finished == 0)
    for basic_item in patent_list:
        detail_list = search_report_detail(basic_item)
        if len(detail_list):
            for detail_item in detail_list:
                insert_patent_detail(detail_item)
        basic_item.finished = 1
        basic_item.save()
        time.sleep(normal_interval)
    logger.info("method [get_patent_detail] end")


# 将detail信息插入数据库
def insert_patent_detail(detail_info):
    logger = getLogger()
    logger.info("method [get_patent_detail] start, patent is {0}".format(detail_info.publication_number))
    ReportDetail.create(
        publication_number=detail_info.publication_number,
        patent_citations_number=detail_info.patent_citations_number,
        cited_by_number=detail_info.cited_by_number,
        classifications=detail_info.classifications,
        claims=detail_info.claims,
        legal_events=detail_info.legal_events,

        patent_citations=detail_info.patent_citations,
        patent_citations_family=detail_info.patent_citations_family,
        cited_by=detail_info.cited_by,
        cited_by_family=detail_info.cited_by_family,

        ref_star=detail_info.ref_star,
        ref_priority_date=detail_info.ref_priority_date,
        ref_publication_date=detail_info.ref_publication_date,
        ref_assignee=detail_info.ref_assignee,
        ref_chinese=detail_info.ref_chinese,
        ref_patent_citations_number=detail_info.ref_patent_citations_number,
        ref_cited_by_number=detail_info.ref_cited_by_number,
        ref_classifications=detail_info.ref_classifications,
        ref_claims=detail_info.ref_claims

    )


if __name__ == '__main__':
    if config.load_value('system', 'init_database', 'False') == 'True':
        initial_database()
        initial_table_company()
    if config.load_value('system', 'load_company', 'False') == 'True':
        load_company('data/company.csv')
        get_company_info()

    get_basic_info()
    get_patent_detail()
