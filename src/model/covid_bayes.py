from typing import Optional

import numpy as np


def predict_risk(
    incident_rate: float,
    vaccination_rate: float,
    vaccine_efficacy: float,
    identification_rate: Optional[float]=None
):
    """Return probabilities of current infection in vaccinated and unvaccinated individuals
    
    Given Bayes' Theorem that P(A|B) = P(B|A) P(A) / P(B):
    
    For vaccinated individuals (V), the probability of current COVID infection (I) is
    
    P(I|V) = P(V|I) P(I) / P(V)
    
    where 
    
    P(V) is the current local vaccination rate
    P(I) is the current local infection rate
    P(V|I) is related to vaccine efficacy against prevalent variants by
        P(V|I) = (1 - vaccine_efficacy)/(1 + (1 - vaccine_efficacy))
    
    For unvaccinated individuals (¬V), the probability of current COVID infection (I) is
    
    P(I|¬V) = P(¬V|I) P(I) / P(¬V)
    
    where P(¬V|I) = 1 - P(V|I)
    
    Assumptions include:
        - Equal risk of virus exposure to vaccinated and unvaccianted individuals
    
    Args:
        incident_rate (float): Local rate of  active infection (per 100,000 pop)
        vaccination_rate (float): Local vaccination rate (0.0-1.0)
        vaccine_efficacy (float): Proportion of potential infections blocked by vaccine (0.0-1.0)
        identification_rate (Optional[float]): Proportion of true infection count represented in data.
            If None, infection_rate assumed to be accurate.
    Returns:
        risk (dict): Current risk of infection in vaccinated and unvaccinated individuals
    """
    risk = {}

    # Scale from per 100,000 to 0.0 -s 1.0 range
    infection_rate = incident_rate / 1e5

    if identification_rate:
        infection_rate /= identification_rate # Adjust infeciton rate to account for missed diagnoses
    
    p_v = vaccination_rate # P(V)
    p_nv = 1 - vaccination_rate # P(¬V)
    p_i = infection_rate # P(I)
    p_vi = (p_v*(1 - vaccine_efficacy)) / ((p_v*(1 - vaccine_efficacy)) + p_nv) # P(V|I)
    p_nv_i = p_nv / ((p_v*(1 - vaccine_efficacy)) + p_nv) # P(¬V|I)
    
    risk['vaccinated'] = np.round(p_vi * p_i / p_v, 3)
    risk['unvaccinated'] = np.round(p_nv_i * p_i / p_nv, 3)
    risk['p_vi'] = p_vi
    risk['p_nv_i'] = p_nv_i
    
    return risk