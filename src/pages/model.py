import pandas as pd
import streamlit as st

from src.model import covid_bayes


def write(df: pd.DataFrame) -> None:
    st.title('COVID-19 infeciton likelihood estimation')
    return None
