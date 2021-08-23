# covid-risk-bayes
## Disclaimer
This project is simply intended as a proof of concept, and is neither peer-reviewed nor actively maintained (althogh development is ongoing). As such, users should not make decisions based on the model output.
## Introduction
An app to predict the probability that an individual has an active COVID infection based on current local conditions. An online version will be available shortly on the Streamlit hosting platform, pending account approval.

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

![Bayes theorem](./images/bayes-theorem.svg)

Using this statement, we can estimate the likelihood of an individual having an active COVID-19 infection (`I`), conditional on their vaccination status status (`V`), as:

![COVID Bayes](./images/covid-bayes.svg)

We can solve this equation relatively trivially using publically available data if we make a number of assumptions:

 - Both vaccinated and unvaccinated individuals have equal likelihood of exposure to an infectious level of SARS-COV-2 virus.
 - Both Both vaccinated and unvaccinated individuals are equally likely to get tested for COVID-19 infection.

`P(I)` is the local infection rate, and can be calculated from Johns HOpkins University COVID-19 data available [here](https://coronavirus.jhu.edu/about/how-to-use-our-data). This rate can be scaled by prior knowledge or belief regarding the proportion of true cases identified by testing. Currently, this factor is chosen by the user and incorporated into the model. Projects such as [covid19-projections.com](https://covid19-projections.com/estimating-true-infections-revisited/) have developed complex models addressing this issue, but [do not currently update their figures](https://youyanggu.com/blog/one-year-later).

`P(V)` is the local vaccination rate, and is more trivially calculated from the CCI vaccination dataset also linked from the [JHU COVID data page](https://coronavirus.jhu.edu/about/how-to-use-our-data). In this model, vaccination rate is assumed to be constant within countries outside of the US, and within States in the US.

`P(V|I)` can be deduced from a simple statement of the number of infections `NI` in a population `pop` given a fixed probability a potentially infectious exposure to COVID-19 `P(E)`, an estimated vaccing efficacy `eff`, and `P(V)`.

![NI1](./images/NI_1.svg) ,

![NI2](./images/NI_2.svg) , and

![NI3](./images/NI_3.svg) , 

therefore:

 ![NI](./images/NI.svg) .

Given that

![p_vi](./images/p_v_i.svg) ,

we find that 

![p_V_i_solved](./images/p_v_i_solved.svg)




