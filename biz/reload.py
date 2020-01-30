# -*- coding:utf8 -*-
import os, pandas
from biz.orm import initial_database, Company
from utils.log import getLogger


'''
读取企业信息
'''
def load_company(file_path):

    logger = getLogger()
    logger.info('method [load_company] start.')

    if os.path.exists(file_path) and os.path.isfile(file_path):

        # company_info = pandas.read_csv(file_path, header=0, encoding='gbk')
        company_info = pandas.read_csv(file_path, header=0)
        logger.info("input file [{0}], shape [{1}]".format(file_path, company_info.shape))

        for index, row in company_info.iterrows():

            stckcd = row['stckcd']
            company_name = row['company']

            Company.create(
                stckcd=stckcd,
                company_name=company_name,
            )
    else:
        logger.info("input file [{0}] not exists.".format(file_path))

    logger.info('method [load_company] end')


if __name__ == '__main__':

    initial_database()
    load_company('data/company.csv')

