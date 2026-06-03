# NBA-Predictions
Look into upcoming NBA match-ups and see what the data says. Not gambling advice.
# 🏀 Automated End-to-End NBA Prediction Pipeline

An automated data engineering and predictive machine learning pipeline that simulates conference-aligned NBA regular seasons and utilizes gradient-boosted decision trees (XGBoost) to predict daily game outcomes. 

The entire architecture is self-sustaining, self-correcting, and executes daily in the cloud via a scheduled headless workflow infrastructure.

## 🚀 System Architecture

The pipeline is split into three decoupled, modular layers to adhere to production-grade software engineering principles:

1. **The Synthetic Sports Engine (`pipeline/data_fetcher.py`):** An advanced domain-specific simulator that generates mathematically sound basketball tracking matrices. Rather than using raw statistical noise, it splits teams into factually accurate NBA conferences, utilizes dynamic seasonal performance shocks, incorporates a +2.5 baseline home-court advantage, and decouples performance weights into offensive efficiency, defensive efficiency, and pace vectors.
2. **The Feature & Modeling Layer (`pipeline/feature_engineering.py`):** Calculates rolling performance averages across 5-game windows. It applies a strict 1-game chronology shift to prevent future-data leakage before flattening individual team vectors into a unified matchup matrix. Models are trained using chronological time-series splits rather than random distributions.
3. **The Deployment/Automation Orchestrator (`main.py` & GitHub Actions):** A scheduled cloud runner triggers every afternoon at 20:00 UTC, initializes the environment, executes the end-to-end pipeline, serializes the trained model (`nba_model.pkl`), and securely commits a live-rendered prediction dashboard (`predictions_today.md`) directly back to the repository.

## 🛠️ Tech Stack & Core Tools
* **Language:** Python 3.10+
* **Machine Learning:** XGBoost (Classifier Engine), Scikit-Learn
* **Data Infrastructure:** Pandas, NumPy, Python-Requests, Regular Expressions (Re)
* **Automation & CI/CD:** GitHub Actions (Headless Cloud Server Workflow)

## 📊 Evaluation & Mathematical Rigor
* **Data Integrity Proof:** Turnovers are modeled dynamically as a function of simulated game pace ($13\%$ of total possessions + Gaussian noise), establishing genuine multi-variable collinearity for the ML model to learn.
* **Deterministic Seeding:** The simulation utilizes the season's start calendar year as an algorithmic random seed, guaranteeing that distinct years produce entirely unique roster environments, player developments, and win/loss records.
* **Baseline Accuracy Limits:** Built to adhere to modern quantitative sports analytics constraints, where baseline models accounting for historical momentum and home advantage aggressively compete at a $\sim 62\% - 66\%$ accuracy boundary.

## ⚙️ Automated Execution
The pipeline runs autonomously via the following cron configuration inside `.github/workflows/daily_pipeline.yml`:
```yaml
on:
  schedule:
    - cron: '0 20 * * *' # Executes daily ahead of evening tip-offs
