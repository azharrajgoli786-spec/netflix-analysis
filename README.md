# Netflix Content Analysis

An exploratory data analysis (EDA) of the Netflix catalog — movies and TV shows available on the platform.

## Dataset

The dataset is the popular **Netflix Movies and TV Shows** dataset from Kaggle:
[https://www.kaggle.com/datasets/shivamb/netflix-shows](https://www.kaggle.com/datasets/shivamb/netflix-shows)

1. Download `netflix_titles.csv`
2. Place it in the `data/` folder

## Project Structure

```
netflix-analysis/
├── README.md
├── requirements.txt
├── data/
│   └── netflix_titles.csv      # you provide this (Kaggle download)
├── notebooks/
│   └── 01-exploratory-analysis.ipynb
└── src/                        # reusable scripts (added later)
```

## Setup

```bash
pip install -r requirements.txt
```

## Usage

Launch Jupyter and open the notebook:

```bash
jupyter notebook notebooks/01-exploratory-analysis.ipynb
```

## Analysis Overview

The notebook covers:

- **Data loading & cleaning** — missing values, date parsing, duration parsing
- **Content mix** — movies vs. TV shows
- **Growth over time** — titles added per year, release-year trends
- **Ratings distribution** — TV-MA, TV-14, etc.
- **Top countries & genres** — where content comes from
- **Director / cast insights** — most frequent contributors
