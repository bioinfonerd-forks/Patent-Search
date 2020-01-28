import pandas as pd
from biz.orm import PatentBasic
from utils.log import getLogger

# basic.csv
def export_basic():

    logger = getLogger()
    logger.info('method [export_basic] start')

    query = PatentBasic.select(PatentBasic.stckcd, PatentBasic.company, PatentBasic.publication_number,
                               PatentBasic.worldwide, PatentBasic.inventor,  PatentBasic.company2,
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


if __name__ == '__main__':

    export_basic()

