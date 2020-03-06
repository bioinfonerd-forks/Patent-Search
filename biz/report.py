from datetime import datetime

import pandas as pd
from biz.orm import PatentBasic, ReportDetail, Company
from utils.log import getLogger


# basic.csv
def export_basic():
    logger = getLogger()
    logger.info('method [export_basic] start')

    query = PatentBasic.select(PatentBasic.stckcd, PatentBasic.company, PatentBasic.publication_number,
                               PatentBasic.worldwide, PatentBasic.inventor, PatentBasic.company2,
                               PatentBasic.priority, PatentBasic.filed, PatentBasic.published, PatentBasic.finished)
    df = pd.DataFrame(
        columns=(
            'stckcd', 'company', 'publication_number', 'worldwide',
            'inventor', 'company2', 'priority', 'filed', 'published', 'finished'
        ))

    if len(query):
        for i, record in enumerate(query):
            df.loc[i, 'stckcd'] = record.stckcd
            df.loc[i, 'company'] = record.company
            df.loc[i, 'publication_number'] = record.publication_number
            df.loc[i, 'worldwide'] = record.worldwide
            df.loc[i, 'inventor'] = record.inventor
            df.loc[i, 'company2'] = record.company2
            df.loc[i, 'priority'] = record.priority
            df.loc[i, 'filed'] = record.filed
            df.loc[i, 'published'] = record.published
            df.loc[i, 'finished'] = record.finished
        dt = datetime.now()
        path = "output/basic"+dt.strftime('%Y%m%d%H%M%S') + ".csv"
        df.to_csv(path, encoding='utf_8_sig', index=False)

    logger.info('method [export_basic] end')


def export_detail():
    logger = getLogger()
    logger.info('method [export_detail] start')
    query = ReportDetail.select()
    df = pd.DataFrame(
        columns=(
            'publication-number',
            'Patent-citations-number',
            'Cited-by-Number',
            'Classifications',
            'Claims',
            'Patent-Citations',
            'Patent-Citations-Family',
            'Cited-By',
            'Cited-By-Family',
            'Ref-star',
            'Ref-Priority-date',
            'Ref-Publication-date',
            'Ref-Assignee',
            'Ref-chinese',
            'Ref-Patent-citations-number',
            'Ref-Cited-by-Number',
            'Ref-Classifications',
            'Ref-Claims',
            'Legal-Events'
        )
    )
    if len(query):
        for i, record in enumerate(query):
            df.loc[i, 'publication-number'] = record.publication_number
            df.loc[i, 'Patent-citations-number'] = record.patent_citations_number
            df.loc[i, 'Cited-by-Number'] = record.cited_by_number
            df.loc[i, 'Classifications'] = record.classifications
            df.loc[i, 'Claims'] = record.claims
            df.loc[i, 'Patent-Citations'] = record.patent_citations
            df.loc[i, 'Patent-Citations-Family'] = record.patent_citations_family
            df.loc[i, 'Cited-By'] = record.cited_by
            df.loc[i, 'Cited-By-Family'] = record.cited_by_family
            df.loc[i, 'Ref-star'] = record.ref_star
            df.loc[i, 'Ref-Priority-date'] = record.ref_priority_date
            df.loc[i, 'Ref-Publication-date'] = record.ref_publication_date
            df.loc[i, 'Ref-Assignee'] = record.ref_assignee
            df.loc[i, 'Ref-chinese'] = record.ref_chinese
            df.loc[i, 'Ref-Patent-citations-number'] = record.ref_patent_citations_number
            df.loc[i, 'Ref-Cited-by-Number'] = record.ref_cited_by_number
            df.loc[i, 'Ref-Classifications'] = record.ref_classifications
            df.loc[i, 'Ref-Claims'] = record.ref_claims

            df.loc[i, 'Legal-Events'] = record.legal_events
            dt = datetime.now()
            path = "output/detail"+dt.strftime('%Y%m%d%H%M%S') + ".csv"
        df.to_csv(path, encoding='utf_8_sig', index=False)

    logger.info('method [export_detail] end')


def export_company():
    logger = getLogger()
    logger.info('method [export_company] start')
    query = Company.select()
    df = pd.DataFrame(
        columns=(
            'stckcd', 'company_name', 'patent_count'
        ))

    if len(query):
        for i, record in enumerate(query):
            df.loc[i, 'stckcd'] = record.stckcd
            df.loc[i, 'company_name'] = record.company_name
            df.loc[i, 'patent_count'] = record.patent_count

        dt = datetime.now()
        path = "output/company"+dt.strftime('%Y%m%d%H%M%S') + ".csv"
        df.to_csv(path, encoding='utf_8_sig', index=False)

    logger.info('method [export_company] end')

if __name__ == '__main__':
    #export_company()
    export_basic()
    export_detail()
