from typing import Optional

import numpy as np
import pandas as pd
import streamlit as st

from src.data import data
from src.model import covid_bayes


def write(
    df: pd.DataFrame,
    vacc_data: pd.DataFrame,
    country: str,
    region: str,
    sub_region: str
) -> None:
    st.title('COVID-19 infeciton likelihood estimation')
    model_control = st.container()

    with model_control:
        cols = st.columns(3)
        
        with cols[1]:
            identification_rate = st.slider(
                'Infection detection rate (%)', min_value=1, max_value=100, value=100
            )
            identification_rate /= 100 # Rescale from % to decimal
        with cols[2]:
            vaccine_efficacy = st.slider(
                'Estimated vaccine efficacy (%)', min_value=1, max_value=100, value=65
            )
            vaccine_efficacy /= 100 # Rescale from % to decimal
    run_model(
        df,
        vacc_data,
        country,
        region=region,
        sub_region=sub_region,
        identification_rate=identification_rate,
        vaccine_efficacy=vaccine_efficacy
    )
    return None


def run_model(
    df: pd.DataFrame,
    vacc_data: pd.DataFrame,
    country: str='US',
    region: Optional[str]=None,
    sub_region: Optional[str]=None,
    infectious_duration: int=10,
    identification_rate: float=1.0,
    vaccine_efficacy: float = 0.65
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
    loc_inputs = (country, region, sub_region)
    subset = data.subset_data(df, *loc_inputs)
    infectious_rate = get_model_inputs(
            subset, vacc_data, infectious_duration, *loc_inputs
    )
    vaccination_rate = calc_vacc_rate(df, vacc_data, country, region, sub_region)

    loc_inputs = [n for n in [country, region, sub_region] if n]
    locs = [loc for loc in loc_inputs if loc!='All']
    location = ', '.join(locs)

    if subset.shape[0] != 14:
        st.write(
            """## Unexpected data! \n \n There appears to be an unexpected number of
             entries in the subset of data requested. Rather than deliver questionable
            results, this app has been programmed to deliver this excessively verbose
            and uninformative error message. \n \nApologies for the inconvenience!"""
        )
    else:

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
        ### Based on:\n * A local vaccination rate of **{vacc_rate}%** \n- An estimated vaccine efficacy of **{vacc_eff}%** against COVID-19 infection\n - A rate of **{inf_rate}** infections per 100,000 people in the local population.\n - A projected "true" rate of **{inf_rate_scaled}** infections per 100,000 people in the local population.""".format(
            vacc_rate = np.round(100*vaccination_rate, 2),
            vacc_eff = 100*vaccine_efficacy,
            inf_rate = np.round(1e5*infectious_rate, 2),
            inf_rate_scaled = np.round(1e5*infectious_rate/identification_rate, 2)
            )
        )
    
    return None


def get_model_inputs(
    subset: pd.DataFrame,
    vacc_data: pd.DataFrame,
    infectious_duration: int,
    country: str,
    region: str,
    sub_region: str
) -> tuple:
    """Extract model inputs from data

    Args:
        subset (pd.DataFrame): Location-specific subset of JHU COVID data for last 14 
            days 
        vacc_data (pd.DataFrame): Latest merged CCI vaccination dataset
        infectious_duration (int): Number of days following +ve test that individuals 
            are assumed to remain infectious
        country (str): Selected country
        region (str): Selected state/region
        sub_region (str): Selected county/sub_region

    Returns:
        tuple: [description]
    """
    # Subset-derived inputs
    pop = subset.population.iloc[-1]
    infectious_cases = subset.new_cases[-infectious_duration:].sum()
    infectious_rate = infectious_cases / pop
    # Vaccination-related inputs

    if country != 'US':
        filter = (vacc_data.Country_Region==country) & (vacc_data.Province_State.isna())
    elif country=='US':
        filter = (vacc_data.Country_Region==country)
        if region != 'All':
            filter = (filter) & (vacc_data.Province_State==region)

    return (infectious_rate)


def calc_vacc_rate(
    df,
    vacc_data,
    country,
    region,
    sub_region
):
    if country != 'US':
        filter = (vacc_data.Country_Region==country) & (vacc_data.Province_State.isna())

    elif country=='US':
        filter = (vacc_data.Country_Region==country)
        if region != 'All':
            filter = (filter) & (vacc_data.Province_State==region)
    
    vacc_count = vacc_data.loc[filter, 'People_Fully_Vaccinated'].max()
    pop = get_pop(df, country, region=region)
    vaccination_rate = vacc_count/pop

    return vaccination_rate


def get_pop(df: pd.DataFrame, country: str, region: Optional[str]=None):
    """Return subset population at granularity of available vaccination data"""
    c1 = country=='US'
    c2 = region != None
    c3 = region != 'All'

    if all([c1, c2, c3]):
        pop_agg = df.groupby(
                by=['date', 'Country_Region', 'Province_State'], as_index=False
            ).agg({'population': sum})
        pop_agg = pop_agg.loc[
            (pop_agg.Country_Region==country) & (pop_agg.Province_State==region)
        ]
    
    c4 = country != 'US'
    c5 = all([country=='US', any([not region, region=='All'])])
    
    if any([c4, c5]) :
        pop_agg = df.groupby(
            by=['date', 'Country_Region'], as_index=False
        ).agg({'population': sum})
        pop_agg = pop_agg.loc[pop_agg.Country_Region==country]

    pop=np.round(pop_agg.population.max())

    return pop