"""Netflix Content Dashboard — Streamlit + Plotly.

Data: data/netflix_titles.csv
Run:  python -m streamlit run app.py
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# --------------------------------------------------------------------------- #
# Page config & Netflix theme
# --------------------------------------------------------------------------- #
st.set_page_config(
    page_title="Netflix Content Dashboard",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

NETFLIX_RED = "#E50914"
NETFLIX_DARK_RED = "#B20710"
PAPER = "rgba(0,0,0,0)"  # transparent chart backgrounds
GRID = "#2e2e2e"
TEXT = "#f5f5f5"

st.markdown(
    f"""
    <style>
      .stApp {{
        background-color: #141414;
        color: {TEXT};
      }}
      section[data-testid="stSidebar"] {{
        background-color: #1b1b1b;
        border-right: 3px solid {NETFLIX_RED};
      }}
      h1, h2, h3, label, p, li {{ color: {TEXT}; }}
      .netflix-title {{
        font-size: 2.4rem;
        font-weight: 800;
        letter-spacing: 1px;
        margin: 0 0 2px 0;
        color: {TEXT};
      }}
      .netflix-title span {{ color: {NETFLIX_RED}; }}
      .netflix-sub {{ color: #9a9a9a; margin: 0 0 18px 0; font-size: 0.95rem; }}
      .card {{
        background: #1f1f1f;
        border-left: 5px solid {NETFLIX_RED};
        border-radius: 6px;
        padding: 16px 20px;
        height: 105px;
      }}
      .card .value {{
        font-size: 2.1rem; font-weight: 700; color: {NETFLIX_RED};
        line-height: 1.2;
      }}
      .card .label {{ font-size: 0.9rem; color: #b5b5b5; text-transform: uppercase; letter-spacing: 1px; }}
      div[data-testid="stExpander"] {{ background: #1f1f1f; border: 1px solid #333; border-radius: 6px; }}
      .stPlotlyChart {{ background: #1f1f1f; border-radius: 8px; padding: 6px; }}
    </style>
    <div class="netflix-title">NETFLIX <span>Content Dashboard</span></div>
    <div class="netflix-sub">Exploratory analysis of the Netflix Movies &amp; TV Shows catalog (Kaggle dataset)</div>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------- #
# Data loading & cleaning
# --------------------------------------------------------------------------- #
DATA_PATH = Path(__file__).resolve().parent / "data" / "netflix_titles.csv"


@st.cache_data
def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)

    # Missing values: country (831), rating (4), date_added (10)
    df["country"] = df["country"].fillna("Unknown").str.strip()
    df["rating"] = df["rating"].fillna("Unknown").str.strip()

    df["date_added"] = pd.to_datetime(
        df["date_added"].astype("string").str.strip(),
        format="%B %d, %Y",
        errors="coerce",
    )
    df["year_added"] = df["date_added"].dt.year  # NaT -> NaN

    df["listed_in"] = df["listed_in"].fillna("").str.strip()
    return df


df = load_data(DATA_PATH)

# --------------------------------------------------------------------------- #
# Sidebar filters
# --------------------------------------------------------------------------- #
st.sidebar.header("🔍 Filters")

selected_types = st.sidebar.multiselect(
    "Content type",
    options=["Movie", "TV Show"],
    default=["Movie", "TV Show"],
)

year_min = int(df["release_year"].min())
year_max = int(df["release_year"].max())
year_range = st.sidebar.slider(
    "Release year",
    min_value=year_min,
    max_value=year_max,
    value=(year_min, year_max),
)

st.sidebar.caption(
    f"Missing values handled — country: {int(df['country'].eq('Unknown').sum())}, "
    f"rating: {int(df['rating'].eq('Unknown').sum())}, "
    f"date_added: {int(df['date_added'].isna().sum())} (excluded from the timeline)"
)

# --------------------------------------------------------------------------- #
# Apply filters
# --------------------------------------------------------------------------- #
filtered = df[
    df["type"].isin(selected_types)
    & df["release_year"].between(year_range[0], year_range[1])
].copy()

if filtered.empty:
    st.warning("No titles match the current filters.")
    st.stop()

# --------------------------------------------------------------------------- #
# Summary cards
# --------------------------------------------------------------------------- #
total = len(filtered)
n_movies = int((filtered["type"] == "Movie").sum())
n_shows = int((filtered["type"] == "TV Show").sum())
n_ratings = int(filtered["rating"].nunique())

c1, c2, c3, c4 = st.columns(4)
for col, value, label in (
    (c1, f"{total:,}", "Total Titles"),
    (c2, f"{n_movies:,}", "Movies"),
    (c3, f"{n_shows:,}", "TV Shows"),
    (c4, f"{n_ratings:,}", "Rating Types"),
):
    col.markdown(
        f'<div class="card"><div class="value">{value}</div>'
        f'<div class="label">{label}</div></div>',
        unsafe_allow_html=True,
    )

st.write("")

# --------------------------------------------------------------------------- #
# Shared Plotly styling
# --------------------------------------------------------------------------- #
AXIS = dict(gridcolor=GRID, zeroline=False, color="#d0d0d0")


def finalize(fig, title: str, height: int = 430):
    fig.update_layout(
        title=dict(text=title, font=dict(size=17, color=TEXT), x=0.02, xanchor="left"),
        template="plotly_dark",
        paper_bgcolor=PAPER,
        plot_bgcolor=PAPER,
        font=dict(color=TEXT, size=13),
        height=height,
        margin=dict(t=60, l=10, r=10, b=10),
        hoverlabel=dict(bgcolor="#1f1f1f", font_color=TEXT),
    )
    fig.update_xaxes(**AXIS)
    fig.update_yaxes(**AXIS)
    return fig


# --------------------------------------------------------------------------- #
# Charts
# --------------------------------------------------------------------------- #
row1_col1, row1_col2 = st.columns(2, gap="large")

# 1) Movies vs TV Shows — pie ---------------------------------------------- #
type_counts = filtered["type"].value_counts()
fig_pie = px.pie(
    names=type_counts.index,
    values=type_counts.values,
    hole=0.55,
    color=type_counts.index,
    color_discrete_map={"Movie": NETFLIX_RED, "TV Show": "#7f7f7f"},
)
fig_pie.update_traces(
    textinfo="label+percent",
    textfont_size=13,
    marker=dict(line=dict(color="#141414", width=2)),
    hovertemplate="%{label}<br>%{value:,} titles<br>%{percent}<extra></extra>",
)
finalize(fig_pie, "Movies vs TV Shows")
row1_col1.plotly_chart(fig_pie, width="stretch", theme=None)

# 2) Titles added per year — line ------------------------------------------ #
added_per_year = (
    filtered.dropna(subset=["year_added"])
    .groupby("year_added")
    .size()
    .reset_index(name="titles")
    .sort_values("year_added")
)
fig_line = px.line(
    added_per_year,
    x="year_added",
    y="titles",
    markers=True,
)
fig_line.update_traces(
    line=dict(color=NETFLIX_RED, width=3),
    marker=dict(size=7, color=NETFLIX_RED, line=dict(color="#ffffff", width=1)),
    hovertemplate="Year %{x}<br>%{y:,} titles<extra></extra>",
)
fig_line.update_layout(showlegend=False)
fig_line.update_xaxes(dtick=1)
finalize(fig_line, "Titles Added to Netflix per Year")
row1_col2.plotly_chart(fig_line, width="stretch", theme=None)

row2_col1, row2_col2 = st.columns(2, gap="large")


def top_split(series: pd.Series, n: int = 10) -> pd.DataFrame:
    """Split comma-separated multi-value column and count the top n."""
    exploded = (
        series[series != ""]
        .str.split(",")
        .explode()
        .str.strip()
        .replace("", pd.NA)
        .dropna()
    )
    counts = exploded.value_counts().head(n).sort_values()
    return pd.DataFrame({"name": counts.index, "count": counts.to_numpy()})


# 3) Top 10 genres — horizontal bar ---------------------------------------- #
genres = top_split(filtered["listed_in"])
fig_genres = px.bar(
    genres,
    x="count",
    y="name",
    orientation="h",
    color="count",
    color_continuous_scale=[NETFLIX_DARK_RED, NETFLIX_RED],
)
fig_genres.update_traces(
    hovertemplate="%{y}<br>%{x:,} titles<extra></extra>",
    marker_line=dict(color="#141414", width=1),
)
fig_genres.update_layout(coloraxis_showscale=False)
fig_genres.update_yaxes(title="")
finalize(fig_genres, "Top 10 Genres")
row2_col1.plotly_chart(fig_genres, width="stretch", theme=None)

# 4) Top 10 countries — horizontal bar -------------------------------------- #
countries = top_split(filtered["country"])
fig_countries = px.bar(
    countries,
    x="count",
    y="name",
    orientation="h",
    color="count",
    color_continuous_scale=[NETFLIX_DARK_RED, NETFLIX_RED],
)
fig_countries.update_traces(
    hovertemplate="%{y}<br>%{x:,} titles<extra></extra>",
    marker_line=dict(color="#141414", width=1),
)
fig_countries.update_layout(coloraxis_showscale=False)
fig_countries.update_yaxes(title="")
finalize(fig_countries, "Top 10 Countries")
row2_col2.plotly_chart(fig_countries, width="stretch", theme=None)

# 5) Ratings distribution — bar --------------------------------------------- #
rating_order = filtered["rating"].value_counts().index
rating_counts = filtered["rating"].value_counts().reindex(rating_order)
fig_ratings = px.bar(
    x=rating_counts.index,
    y=rating_counts.values,
)
fig_ratings.update_traces(
    marker=dict(color=NETFLIX_RED, line=dict(color="#141414", width=1)),
    hovertemplate="%{x}<br>%{y:,} titles<extra></extra>",
)
fig_ratings.update_xaxes(title="")
fig_ratings.update_yaxes(title="Titles")
fig_ratings.update_layout(showlegend=False)
finalize(fig_ratings, "Ratings Distribution")
st.plotly_chart(fig_ratings, width="stretch", theme=None)

# --------------------------------------------------------------------------- #
# Filtered data table
# --------------------------------------------------------------------------- #
display_cols = [
    "show_id",
    "type",
    "title",
    "director",
    "cast",
    "country",
    "date_added",
    "release_year",
    "rating",
    "duration",
    "listed_in",
]

with st.expander(f"📄 View filtered data ({len(filtered):,} rows)"):
    table = filtered[display_cols].copy()
    table["date_added"] = table["date_added"].dt.strftime("%Y-%m-%d")
    st.dataframe(table, width="stretch", height=400, hide_index=True)

st.caption(
    "Source: Kaggle “Netflix Movies and TV Shows” · "
    f"{len(filtered):,} of {len(df):,} titles shown"
)
