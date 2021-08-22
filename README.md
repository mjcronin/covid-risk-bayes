# covid-risk-bayes
## Disclaimer
This project is simply intended as a proof of concept, and is neither peer-reviewed nor actively maintained (althogh development is ongoing). As such, users should not use
## Introduction
An app to predict the probability that an individual has an active COVID infection based on current local conditions.

To run from command line (`bash` or `zsh`):
- Create virtual environment (reccommended):

    `pip install venv`

    `python -m venv venv-covid`
    
    `source venv-covid/bin/activate`
- Install requirements:

    `pip install -r requirements.txt`
- Launch via Streamlit:

    `streamlit run app.py`

## Motivation
In the early days of the COVID-19 pandemic, the prevailing philosophy of precautionary advice and regulations was to absolutely minimize the risk of exposure to the SARS-COV-2 virus. This necessitated the cessation of all non-essential activities and minimization of contact or association with those outside of a person's household. The ultimate goal was to "flatten the curve" and starve outbreaks by bringing the reproduction number (R) under 1.0 and eventually eliminating the virus; or at least to mitigate the spread of the virus until a successful vaccine candidate could be identified and deployed to end the pandemic.

Unfortunately, with a small number of exceptions (e.g. New Zealand), this strategy has been unsuccessful, and no longer appears to be politically, socially, or economically practical. Combinined with the emergence of highly contagious new varients (e.g. Delta), individuals and households are left to balance their personal risk tolerance against a confusing web of risk factors.

One such factor that likely affects the daily activity of many individuals is the current risk that any other individual is actively infected with COVID. Before the general availability of vaccines, this factor might be estimated simply from the current local infection rate. At present (August 2021), however, this risk is additonally dependant on an individual's vaccination status, vaccine efficacy against the dominant varient(s), and local vaccination rate.

Here, we deploy a Bayesian statistical model to provide an estimation of the probability of active COVID infection in an individual based on vaccination status, estimated vaccine efficacy, and local pandemic conditions.

## Theory
Bayes' theorem states that:

![Bayes theorem](./images/bayes_theorem.png)

A
