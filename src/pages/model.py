from typing import Optional

import numpy as np
import pandas as pd
import streamlit as st

from src.data import data
from src.model import covid_bayes


def write(df: pd.DataFrame, country: str, region: str, sub_region: str) -> None:
    st.title('COVID-19 infeciton likelihood estimation')
    model_control = st.container()

    with model_control:
        cols = st.columns(3)
        
        with cols[1]:
            identification_rate = st.slider(
                'Infection detection rate (%)', min_value=1, max_value=100, value=100
            )
            identification_rate /= 100 # Rescale from % to decimal
    run_model(
        df,
        country,
        region=region,
        sub_region=sub_region,
        identification_rate=identification_rate,
    )
    return None


def run_model(
    df,
    country: str='US',
    region: Optional[str]=None,
    sub_region: Optional[str]=None,
    infectious_duration: int=10,
    identification_rate: float=1.0
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
    locs = [loc for loc in [sub_region, region, country] if loc!='All']
    location = ', '.join(locs)

    if subset.shape[0] != 14:
        st.write(
            """## Unexpected data! \n \n There appears to be an unexpected number of
             entries in the subset of data requested. Rather than deliver questionable
            results, this app has been programmed to deliver this excessively verbose
            and uninformative error message. \n \nApologies for the inconvenience!"""
        )
    else:
        pop = subset.population.iloc[-1]
        infectious_cases = subset.new_cases[-infectious_duration:].sum()
        infectious_rate = infectious_cases / pop
        st.write('USING PLACEHOLDER VACCINATION RATE = 0.4 AND VACCINE EFFICACY = 0.65')
        vaccination_rate = 0.4
        vaccine_efficacy = 0.65

        risk = covid_bayes.predict_risk(
            infectious_rate,
            vaccination_rate,
            vaccine_efficacy,
            identification_rate=identification_rate
        )

        st.write("""### The model estmates that in {loc}: \n \n * ### A vaccinatied individual has a **{v_prob}%** probability of active COVID-19 infection\n * ### An unvaccinatied individual has a **{uv_prob}%** probability of active COVID-19 infection
        """.format(
            loc=location,
            v_prob = np.round(100*risk['vaccinated'], 2),
            uv_prob = np.round(100*risk['unvaccinated'], 2)
            )
        )
        st.write("""
        ### Based on:\n * A local vaccination rate of **{vacc_rate}%** \n- An estimated vaccine efficacy of **{vacc_eff}%** against COVID-19 infection\n - A rate of **{inf_rate}** infections per 100,000 people in the local population.""".format(
            vacc_rate = 100*vaccination_rate,
            vacc_eff = 100*vaccine_efficacy,
            inf_rate = np.round(1e5*infectious_rate, 2)
            )
        )
    
    return None


# def write_results(infectious_rate, risk)