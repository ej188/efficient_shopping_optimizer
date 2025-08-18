![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-in--progress-yellow)

# Efficient Shopping Optimizer 🛒

## Overview

This project is now a Streamlit-based grocery basket optimizer that uses a pre-loaded CSV file (`eso_new_ver1.csv`) containing cleaned and updated price and nutrition data. The app provides an interactive interface for users to optimize their grocery basket efficiently without the need for multiple notebooks.

## Objective

The app helps users select the best combination of grocery items within a fixed budget through an interactive UI. Users can adjust weights and constraints to tailor the optimization according to their nutritional and financial goals.

## Optimization Focus

The scoring system is customizable and implemented directly in Python and Streamlit, allowing optimization for various macronutrient goals beyond just protein. The current dataset supports multiple nutritional targets, enabling flexible prioritization such as fiber, calories, fats, or combined weighted scores.

## Algorithm

The optimization uses a greedy selection approach with the option to include multiple quantities per item. This method balances efficiency and user flexibility in constructing an optimal grocery basket.

## Results

The optimizer produces tailored shopping lists based on user-selected budgets and preferences. Users can download the resulting basket as a CSV file directly from the app.

## Data Sources

- USDA FoodData Central: https://fdc.nal.usda.gov/
- NOAA Fisheries: https://www.fisheries.noaa.gov/
- Bureau of Labor Statistics: https://www.bls.gov/cpi/
- Agricultural Marketing Service: https://www.ams.usda.gov/market-news

## File Structure

```
efficient-shopping-optimizer/
│
├── data/
│   └── eso_new_ver1.csv
│
├── figures/
│
├── src/
│   ├── app.py
│   └── optimizer_core.py
│
├── README.md
├── ACKNOWLEDGEMENTS.md
├── requirements.txt
└── .gitignore
```

## Acknowledgements

Special thanks to the USDA FoodData Central, NOAA Fisheries, Bureau of Labor Statistics, and USDA Agricultural Marketing Service for providing the primary datasets used in this project.  
For a full list of data sources and details on how they were used, see [ACKNOWLEDGEMENTS.md](ACKNOWLEDGEMENTS.md).

## How to Run (Python 3.10+ needed!)

### 1. Clone the repository
```bash
git clone https://github.com/ej188/efficient_shopping_optimizer.git
cd efficient_shopping_optimizer
```

### 2. (Optional) Create and activate a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

### 3. Install required packages
```bash
pip install -r requirements.txt
```

### 3.5 (Optional) Quick dependency check
From a clean terminal/venv, verify the core libs import and Streamlit can launch:
```bash
python -c "import streamlit, pandas, numpy; print('deps ok')"
python -c "import src.optimizer_core as m; print('core ok')"
# Optional: Streamlit's built‑in demo
streamlit hello
```
You should see `deps ok` and `core ok` printed. The `streamlit hello` command should open a demo page in your browser.

### 4. Run the Streamlit app
```bash
streamlit run src/app.py
```