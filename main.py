# -*- coding:utf8 -*-
import time
from biz.glgoo import search_by_company, search_by_company_eachpage, search_by_patent, search_by_patent_html
from biz.orm import initial_database, initial_table_company, Company, PatentBasic, PatentDetail, Citation
from biz.reload import load_company
from utils.common import ConfigUtil, DateUtil
from utils.log import getLogger

# 读取配置文件
config = ConfigUtil()


# 取得basic.csv所需信息
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


def set_citations(citations_of_list):
    logger = getLogger()
    logger.info("method [set_citations] start")
    for item in citations_of_list:
        Citation.create(
            # 专利号
            publication_number=item.publication_number,
            star=item.star,
            priority_date=item.priority_date,
            publication_date=item.publication_date,
            assignee=item.assignee,
            chinese=item.chinese,
            patent_citations_number=item.patent_citations_number,
            cited_by_number=item.cited_by_number,
            classifications=item.classifications,
            claims=item.claims
        )


# 取得detail.csv所需信息
def get_patent_detail():
    logger = getLogger()
    logger.info("method [get_patent_detail] start")

    patent_list = PatentBasic.select()
    for patent in patent_list:
        patent_info, citations_of_list, cited_by_list = search_by_patent_html(patent)
        set_patent_detail(patent_info)
        if len(citations_of_list):
            set_citations(citations_of_list)
        if len(cited_by_list):
            set_citations(cited_by_list)

    logger.info("method [get_patent_detail] end")


# 将detail信息插入数据库
def set_patent_detail(patent_info):
    logger = getLogger()
    logger.info("method [get_patent_detail] start, patent is {0}".format(patent_info.publication_number))
    PatentDetail.create(
        publication_number=patent_info.publication_number,
        patent_citations_number=patent_info.patent_citations_number,
        cited_by_number=patent_info.cited_by_number,
        classifications=patent_info.classifications,
        claims=patent_info.claims,
        legal_events=patent_info.legal_events
    )


if __name__ == '__main__':
    # if config.load_value('system', 'init_database', 'False') == 'True':
    #  initial_database()

    # initial_table_company()
    # load_company('data/company.csv')
    # get_basic_info()
    get_patent_detail()
