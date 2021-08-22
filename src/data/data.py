import os
import datetime as dt
from typing import List, Tuple, Optional, Dict

import pandas as pd
import numpy as np


def load_cases(today: dt.date, data_dir: str='./data/') -> pd.DataFrame:
    """
    Load last 15 days of JHU COVID data.

    Args:
        today (dt.date)
    Returns:
        df (pd.DataFrame): DataFrame containing the last 15 days of JHU COVID 
            Incident_Rate and geographical info
    """
    # Additional day is downloaded to allow calc. of 14 days of new case counts
    last_15 = [(today-dt.timedelta(days=d)).strftime('%m-%d-%Y') for d in range(1,16)]

    raw_files = os.listdir(data_dir+'raw/')
    downloaded = [f[:-4] for f in raw_files if f[-4:]=='.csv']
    to_download = [f for f in last_15 if f not in downloaded]

    # Download data from remote repositories
    download_and_save_JHU(to_download, data_dir=data_dir)
    download_and_save_CCI(data_dir)

    df = load_and_concat(last_15, data_dir=data_dir, today=today)

    return df


def load_vaccinations(
    today: dt.date, data_dir: str='./data/'
) -> Dict[str, pd.DataFrame]:
    """
    Load last 15 days of CCI COVID vaccinationdata.

    Args:
        today (dt.date)
    Returns:
        df (Dict[str, pd.DataFrame]): DataFrame containing the last 15 days of CCI
            COVID vaccination data for 'US' and 'Global'
    """


def download_and_save_JHU(to_download: List[str], data_dir: str='./data/') -> None:
    """Download last 15* daily CSVs from JHU COVID tracker if not stored locally
    
    \* 15 days are pulled to allow a diff() operation to calculate new cases over the 
    last 14 days

    Args:
        to_download (List[str]): dates to download in format '%m-%d-%Y'
        data_dir (str): root directory for app data
    Returns:
        None
    """
    # Download any data from the last 15 days that is not stored locally
    if len(to_download) > 0:
        for d in to_download:
            url = (
                'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master'
                '/csse_covid_19_data/csse_covid_19_daily_reports/{}.csv'.format(d)
            )
            pd.read_csv(url).to_csv(data_dir+'raw/{}.csv'.format(d))

    return None


def download_and_save_CCI(data_dir: str='./data/raw/') -> None:
    """Download the latest US and Global vaccination data from the CCI repo and save"""
    data_dir += 'raw/vaccinations/'
    url_us = (
        'https://raw.githubusercontent.com/govex/COVID-19/master/data_tables'
        '/vaccine_data/us_data/hourly/vaccine_people_vaccinated_US.csv'
    )
    url_global = (
        'https://raw.githubusercontent.com/govex/COVID-19/master/data_tables'
        '/vaccine_data/global_data/time_series_covid19_vaccine_global.csv'
    )
    pd.read_csv(url_us).to_csv(data_dir+'vaccinations_us.csv')
    pd.read_csv(url_us).to_csv(data_dir+'vaccinations_global.csv')

    return None


def load_and_concat(
    last_15: List[str], data_dir: str='./data/', today: dt.date=None
) -> pd.DataFrame:
    """Load and concatenate last 15 days of JHU COVID CSV data
    
    Args:
        last_15 (list): Last 15 days' dates in format '%m-%d-%Y'
        data_dir (str): root directory for app data
        today (dt.date): Today's date as a dt.date
    Returns:
        df (pd.DataFrame): DataFrame containing the last 15 days of JHU COVID 
            Incident_Rate and geographical info 
    """
    kwargs = {
        'usecols': [
            'Admin2',
            'Province_State',
            'Country_Region',
            'Last_Update',
            'Incident_Rate',
            'Confirmed'
            ]
    }
    frames = [
        pd.read_csv(data_dir+'raw/{}.csv'.format(date), **kwargs) for date in last_15
    ]
    # Do a little feature engineering
    df = pd.concat(frames).reset_index(drop=True)
    strptime_JHU = lambda x: dt.datetime.strptime(x, '%Y-%m-%d %H:%M:%S').date()

    df['date'] = [strptime_JHU(d) for d in df.Last_Update]
    df = df.sort_values(by='date').drop('Last_Update', axis=1)

    df['population'] = (
        df.Confirmed.div(df.Incident_Rate).mul(1e5).astype(int, errors='ignore')
    )
    
    # Additional date filter
    df = df.loc[df.date >= (today - dt.timedelta(days=15))]

    return df


def get_regions(df: pd.DataFrame) -> Tuple[List[str]]:
    """Return lists of countries, states, and sub-regions from df"""
    country_set = set(df.Country_Region)
    country_set.remove('US')
    country_set.remove('United Kingdom')
    
    countries = ['US', 'United Kingdom'] + sorted(list(country_set))

    return countries


def subset_data(
    df: pd.DataFrame,
    country: str,
    region: Optional[str]=None,
    sub_region: Optional[str]=None
):
    """Return data subset of interest
    
    Args:
        df (pd.DataFrame): Last 15 days' JHU COVID data
        country (str): Country of interest
        region (str): Region of interest
        sub_region (str): Sub-region of interest
    Returns:
        subset(pd.DataFrame)
    """
    filter = (df.Country_Region==country)
    
    if all([region, region!='All']):
        filter = (filter) & (df.Province_State==region)
    
    if all([sub_region, sub_region!='All']):
        filter = (filter) & (df.Admin2==sub_region)

    subset = df.loc[filter, :].reset_index(drop=True).dropna(axis=1, how='all').copy()

    if region != 'All':
        by=['date', 'Country_Region', 'Province_State']
    elif sub_region != 'All':
        by=['date', 'Country_Region', 'Province_State']
    else:
        by=['date', 'Country_Region'
        ]
    try:
        subset = (
            subset.groupby(
                by=by, as_index=False
            ).agg({'Confirmed': sum, 'population': sum})
        )
        subset['Incident_Rate'] = subset.Confirmed.mul(1e5).div(subset.population)
         # Diff to calulate new cases count
        subset['new_cases'] = subset.Confirmed.diff()
        subset['rolling_7'] = subset.new_cases.rolling(7).mean()
        subset = subset.iloc[1:].reset_index(drop=True)
    except:
        subset = None

    return subset