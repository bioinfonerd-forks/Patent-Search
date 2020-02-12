# -*- coding:utf8 -*-
import time

from bs4 import BeautifulSoup
import requests
from biz.common import PatentDetailInfo
from biz.orm import Citation
from utils.common import ConfigUtil, StringUtil
from utils.log import getLogger
from fake_useragent import UserAgent

# 读取配置文件
config = ConfigUtil()


# 按企业名称查询，取得url
def get_search_company_url(company, date_begin, date_end, page):
    logger = getLogger()
    logger.info("method [get_search_company_url] start")

    url_format = config.load_value('search', 'search_by_company', '')
    # 参数：企业名称 结束日期 开始日期 页数（从0开始）
    url = url_format.format(company, date_end, date_begin, page)

    logger.info("method [get_search_company_url] end")
    return url


# 按patent的publication_number查询，取得url
def get_search_patent_url(publication_number):
    logger = getLogger()
    logger.info("method [get_search_patent_url] start")

    url_format = config.load_value('search', 'search_by_patent', '')
    # 参数：专利号
    url = url_format.format(publication_number, publication_number)

    logger.info("method [get_search_patent_url] end")
    return url


# 取得随机user agent
def get_random_user_agent():
    #ua = UserAgent()
    #user_agent_random = ua.random
    user_agent_random = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
    return user_agent_random


# 按企业名称查询，返回结果为总页数及第一页内容
def search_by_company(company, date_begin, date_end):
    logger = getLogger()
    logger.info("method [search_by_company] start, company is {0}, date_begin is {1}, date_end is {2}".format(
        company, date_begin, date_end))

    url = get_search_company_url(company, date_begin, date_end, 0)
    logger.info(url)
    # 随机user agent
    user_agent_random = get_random_user_agent()

    if url:
        result = requests.get(
            url=url,
            headers={'Content-Type': 'application/json',
                     'user-agent': user_agent_random
                     }
        )
        result_json = result.json()
        result_total = result_json['results']
        result_count = result_total['total_num_results']
        logger.info('result_count is {0}'.format(result_count))
        # 页数
        total_num_pages = result_total['total_num_pages']
        result_cluster = result_total['cluster'][0]
        # 具体结果，内部结构为字典
        result_list = {}
        if len(result_cluster):
            result_list = result_cluster['result']

    logger.info("method [search_by_company] end, company is {0}, date_begin is {1}, date_end is {2}".format(
        company, date_begin, date_end))

    return total_num_pages, result_list


# 按企业名称查询，返回每一页的结果信息（从第二页开始）
def search_by_company_eachpage(company, date_begin, date_end, page):
    logger = getLogger()
    logger.info(
        "method [search_by_company_eachpage] start, company is {0}, date_begin is {1}, date_end is {2},current page is {3}".format(
            company, date_begin, date_end, page))

    url = get_search_company_url(company, date_begin, date_end, page)

    # 随机user agent
    user_agent_random = get_random_user_agent()

    if url:
        result = requests.get(
            url=url,
            headers={'Content-Type': 'application/json',
                     'user-agent': user_agent_random
                     }
        )
        result_json = result.json()
        result_total = result_json['results']
        result_cluster = result_total['cluster'][0]
        # 具体结果，内部结构为字典
        result_list = result_cluster['result']

    logger.info(
        "method [search_by_company_eachpage] end, company is {0}, date_begin is {1}, date_end is {2},current page is {3}".format(
            company, date_begin, date_end, page))

    return result_list


# 按patent的publication_number查询
def search_by_patent(patent):
    logger = getLogger()
    logger.info("method [search_by_patent] start, patent is {0}".format(patent))
    # 对应PatentDetail的实例
    patent_info = PatentDetailInfo()
    # 被patent引用的专利
    citations_of_list = []
    # 引用patent的专利
    cited_by_list = []
    patent_info.publication_number = patent.publication_number
    url = get_search_patent_url(patent.publication_number)
    # 随机user agent
    user_agent_random = get_random_user_agent()

    if url:
        result = requests.get(
            url=url,
            headers={'Content-Type': 'application/json',
                     'user-agent': user_agent_random
                     }
        )
        result_json = result.json()
        # Classifications
        classification_list = get_classifications(result_json)
        classifications = ' '.join(classification_list)
        patent_info.classifications = classifications
        # ToDo 获得detail.csv中其他字段信息

    return patent_info, citations_of_list, cited_by_list


# 按patent的publication_number查询 按照html
def search_by_patent_html(patent):
    logger = getLogger()
    logger.info("method [search_by_patent_html] start, patent is {0}".format(patent))
    # 对应PatentDetail的实例
    patent_info = PatentDetailInfo()
    # 被patent引用的专利
    citations_of_list = []
    # 引用patent的专利
    cited_by_list = []
    patent_info.publication_number = patent.publication_number
    url = get_search_patent_url(patent.publication_number)
    # 随机user agent
    user_agent_random = get_random_user_agent()

    if url:
        try:
            result = requests.get(
                url=url,
                headers={'Content-Type': 'test/html',
                         'user-agent': user_agent_random
                         }
            )
        except BaseException:
            print
            "Error: 服务器拒绝1次"
            time.sleep(10)
            user_agent_random = get_random_user_agent()
            result = requests.get(
                url=url,
                headers={'Content-Type': 'test/html',
                         'user-agent': user_agent_random
                         }
            )

    # 寻找citations 和 cite
    soup = BeautifulSoup(result.content, 'lxml')

    citations_items = soup.find_all(attrs={"itemprop": "backwardReferencesFamily"})
    cited_items = soup.find_all(attrs={"itemprop": "forwardReferencesOrig"})
    legal_events_items = soup.find_all(attrs={"itemprop": "legalEvents"})
    legal_events_text = ""
    if legal_events_items:
        # 多行legal_events拼为一个字符串
        for item in legal_events_items:
            legal_events_text += item.text.replace("\n", "|") + ";"
    # print("patent.publication_number={0}, legal_events={1}".format(patent.publication_number, legal_events_text))
    patent_info.legal_events = legal_events_text

    if citations_items:
        for item in citations_items:
            print(item.text)
            citation = Citation(patent)
            set_citation(citation, item, user_agent_random)
            # 加入list
            citations_of_list.append(citation)

    if cited_items:
        for item in cited_items:
            print(item.text)
            cite = Citation(patent)
            set_citation(cite, item, user_agent_random)
            cited_by_list.append(cite)

    return patent_info, citations_of_list, cited_by_list


# 设定专利信息
def set_citation(citation, item, user_agent_random):
    # 取得引用专利
    citation.publication_number = item.find(attrs={"itemprop": "publicationNumber"}).text

    # 星号
    star_tag = item.find(attrs={"itemprop": "examinerCited"})
    if star_tag:
        citation.star = star_tag.text
    # 优先日期
    citation.priority_date = item.find(attrs={"itemprop": "priorityDate"}).text
    # 公布日期
    citation.publication_date = item.find(attrs={"itemprop": "publicationDate"}).text
    # 代理人
    citation.assignee = item.find(attrs={"itemprop": "assigneeOriginal"}).text
    # 是否中文
    if StringUtil.check_chinese(citation.assignee):
        citation.chinese = 1
    else:
        citation.chinese = 0
    # 再次查询引用
    url_child = get_search_patent_url(citation.patent_citations_number)
    result_child = requests.get(
        url=url_child,
        headers={'Content-Type': 'test/html',
                 'user-agent': user_agent_random
                 })
    soup_child = BeautifulSoup(result_child.content, 'lxml')
    child_citations_items = soup_child.find_all(attrs={"itemprop": "backwardReferencesFamily"})
    citation.patent_citations_number = len(child_citations_items)
    child_cited_items = soup_child.find_all(attrs={"itemprop": "forwardReferencesOrig"})
    citation.cited_by_number = len(child_cited_items)
    claims_items = soup_child.find(attrs={"itemprop": "claims"})
    if claims_items:
        claims_count = claims_items.find(attrs={"itemprop": "count"})
        if claims_count:
            citation.claims = claims_count
    # Classifications
    clfc_ui_items = soup_child.find_all("ul", attrs={"itemprop": "cpcs"})
    clfc_text = "";
    if clfc_ui_items:
        for item in clfc_ui_items:
            # 最后一个<span itemprop="Code">
            span_tags = item.find_all("span", attrs={"itemprop": "Code"})
            span_cnt = len(span_tags)
            clfc_text += span_tags[span_cnt - 1].text
    citation.classifications = clfc_text

# 取得Classifications-Citations
def get_classifications(result_json):
    classification_list = []
    soup = BeautifulSoup(result_json, 'lxml')
    first_ul = soup.find(attrs={'itemprop': 'cpcs'})
    if len(first_ul):
        parent_ul = first_ul.parent.parent
        for li in parent_ul.children:
            classification = ''
            if len(li) > 1:
                all_li = li.findAll('li')
                for li_child in all_li:
                    classification = li_child.find('span').text
                classification_list.append(classification)

    return classification_list


if __name__ == '__main__':
    pass
