import os
import urllib
import xml.etree.ElementTree as ET

import pandas as pd

from serenata_toolbox.datasets.helpers import (
    save_to_csv,
    translate_column,
    xml_extract_datetime,
    xml_extract_text,
)


class SessionStartTimesDataset:
    URL = (
        'http://www.camara.leg.br/SitCamaraWS/sessoesreunioes.asmx/ListarPresencasDia'
        '?siglaPartido=&siglaUF='
        '&data={0}'
        '&numMatriculaParlamentar={1}'
    )

    def fetch(self, pivot, session_dates):
        """
        :param pivot: (int) a congressperson document to use as a pivot for scraping the data
        :param session_dates: (list) datetime objects to fetch the start times for
        """

        records = self.__all_start_times(pivot, session_dates)
        return pd.DataFrame(records, columns=(
            'date',
            'session',
            'started_at'
        ))

    def __all_start_times(self, pivot, session_dates):
        for date in session_dates:
            if os.environ.get('DEBUG') == '1':
                print(date.strftime("%d/%m/%Y"))
            file = urllib.request.urlopen(self.URL.format(date.strftime("%d/%m/%Y"), pivot))
            t = ET.ElementTree(file=file)
            for session in t.getroot().findall('.//sessaoDia'):
                yield (
                    date,
                    xml_extract_text(session, 'descricao'),
                    xml_extract_datetime(session, 'inicio')
                )


def fetch_session_start_times(data_dir, pivot, session_dates):
    """
    :param data_dir: (str) directory in which the output file will be saved
    :param pivot: (int) congressperson document to use as a pivot for scraping the data
    :param session_dates: (list) datetime objects to fetch the start times for
    """
    session_start_times = SessionStartTimesDataset()
    df = session_start_times.fetch(pivot, session_dates)
    save_to_csv(df, data_dir, "session-start-times")

    print("Dates requested:", len(session_dates))
    found = pd.to_datetime(df['date'], format="%Y-%m-%d %H:%M:%S").dt.date.unique()
    print("Dates found:", len(found))
    return df
