# -*- coding:utf8 -*-
from peewee import BooleanField, CharField, ForeignKeyField, IntegerField, PrimaryKeyField
from utils.orm import BaseModel, database
from utils.log import getLogger

'''
企业信息，内容从文件中读取
'''


class Company(BaseModel):
    id = PrimaryKeyField()
    # 公司代码
    stckcd = CharField(null=True)
    # 公司名称
    company_name = CharField(null=False)
    # 专利数
    patent_count = IntegerField(null=True)
    # 完成flag。 0：没完成， 1：已完成
    finished = IntegerField(null=True)

    class Meta:
        order_by = ('id',)
        db_table = 'company'


'''
专利基本信息
'''


class PatentBasic(BaseModel):
    # 主键，默认自增
    id = PrimaryKeyField()
    stckcd = CharField(null=False)
    company = CharField(null=False)
    publication_number = CharField(null=False, index=True)
    worldwide = CharField(null=True)
    inventor = CharField(null=True)
    company2 = CharField(null=True)
    priority = CharField(null=True)
    filed = CharField(null=True)
    published = CharField(null=True)
    # 完成flag。 0：没完成， 1：已完成
    finished = IntegerField(null=True)

    class Meta:
        order_by = ('id',)
        db_table = 'patent_basic'


'''
引用及被引用的专利信息
'''


# 符合CSV格式的detail
class ReportDetail(BaseModel):
    # 主键，默认自增
    id = PrimaryKeyField()
    publication_number = CharField(null=False)
    patent_citations_number = IntegerField(null=True)
    cited_by_number = IntegerField(null=True)
    classifications = CharField(null=True)
    claims = CharField(null=True)
    legal_events = CharField(null=True)

    # 引用或被引用的ID，只会有一个不为空
    patent_citations = CharField(null=True)
    patent_citations_family = CharField(null=True)
    cited_by = CharField(null=True)
    cited_by_family = CharField(null=True)
    # 引用或被引用的专利信息
    ref_star = CharField(null=True)
    ref_priority_date = CharField(null=True)
    ref_publication_date = CharField(null=True)
    ref_assignee = CharField(null=True)
    ref_chinese = CharField(null=True)
    ref_patent_citations_number = IntegerField(null=True)
    ref_cited_by_number = IntegerField(null=True)
    ref_classifications = CharField(null=True)
    ref_claims = CharField(null=True)

    class Meta:
        order_by = ('id',)
        db_table = 'report_detail'


def initial_database():
    logger = getLogger()
    logger.info('method [initial_database] start')

    database.drop_tables(
        [
            Company,
            PatentBasic,
            ReportDetail
        ]
    )
    database.create_tables(
        [
            Company,
            PatentBasic,
            ReportDetail
        ]
    )

    logger.info('method [initial_database] end')


def initial_table_company():
    logger = getLogger('')
    logger.info('method [initial_table_company] start')

    Company.truncate_table()

    logger.info('method [initial_table_company] end')


def initial_test_data():
    pass


if __name__ == '__main__':
    initial_database()
