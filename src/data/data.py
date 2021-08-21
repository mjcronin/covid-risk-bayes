import os
import datetime as dt
from typing import List

import streamlit as st
import pandas as pd


def load(today: dt.date, data_dir: str='./data/') -> pd.DataFrame:
    """
    Load and concatenate the last 14 days of JHU COVID data.

    Args:
        today (dt.date)
    Returns:
        df (pd.DataFrame): DataFrame containing the last 14 days of JHU COVID 
            Incident_Rate and geographical info
    """
    last_14 = [(today-dt.timedelta(days=d)).strftime('%m-%d-%Y') for d in range(1,15)]

    raw_files = os.listdir(data_dir+'raw/')
    downloaded = [f[:-4] for f in raw_files if f[-4:]=='.csv']
    to_download = [f for f in last_14 if f not in downloaded]

    download_and_save(to_download, data_dir=data_dir)
    df = load_and_concat(last_14)

    return df

def download_and_save(to_download: List[str], data_dir: str='./data/') -> None:
    """Download last 14 daily CSVs from JHU COVID tracker if not stored locally
    
    Args:
        to_download (List[str]): dates to download in format '%m-%d-%Y'
        data_dir (str): root directory for app data
    Returns:
        None
    """
    # Download any data from the last 14 days that is not stored locally
    if len(to_download) > 0:
        for d in to_download:
            url = (
                'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master'
                '/csse_covid_19_data/csse_covid_19_daily_reports/{}.csv'.format(d)
            )
            pd.read_csv(url).to_csv(data_dir+'raw/{}.csv'.format(d))

    return None


def load_and_concat(last_14: List[str], data_dir: str='./data/') -> pd.DataFrame:
    """Load and concatenate last 14 days of JHU COVID CSV data
    
    Args:
        last_14 (list): Last 14 dates in format '%m-%d-%Y'
    Returns:
        df (pd.DataFrame): DataFrame containing the last 14 days of JHU COVID 
            Incident_Rate and geographical info 
    """
    kwargs = {
        'usecols': [
            'FIPS',
            'Admin2',
            'Province_State',
            'Country_Region',
            'Last_Update',
            'Incident_Rate'
            ]
    }
    frames = [
        pd.read_csv(data_dir+'raw/{}.csv'.format(date), **kwargs) for date in last_14
    ]
    df = pd.concat(frames).reset_index(drop=True)

    return df