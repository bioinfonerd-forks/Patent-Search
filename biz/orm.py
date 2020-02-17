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

    # 引用专利
    patent_citations = CharField(null=False)
    star = CharField(null=True)
    priority_date = CharField(null=True)
    publication_date = CharField(null=True)
    assignee = CharField(null=True)
    chinese = BooleanField(null=False, default=False)
    patent_citations_number_ci = IntegerField(null=True)
    cited_by_number_ci = IntegerField(null=True)
    classifications_ci = CharField(null=True)
    claims_ci = CharField(null=True)

    # 被引用专利
    patent_citations_by = CharField(null=False)
    star_by = CharField(null=True)
    priority_date_by = CharField(null=True)
    publication_date_by = CharField(null=True)
    assignee_by = CharField(null=True)
    chinese_by = BooleanField(null=False, default=False)
    patent_citations_number_by = IntegerField(null=True)
    cited_by_number_by = IntegerField(null=True)
    classifications_by = CharField(null=True)
    claims_by = CharField(null=True)

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
