
import os
import datetime as dt
from typing import List, Tuple

import streamlit as st
import yaml
import pandas as pd

from src.pages import home, model, disclaimer, about
from src.data import data


with open('./config.yaml', 'r') as f:
    _CONFIG: dict = yaml.safe_load(f)

_PAGES = {
    'Home': home,
    'Model': model,
    'About': about,
    'Disclaimer': disclaimer
}


def main():
    st.write('Proof of concept - see Disclaimer page')

    with st.spinner(text='Loading data...'):
        df, vacc_data, countries = load_data(dt.date.today(), _CONFIG['data_dir'])
    # Write sidebar and return user inputs
    page, country, state, sub_region = write_sidebar(df, countries)
    # Write main page content
    args = {
        'Home': [],
        'Model': [df, vacc_data, country, state, sub_region],
        'About': [],
        'Disclaimer': []
    }
    _PAGES[page].write(*args[page])

    return None


@st.cache
def load_data(today: dt.date, data_dir: str='./data/') -> pd.DataFrame:
    """Load latest COVID data from JHU Github repo

    Args:
        today (dt.date): Todays's date
    Returns:
        df (pd.DataFrame): Last 14 days of daily covid incidence per 100k population by
            geography.
    """
    df = data.load_cases(today, data_dir)
    countries = data.get_regions(df)

    vacc_data = data.load_vaccinations(data_dir=data_dir)
    
    return df, vacc_data, countries


def write_sidebar(df: pd.DataFrame, countries: List[str]) -> Tuple[str]:
    """Populate app sidebar and return user inputs
    
    Args:
        df (pd.DataFrame): Last 14 days' JHU COVID data
        Countries (List[str]): List of unique countries in df.Country_Region
    Returns:
        page (str): Selected page
        country (str): Selected country
        region (str): Selected state/region
        sub_region (str): Selecetd county/sub-region
    """
    sidebar_navigation = st.sidebar.container()
    sidebar_settings = st.sidebar.container()
    sidebar_info = st.sidebar.container()

    with sidebar_navigation:
        st.title('Navigation')
        page = st.radio("Go to", list(_PAGES.keys()))

    with sidebar_settings:
        if page == 'Model':
            country = st.selectbox('Country', countries)

            if country == 'US':
                state_label = 'State'
                county_label = 'County'
            else:
                state_label = 'Province/State'
                county_label = 'Sub-region'

            regions = get_regions(df, country)
            
            if valid_regions(regions):
                state = st.selectbox(state_label, regions)
                sub_regions = get_subregions(df, country, state)
            else:
                state = None
                sub_regions = []

            if valid_regions(sub_regions):
                sub_region = st.selectbox(county_label, sub_regions)
            else:
                sub_region = None

            
        else:
            country = None
            state = None
            sub_region = None

    with sidebar_info:
        st.info(
            """App developed by Matthew Cronin.\n\nQuestions/comments? Please email matthew.j.cronin@gmail.com
            """)

    return (page, country, state, sub_region)


def get_regions(df: pd.DataFrame, country: str):
    """Return unique values of df.Province_State where df.Country_Region==country"""
    regions = ['All'] + sorted(
        list(
            set(
                df.loc[
                    df.Country_Region==country, 'Province_State'
                    ].fillna('Not Reported')
            )
        )
    )
    
    
    return regions


def get_subregions(df: pd.DataFrame, country: str, region: str):
    """
    Return unique values of df.Admin2 where df.Province_State==region and 
    df.Country_Region==country
    """
    sub_regions = ['All'] + sorted(
        list(
            set(
                df.loc[
                    (df.Country_Region==country) & (df.Province_State==region),
                    'Admin2'
                ].fillna('Not Reported')
            )
        )
    )

    return sub_regions


def valid_regions(regions: List[str]) -> bool:
    """Return True if regions contains valid options"""
    cond1 = all([len(regions)==1, regions[0] != 'Not Reported'])
    cond2 = len(regions) > 1
    
    return any([cond1, cond2])


if __name__ == '__main__':
    main()