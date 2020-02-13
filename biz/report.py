import pandas as pd
from biz.orm import PatentBasic, PatentDetail, Citation
from utils.log import getLogger


# basic.csv
def export_basic():
    logger = getLogger()
    logger.info('method [export_basic] start')

    query = PatentBasic.select(PatentBasic.stckcd, PatentBasic.company, PatentBasic.publication_number,
                               PatentBasic.worldwide, PatentBasic.inventor, PatentBasic.company2,
                               PatentBasic.priority, PatentBasic.filed, PatentBasic.published)
    df = pd.DataFrame(
        columns=(
            'stckcd', 'company', 'publication_number', 'worldwide',
            'inventor', 'company2', 'priority', 'filed', 'published',
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

        path = "output/basic.csv"
        df.to_csv(path, encoding='utf_8_sig', index=False)

    logger.info('method [export_basic] end')


def export_detail():
    logger = getLogger()
    logger.info('method [export_detail] start')
    query = PatentDetail.select(PatentDetail).left_outer_join(Citation,
                                                              PatentDetail.publication_number == Citation.publication_number)
    df = pd.DataFrame(
        columns=(
            'publication-number', 'Patent-citations-number',
            'Cited-by-Number', 'Classifications',
            'Claims', 'Patent-Citations',
            'star', 'Priority-date',
            'Publication-date', 'Assignee',
            'chinese', 'Patent-citations-number-Citations',
            'Cited-by-Number-Citations', 'Classifications-Citations',
            'Claims-Citations', 'Cited-By',
            'star-by', 'Priority-date-by',
            'Publication-date-by', 'Assignee-by',
            'chinese-by', 'Patent-citations-number-by',
            'Cited-by-Number-by', 'Classifications-by',
            'Claims-by', 'Legal-Events'
        )
    )
    if len(query):
        for i, record in enumerate(query):
            df.loc[i, 'publication_number'] = record.publication_number
            df.loc[i, 'patent_citations_number'] = record.patent_citations_number
            df.loc[i, 'cited_by_number'] = record.cited_by_number
            df.loc[i, 'classifications'] = record.classifications
            df.loc[i, 'claims'] = record.claims
            df.loc[i, 'legal_events'] = record.legal_events
            df.loc[i, 'publication-number'] = record.publication_number
            df.loc[i, 'Patent-citations-number'] = record.patent_citations_number
            df.loc[i, 'Cited-by-Number'] = record.cited_by_number
            df.loc[i, 'Classifications'] = record.classifications
            df.loc[i, 'Claims'] = record.claims
            df.loc[i, 'Patent-Citations'] = record.Citation.publication_number
            df.loc[i, 'star'] = record.Citation.star
            df.loc[i, 'Priority-date'] = record.Citation.priority_date
            df.loc[i, 'Publication-date'] = record.Citation.publication_date
            df.loc[i, 'Assignee'] = record.Citation.assignee
            df.loc[i, 'chinese'] = record.Citation.chinese
            df.loc[i, 'Patent-citations-number-Citations'] = record.Citation.patent_citations_number
            df.loc[i, 'Cited-by-Number-Citations'] = record.Citation.patent_citations_number
            df.loc[i, 'Classifications-Citations'] = record.Citation.classifications
            df.loc[i, 'Claims-Citations'] = record.Citation.claims
            df.loc[i, 'Cited-By'] = record.Citation.cited_by
            df.loc[i, 'star-by'] = record.Citation.star
            df.loc[i, 'Priority-date-by'] = record.Citation.priority_date
            df.loc[i, 'Publication-date-by'] = record.Citation.publication_date
            df.loc[i, 'Assignee-by'] = record.Citation.assignee
            df.loc[i, 'chinese-by'] = record.Citation.chinese
            df.loc[i, 'Patent-citations-number-by'] = record.Citation.patent_citations_number
            df.loc[i, 'Cited-by-Number-by'] = record.Citation.cited_by_number
            df.loc[i, 'Classifications-by'] = record.Citation.classifications
            df.loc[i, 'Claims-by'] = record.Citation.claims
            df.loc[i, 'Legal-Events'] = record.legal_events

            path = "output/detail.csv"
        df.to_csv(path, encoding='utf_8_sig', index=False)

    logger.info('method [export_basic] end')


if __name__ == '__main__':
    export_basic()
    export_detail()
