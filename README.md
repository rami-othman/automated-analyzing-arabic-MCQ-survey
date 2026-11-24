# Analytics of Arabic MCQ Surveys

Automated analytics pipeline for **Arabic multiple-choice surveys** collected with **KoboToolbox**, built for MEAL
(Monitoring, Evaluation, Accountability & Learning) teams. It is the analytics half of my graduation project (2025);
the other half is the [MEAL web app](https://github.com/rami-othman/meal-web-app).

Built with Eyas. I built the full analytics pipeline.

## What it does

1. **Collect**: a KoboToolbox client builds and uploads survey forms and pulls submissions (including repeat groups) through the Kobo API.
2. **Clean**: normalizes Arabic answers, handles multi-select answers and missing values, and maps each question to an indicator using a YAML rules file (`rules/`).
3. **Score**: turns answer scales into indicator scores and summarizes demographics.
4. **Analyze**: descriptive statistics, cross-tabs, association rules, respondent segments and recurring answer patterns, plus feature engineering for further modeling.
5. **Report**: generates a written MEAL report from the computed results with an LLM (Gemini), so field teams get findings in plain language instead of raw tables.

Each stage writes its results to `output/` (`clean_run`, `stats_run`, `assoc_run`, `segments_run`, `patterns_run`, `features_run`, `insight_run`, `reports`).

## Tech stack

Python · pandas · NumPy · scikit-learn · Featuretools · statsmodels · matplotlib / seaborn (with Arabic text shaping) · KoboToolbox API · Gemini API · Jupyter

## Repository layout

```
Kobo/                  KoboToolbox client, form builder and uploader
analyze_questionnaires.py   demographics and indicator scoring
rules/                 question-to-indicator mapping (YAML)
data/                  sample survey and answers
output/                results of each pipeline stage and generated reports
arabic_mcq_questionaries_analysis_cleaned.ipynb   end-to-end walkthrough
tests/                 client tests
```

## Run locally

```bash
pip install -r requirements.txt
# set KOBO_API_URL, KOBO_API_TOKEN and your Gemini key in a .env file
jupyter notebook arabic_mcq_questionaries_analysis_cleaned.ipynb
```
