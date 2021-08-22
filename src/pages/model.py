from typing import Optional

import pandas as pd
import streamlit as st

from src.data import data
from src.model import covid_bayes


def write(df: pd.DataFrame, country: str, region: str, sub_region: str) -> None:
    st.title('COVID-19 infeciton likelihood estimation')

    run_model(df, country, region=region, sub_region=sub_region)
    return None


def run_model(
    df,
    country: str='US',
    region: Optional[str]=None,
    sub_region: Optional[str]=None,
    infectious_duration: int=10,
):
    """
    Args:
        df (pd.DataFrame): Last 14 days' JHU COVID data
        country (str): Country of interest
        region (str): Region of interest
        sub_region (str): Sub-region of interest
        infectious_duration (int): Number of days following +ve test that individuals 
            are assumed to remain infectious
    """

    subset = data.subset_data(df, country, region, sub_region)

    if subset.shape[0] != 14:
        st.write(
            """## Unexpected data! \n \n There appears to be an unexpected number of
             entries in the subset of data requested. Rather than deliver questionable
            results, this app has been programmed to deliver this excessively verbose
            and uninformative error message. \n \nApologies for the inconvenience!"""
        )
    else:
        st.write(subset.loc[-10:,'Confirmed'].sum())
        infectious_cases = subset.new_cases[-infectious_duration:].sum()
        infectious_rate = infectious_cases / subset.population[-1]
        st.write('USING PLACEHOLDER VACCINATION RATE = 0.4 AND VACCINE EFFICACY = 0.65')
        vaccination_rate = 0.4
        vaccine_efficacy = 0.65

        risk = covid_bayes.predict_risk(
            infectious_rate,
            vaccination_rate,
            vaccine_efficacy
        )
        pass
    
    st.write(subset)
    return None