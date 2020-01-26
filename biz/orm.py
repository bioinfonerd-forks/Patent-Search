# -*- coding:utf8 -*-
from peewee import BooleanField, CharField, DateTimeField, ForeignKeyField, IntegerField, PrimaryKeyField
from utils.orm import BaseModel, database
from utils.log import getLogger


# 读取配置文件
# config = ConfigUtil()


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
专利详细信息
'''
class PatentDetail(BaseModel):

    # 主键，默认自增
    id = PrimaryKeyField()
    publication_number = ForeignKeyField(PatentBasic, to_field='publication_number', null=False)
    patent_citations_number = IntegerField(null=True)
    cited_by_number = IntegerField(null=True)
    classifications = CharField(null=True)
    claims = CharField(null=True)
    legal_events = CharField(null=True)

    class Meta:
        order_by = ('id',)
        db_table = 'patent_detail'


'''
引用及被引用的专利信息
'''
class Citation(BaseModel):

    # 主键，默认自增
    id = PrimaryKeyField()
    # 专利号
    publication_number = CharField(null=False)
    star = CharField(null=True)
    priority_date = CharField(null=True)
    publication_date = CharField(null=True)
    assignee = CharField(null=True)
    chinese = BooleanField(null=False, default=False)
    patent_citations_number = IntegerField(null=True)
    cited_by_number = IntegerField(null=True)
    classifications = CharField(null=True)
    claims = CharField(null=True)
    # 引用PatentDetail中的记录的专利号，对应输出文件detail中的Cited-By字段
    citations_of = ForeignKeyField(PatentDetail, to_field='publication_number', null=True)
    # 被PatentDetail中的记录引用的专利号，对应输出文件detail中的Patent-Citations字段
    cited_by = ForeignKeyField(PatentDetail, to_field='publication_number', null=True)

    class Meta:
        order_by = ('id',)
        db_table = 'citation'


def initial_database():

    logger = getLogger()
    logger.info('method [initial_database] start')

    database.drop_tables(
        [
            Company,
            PatentBasic,
            PatentDetail,
            Citation,
        ]
    )
    database.create_tables(
        [
            Company,
            PatentBasic,
            PatentDetail,
            Citation,
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



