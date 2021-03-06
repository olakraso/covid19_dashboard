from functools import reduce, partial

import dateparser
import numpy as np
import pandas as pd

# How many columns in the time series data, before the time series columns begin.
_TIMESERIES_FIXED_COLS = 4

_URL_PREFIX = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/'
_SERIES = {
    'Confirmed':
        _URL_PREFIX+'time_series_19-covid-Confirmed.csv',
    'Deaths':
        _URL_PREFIX+'time_series_19-covid-Deaths.csv',
    'Recovered':
        _URL_PREFIX+'time_series_19-covid-Recovered.csv'
}


def _get_category_df(value_name, url):
    df = pd.read_csv(url)
    dates = pd.Series([np.datetime64(dateparser.parse(s)) for s in df.columns[_TIMESERIES_FIXED_COLS:]])
    dates = pd.Series(dates).dt.normalize().drop_duplicates(keep='last')
    df2 = pd.melt(df, id_vars=df.columns[:_TIMESERIES_FIXED_COLS],
                  value_vars=df.columns[_TIMESERIES_FIXED_COLS + dates.index],
                  var_name='Date', value_name=value_name)

    df2.dropna(subset=[value_name], inplace=True)

    df2['Date'] = df2['Date'].apply(lambda x: dateparser.parse(x).strftime('%Y-%m-%d'))

    columns = list(df2.columns)
    df2.columns = columns

    return df2


def get_cases_as_df():
    """
    Retrieves the Confirmed, Deaths and Recovered time series from the csv files provided by JHU CSSE on GitHub. Joins
    the information into a single dataframe.

    :return: dataframe, each row describes the situation per country/province and day.
    """
    worksheets = [_get_category_df(value_name, url) for (value_name, url) in _SERIES.items()]
    df = reduce(partial(pd.merge, how='outer', on=list(worksheets[0].columns[:(_TIMESERIES_FIXED_COLS + 1)])),
                worksheets)
    df['Epidemy'] = 'Corona'
    return df
