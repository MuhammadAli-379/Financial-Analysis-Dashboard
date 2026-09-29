# -*- coding: utf-8 -*-
"""
PSX Financial Analysis Lab
COMSATS University Islamabad
Robust single-file Streamlit application.

Run:
    streamlit run app.py

Recommended requirements:
    streamlit
    pandas
    numpy
    plotly
    matplotlib
    openpyxl
    scikit-learn
"""

import json
import math
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# Optional dependency: pandas Styler.background_gradient uses matplotlib.
try:
    import matplotlib  # noqa: F401
    MATPLOTLIB_AVAILABLE = True
except Exception:
    MATPLOTLIB_AVAILABLE = False


# ============================================================
# APP CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="PSX Financial Analysis Lab",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
.stApp {
    background:#07111f;
    color:#eaf2fb;
}
.block-container {
    max-width:1500px;
    padding-top:4.5rem;
}
[data-testid="stSidebar"] {
    background:#06101d;
}
.hero {
    padding:1.2rem 1.5rem;
    border:1px solid #20364d;
    border-radius:16px;
    background:linear-gradient(135deg,#11243a,#0c1c2e);
    margin-bottom:1rem;
}
.warning {
    border-left:4px solid #ffd166;
    background:#201c0a;
    padding:.7rem 1rem;
    border-radius:10px;
    color:#f6e6a9;
    font-size:.9rem;
}
.card {
    border:1px solid #20364d;
    border-radius:12px;
    padding:1rem;
    background:#0d1b2e;
    margin-bottom:.5rem;
}
.stApp,.stApp p,.stApp label,.stApp li,.stApp h1,.stApp h2,
.stApp h3,.stApp h4,.stApp span,
[data-testid="stMarkdownContainer"] *,
[data-testid="stCaptionContainer"] *,
[data-testid="stMetricValue"] *,
[data-testid="stMetricLabel"] * {
    color:#eaf2fb !important;
}
[data-testid="stHeader"] {
    background:#07111f !important;
}
[data-testid="stHeader"] * {
    color:#9fb6cc !important;
    fill:#9fb6cc !important;
}
[data-testid="stSidebar"] * {
    color:#eaf2fb !important;
}
[data-baseweb="select"]>div,
[data-baseweb="input"],
[data-baseweb="base-input"],
input, textarea {
    background:#0d1b2e !important;
    color:#eaf2fb !important;
    border-color:#20364d !important;
}
[data-baseweb="select"] * {
    color:#eaf2fb !important;
    background:transparent !important;
}
[data-baseweb="popover"] * {
    background:#0d1b2e !important;
    color:#eaf2fb !important;
}
div[role="radiogroup"] {
    gap:.4rem;
    flex-wrap:wrap;
}
label[data-baseweb="radio"] {
    background:#0d1b2e;
    border:1px solid #20364d;
    border-radius:999px;
    padding:.25rem .9rem;
    margin:0 !important;
    cursor:pointer;
}
label[data-baseweb="radio"]:hover {
    border-color:#5cc8ff;
}
label[data-baseweb="radio"]>div:first-child {
    display:none !important;
}
label[data-baseweb="radio"]:has(input:checked) {
    background:#5cc8ff !important;
    border-color:#5cc8ff;
}
label[data-baseweb="radio"]:has(input:checked) * {
    color:#07111f !important;
    font-weight:700;
}
label[data-baseweb="radio"] p {
    font-size:.85rem;
    margin:0;
}
.hero .warning,.hero .warning * {
    color:#f6e6a9 !important;
}
.hero b[style] {
    color:#5cc8ff !important;
}
[data-testid="stMetric"] {
    background:#0d1b2e;
    border:1px solid #20364d;
    border-radius:12px;
    padding:.6rem .9rem;
}
.small-note {
    color:#9fb6cc !important;
    font-size:.82rem;
}
</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# CONSTANTS / DATA MODEL
# ============================================================

YEARS = [2021, 2022, 2023, 2024, 2025]

HK = [
    "revenue",
    "netIncome",
    "npm",
    "roa",
    "roe",
    "current",
    "quick",
    "debtEq",
    "interest",
    "assetTurn",
    "inventoryTurn",
    "receivablesTurn",
    "pe",
    "eps",
    "dividendYield",
]

LBL = dict(
    zip(
        HK,
        [
            "Revenue (PKR m)",
            "Net Income (PKR m)",
            "NPM (%)",
            "ROA (%)",
            "ROE (%)",
            "Current Ratio",
            "Quick Ratio",
            "Debt/Equity",
            "Interest Coverage",
            "Asset Turnover",
            "Inventory Turnover",
            "Receivables Turnover",
            "P/E",
            "EPS",
            "Dividend Yield (%)",
        ],
    )
)

# Generic teaching thresholds. They are deliberately labelled as
# educational heuristics rather than sector-specific recommendations.
RULES = {
    "current": (1.5, "hi"),
    "quick": (1.0, "hi"),
    "debtEq": (1.0, "lo"),
    "interest": (3.0, "hi"),
    "npm": (10.0, "hi"),
    "roa": (5.0, "hi"),
    "roe": (12.0, "hi"),
    "assetTurn": (0.3, "hi"),
    "receivablesTurn": (4.0, "hi"),
}

PAGES = [
    "Executive Dashboard",
    "Trends Explorer",
    "Ratio Scorecard",
    "DuPont Analysis",
    "Growth Analysis",
    "Vertical Analysis",
    "Peer Comparison",
    "Industry / PESTEL",
    "Risk Dashboard",
    "DCF & Monte Carlo",
    "Relative Valuation",
    "Scenario Analysis",
    "Data Integrity",
    "Import & Export",
    "References",
]


# ============================================================
# DATA HELPERS
# ============================================================

def clean_number(value: Any, default: float = np.nan) -> float:
    """Convert common numeric inputs safely to float."""
    if value is None:
        return default
    try:
        if isinstance(value, str):
            value = value.replace(",", "").replace("%", "").strip()
        result = float(value)
        return result if np.isfinite(result) else default
    except Exception:
        return default


def safe_div(a: Any, b: Any, default: float = np.nan) -> float:
    a = clean_number(a)
    b = clean_number(b)
    if not np.isfinite(a) or not np.isfinite(b) or b == 0:
        return default
    return a / b


def fmt(x: Any, d: int = 0) -> str:
    x = clean_number(x)
    if not np.isfinite(x):
        return "N/A"
    return f"{x:,.{d}f}"


def pct_change(new: Any, old: Any) -> float:
    new = clean_number(new)
    old = clean_number(old)
    if not np.isfinite(new) or not np.isfinite(old) or old == 0:
        return np.nan
    return (new / old - 1) * 100


def cagr(a: Any, b: Any, n: int = 4) -> float:
    a = clean_number(a)
    b = clean_number(b)
    if (
        not np.isfinite(a)
        or not np.isfinite(b)
        or a <= 0
        or b <= 0
        or n <= 0
    ):
        return np.nan
    return ((b / a) ** (1 / n) - 1) * 100


def safe_mean(values: Any) -> float:
    arr = pd.to_numeric(pd.Series(values), errors="coerce").to_numpy(dtype=float)
    return float(np.nanmean(arr)) if np.isfinite(arr).any() else np.nan


def light(score: float) -> str:
    score = clean_number(score)
    if not np.isfinite(score):
        return "⚪ N/A"
    if score >= 70:
        return "🟢 Strong"
    if score >= 45:
        return "🟡 Watch"
    return "🔴 Weak"


def mk(
    name: str,
    desc: str,
    rows: List[List[float]],
    ver: Optional[Dict[str, float]],
    vert: Optional[Dict[str, float]],
    src: List[Tuple[str, str]],
) -> Dict[str, Any]:
    ver = ver or {}
    vert = vert or {}
    return {
        "name": name,
        "description": desc,
        "historical": dict(zip(HK, rows)),
        "verified2025": ver,
        "vertical": vert,
        "sources": src,
    }


def validate_company_structure(company: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate a company object before it enters the active dataset."""
    if not isinstance(company, dict):
        return False, "Company record must be a JSON object."

    required = {"name", "historical", "verified2025", "vertical", "sources"}
    missing = required - set(company)
    if missing:
        return False, f"Missing company fields: {', '.join(sorted(missing))}"

    hist = company["historical"]
    if not isinstance(hist, dict):
        return False, "historical must be an object."

    for key in HK:
        if key not in hist:
            return False, f"Missing historical metric: {key}"
        if not isinstance(hist[key], list) or len(hist[key]) != len(YEARS):
            return False, f"{key} must contain exactly {len(YEARS)} values."

    return True, ""


def vget(company: Dict[str, Any], key: str) -> float:
    """
    Return the verified FY2025 value where supplied; otherwise use
    the submitted historical FY2025 value.
    """
    hist = company.get("historical", {})
    verified = company.get("verified2025", {})

    if key in verified:
        return clean_number(verified[key])

    if key == "eps" and "epsRestated" in verified:
        return clean_number(verified["epsRestated"])

    vals = hist.get(key, [])
    if vals:
        return clean_number(vals[-1])

    return np.nan


def hdf(company: Dict[str, Any]) -> pd.DataFrame:
    hist = company["historical"]
    data = {"Year": YEARS}
    for key in HK:
        data[LBL[key]] = pd.to_numeric(hist[key], errors="coerce")
    return pd.DataFrame(data).set_index("Year")


def shares(company: Dict[str, Any]) -> float:
    ni = vget(company, "netIncome")
    eps = vget(company, "eps")
    return safe_div(ni, eps)


def score(metric: str, value: Any) -> float:
    value = clean_number(value)
    if metric not in RULES or not np.isfinite(value):
        return np.nan

    threshold, direction = RULES[metric]

    if direction == "hi":
        return float(np.clip(70 * value / threshold, 0, 100))

    if value <= threshold:
        return 100.0

    return float(np.clip(100 * threshold / value, 0, 100))


def scorecard(company: Dict[str, Any]) -> pd.DataFrame:
    hist = company["historical"]
    rows = []

    for key, (benchmark, direction) in RULES.items():
        values = pd.to_numeric(hist.get(key, []), errors="coerce")
        if len(values) < 2:
            continue

        cur = clean_number(values.iloc[-1])
        prev = clean_number(values.iloc[-2])
        s = score(key, cur)

        rows.append(
            [
                LBL[key],
                cur,
                prev,
                cur - prev if np.isfinite(cur) and np.isfinite(prev) else np.nan,
                benchmark,
                "≥" if direction == "hi" else "≤",
                round(s) if np.isfinite(s) else np.nan,
                light(s),
            ]
        )

    return pd.DataFrame(
        rows,
        columns=[
            "Ratio",
            "FY2025",
            "FY2024",
            "Δ YoY",
            "Benchmark",
            "Rule",
            "Score",
            "Status",
        ],
    )


def style_numeric(
    df: pd.DataFrame,
    decimals: int = 2,
    gradient_col: Optional[str] = None,
):
    """Return a styled DataFrame when possible; safely fall back otherwise."""
    try:
        styler = df.style.format(f"{{:,.{decimals}f}}")
        if gradient_col and MATPLOTLIB_AVAILABLE and gradient_col in df.columns:
            styler = styler.background_gradient(
                subset=[gradient_col],
                cmap="RdYlGn",
                vmin=0,
                vmax=100,
            )
        return styler
    except Exception:
        return df


def style_scorecard(df: pd.DataFrame):
    try:
        styler = df.style.format(
            {
                "FY2025": "{:.2f}",
                "FY2024": "{:.2f}",
                "Δ YoY": "{:+.2f}",
                "Benchmark": "{:.2f}",
                "Score": "{:.0f}",
            }
        )
        if MATPLOTLIB_AVAILABLE and "Score" in df.columns:
            styler = styler.background_gradient(
                subset=["Score"],
                cmap="RdYlGn",
                vmin=0,
                vmax=100,
            )
        return styler
    except Exception:
        return df


# ============================================================
# CHART HELPERS
# ============================================================

def style_fig(fig: go.Figure, height: int = 380, title: Optional[str] = None):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=height,
        margin=dict(l=10, r=10, t=55, b=10),
        legend=dict(orientation="h", y=1.12),
        title=title,
    )
    return fig


def show(fig: go.Figure, height: int = 380, title: Optional[str] = None):
    st.plotly_chart(
        style_fig(fig, height, title),
        use_container_width=True,
        config={"displaylogo": False, "responsive": True},
    )


def lines(
    df: pd.DataFrame,
    cols: List[str],
    title: str,
    height: int = 380,
    bar: bool = False,
):
    fig = go.Figure()

    for col in cols:
        if col not in df.columns:
            continue

        x = df.index
        y = pd.to_numeric(df[col], errors="coerce")

        if bar:
            fig.add_trace(go.Bar(x=x, y=y, name=col))
        else:
            fig.add_trace(
                go.Scatter(
                    x=x,
                    y=y,
                    name=col,
                    mode="lines+markers",
                )
            )

    if not fig.data:
        st.info("No valid data available for this chart.")
        return

    if bar:
        fig.update_layout(barmode="group")

    show(fig, height, title)


# ============================================================
# DCF ENGINE
# ============================================================

def dcf(
    rev0: float,
    growth: float,
    margin: float,
    tax: float,
    capex: float,
    wc: float,
    wacc: float,
    terminal_growth: float,
    net_debt: float,
    shares_outstanding: float,
    years: int = 5,
) -> Dict[str, Any]:

    inputs = [
        rev0,
        growth,
        margin,
        tax,
        capex,
        wc,
        wacc,
        terminal_growth,
        net_debt,
        shares_outstanding,
    ]

    if not all(np.isfinite(clean_number(x)) for x in inputs):
        raise ValueError("DCF inputs contain invalid numeric values.")

    if rev0 <= 0:
        raise ValueError("Revenue must be positive.")

    if shares_outstanding <= 0:
        raise ValueError("Shares outstanding must be positive.")

    if wacc <= terminal_growth:
        raise ValueError("WACC must be greater than terminal growth.")

    if years < 1:
        raise ValueError("Forecast horizon must be at least one year.")

    revenue = rev0
    pv = 0.0
    rows = []

    for t in range(1, years + 1):
        revenue *= 1 + growth / 100
        ebit = revenue * margin / 100
        fcf = ebit * (1 - tax / 100) - revenue * (capex + wc) / 100
        discount_factor = (1 + wacc / 100) ** t
        discounted_fcf = fcf / discount_factor

        pv += discounted_fcf

        rows.append(
            [
                t,
                revenue,
                ebit,
                fcf,
                discounted_fcf,
            ]
        )

    terminal_fcf = rows[-1][3]
    terminal_value = (
        terminal_fcf * (1 + terminal_growth / 100)
        / ((wacc - terminal_growth) / 100)
    )

    pv_terminal = terminal_value / (1 + wacc / 100) ** years
    enterprise_value = pv + pv_terminal
    equity_value = enterprise_value - net_debt
    value_per_share = equity_value / shares_outstanding

    return {
        "rows": rows,
        "pv": pv,
        "tv": terminal_value,
        "pvtv": pv_terminal,
        "ev": enterprise_value,
        "eq": equity_value,
        "ps": value_per_share,
    }


# ============================================================
# DEMO DATA
# ============================================================

DEMO = {
    "OGDC": mk(
        "Oil & Gas Development Company Limited",
        "Large Pakistani upstream exploration and production company.",
        [
            [239774, 279816, 324282, 378423, 401178],
            [91534, 133430, 224617, 208976, 169903],
            [38.28, 39.88, 54.31, 45.07, 42.35],
            [9.57, 11.84, 15.77, 13.03, 10.27],
            [11.89, 15.28, 20.74, 16.71, 12.60],
            [6.40, 5.60, 5.96, 5.86, 8.97],
            [6.21, 5.45, 5.81, 5.73, 8.72],
            [0, 0, 0, 0, 0],
            [5.92, 9.75, 6.17, 3.74, 3.54],
            [.25, .30, .29, .29, .24],
            [5.08, 5.78, 6.15, 7.38, 5.53],
            [.63, .69, .67, .68, .61],
            [9.40, 7.07, 4.79, 4.73, 4.56],
            [21.28, 31.11, 52.23, 48.59, 39.50],
            [3.45, 3.30, 3.42, 4.40, 2.81],
        ],
        {
            "revenue": 401178,
            "netIncome": 169904,
            "eps": 39.50,
            "pe": 5.58,
        },
        {
            "Cost of Revenue": 42.28,
            "Gross Profit": 57.72,
            "Operating Income": 46.40,
            "Net Income": 42.35,
            "Current Assets": 42.47,
            "Net PPE": 57.53,
            "Total Liabilities": 25.06,
            "Total Equity": 74.94,
        },
        [
            ("PSX company page", "https://dps.psx.com.pk/company/OGDC"),
            (
                "OGDCL Financial Reports",
                "https://ogdcl.com/investors/financial-reports?language=en",
            ),
            (
                "OGDCL Financial Highlights",
                "https://ogdcl.com/investors/financial-highlights",
            ),
        ],
    ),
    "PPL": mk(
        "Pakistan Petroleum Limited",
        "Major Pakistani exploration and production company.",
        [
            [149279, 203811, 288053, 291241, 244977],
            [52283, 54356, 97937, 114309, 89949],
            [35.02, 26.67, 33.75, 39.65, 36.72],
            [9.73, 8.65, 12.24, 12.65, 9.68],
            [13.44, 12.50, 17.98, 18.02, 12.76],
            [4.37, 3.52, 3.32, 3.55, 4.78],
            [4.31, 3.48, 3.28, 3.52, 4.72],
            [0, 0, 0, 0, 0],
            [17.25, 13.42, 12.89, 8.85, 6.55],
            [.28, .32, .36, .32, .26],
            [13.79, 12.99, 16.23, 14.78, 10.49],
            [.53, .56, .56, .50, .41],
            [6.25, 6.51, 4.48, 4.24, 4.54],
            [19.21, 19.98, 35.73, 42.44, 33.06],
            [2.92, 1.92, 3.75, 4.17, 3.33],
        ],
        {
            "revenue": 242516,
            "netIncome": 92027,
            "eps": 33.82,
            "pe": 5.03,
            "current": 4.81,
            "roe": 13.0,
        },
        {
            "Cost of Revenue": 37.72,
            "Gross Profit": 62.28,
            "Operating Income": 46.40,
            "Net Income": 36.72,
            "Current Assets": 75.53,
            "Net PPE": 15.54,
            "Total Liabilities": 24.14,
            "Total Equity": 75.86,
        },
        [
            ("PSX company page", "https://dps.psx.com.pk/company/PPL"),
            ("PPL Annual Report 2025", "https://www.ppl.com.pk/content/annual-report-2025"),
            (
                "PPL Financial Highlights",
                "https://www.ppl.com.pk/content/financial-highlights",
            ),
        ],
    ),
    "MARI": mk(
        "Mari Energies Limited",
        "Pakistani E&P company formerly Mari Petroleum Company Limited.",
        [
            [63703, 83135, 128221, 159731, 141486],
            [31445, 33064, 56129, 77288, 65369],
            [49.36, 39.77, 43.77, 48.39, 46.20],
            [20.91, 17.86, 22.05, 22.30, 15.36],
            [27.22, 25.27, 33.33, 34.36, 23.87],
            [3.61, 2.26, 1.98, 2.79, 2.97],
            [3.49, 2.17, 1.86, 2.66, 2.78],
            [0, .01, .01, 0, .04],
            [10.27, 19.77, 17.21, 10.50, 7.86],
            [.42, .45, .50, .46, .33],
            [5.12, 4.93, 3.76, 4.04, 3.17],
            [2.27, 2.57, 2.08, 1.97, 1.63],
            [13.36, 13.80, 9.63, 8.54, 9.18],
            [26.19, 27.54, 46.75, 64.37, 54.45],
            [4.48, 3.63, 3.63, 4.69, 4.34],
        ],
        {
            "revenue": 177097,
            "netIncome": 65136,
            "eps": 54.25,
            "pe": 11.56,
            "current": 2.81,
            "quick": 2.59,
            "roe": 26.23,
            "assetTurn": .46,
            "dividendYield": 7.20,
        },
        {
            "Cost of Revenue": 28.37,
            "Gross Profit": 71.63,
            "Operating Income": 55.03,
            "Net Income": 36.78,
            "Current Assets": 47.90,
            "Net PPE": 47.33,
            "Total Liabilities": 35.62,
            "Total Equity": 64.38,
        },
        [
            ("PSX company page", "https://dps.psx.com.pk/company/MARI"),
            (
                "MariEnergies Annual Reports",
                "https://www.marienergies.com.pk/investors-relations/financial-reports",
            ),
            (
                "MariEnergies Financial Highlights",
                "https://www.marienergies.com.pk/investors-relations/financial-highlights",
            ),
        ],
    ),
}


# ============================================================
# SESSION STATE
# ============================================================

if "custom" not in st.session_state:
    st.session_state.custom = {}

ALL = {**DEMO, **st.session_state.custom}

# Validate built-in and imported data without stopping the entire application.
invalid_records = []
for symbol, company in list(ALL.items()):
    ok, reason = validate_company_structure(company)
    if not ok:
        invalid_records.append((symbol, reason))

if invalid_records:
    for symbol, reason in invalid_records:
        st.error(f"Invalid data record {symbol}: {reason}")


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("📊 PSX Financial Lab")
st.sidebar.caption("Five-Year Academic Analysis Engine v3")

symbols = list(ALL.keys())

if not symbols:
    st.error("No company data is available.")
    st.stop()

sel = st.sidebar.selectbox(
    "Company",
    symbols,
    format_func=lambda x: f"{x} – {ALL[x]['name']}",
)

st.sidebar.markdown("---")
st.sidebar.caption("Select a company, then navigate using the page bar.")

company = ALL[sel]
hist = company["historical"]
verified = company["verified2025"]
D = hdf(company)

page = st.radio(
    "Navigate",
    PAGES,
    horizontal=True,
    label_visibility="collapsed",
    key="main_navigation",
)

st.markdown(
    '<hr style="margin:.2rem 0 .8rem;border-color:#20364d">',
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="hero">
<b style="color:#5cc8ff">
COMSATS UNIVERSITY ISLAMABAD • DEPARTMENT OF MANAGEMENT SCIENCES
</b>
<h2 style="margin:.3rem 0">
PSX Five-Year Financial Analysis Dashboard
</h2>
<div class="warning">
<b>Data-quality note:</b>
submitted history and verified FY2025 snapshots are intentionally kept separate.
Differences may result from restatements, consolidation, units, or methodology.
See <i>Data Integrity</i>.
</div>
</div>
""",
    unsafe_allow_html=True,
)


# ============================================================
# EXECUTIVE DASHBOARD
# ============================================================

if page == "Executive Dashboard":
    st.header(f"{sel} — {company['name']}")
    st.caption(company["description"])

    sc = scorecard(company)
    health = safe_mean(sc["Score"])

    k = st.columns(6)

    revenue_2025 = vget(company, "revenue")
    revenue_2024 = clean_number(hist["revenue"][-2])
    pat_2025 = vget(company, "netIncome")
    pat_2024 = clean_number(hist["netIncome"][-2])

    k[0].metric(
        "Revenue",
        f"{fmt(revenue_2025)}m",
        f"{pct_change(revenue_2025, revenue_2024):+.1f}% YoY"
        if np.isfinite(pct_change(revenue_2025, revenue_2024))
        else "N/A",
    )

    k[1].metric(
        "PAT",
        f"{fmt(pat_2025)}m",
        f"{pct_change(pat_2025, pat_2024):+.1f}% YoY"
        if np.isfinite(pct_change(pat_2025, pat_2024))
        else "N/A",
    )

    k[2].metric("EPS", fmt(vget(company, "eps"), 2))
    k[3].metric("P/E", f"{fmt(vget(company, 'pe'), 2)}x")
    k[4].metric("ROE", f"{fmt(vget(company, 'roe'), 1)}%")
    k[5].metric(
        "Health score",
        f"{fmt(health, 0)}/100",
        light(health),
    )

    a, b = st.columns([3, 2])

    with a:
        fig = go.Figure(
            [
                go.Bar(x=YEARS, y=hist["revenue"], name="Revenue"),
                go.Bar(x=YEARS, y=hist["netIncome"], name="Net income"),
                go.Scatter(
                    x=YEARS,
                    y=hist["npm"],
                    name="NPM %",
                    yaxis="y2",
                    mode="lines+markers",
                ),
            ]
        )
        fig.update_layout(
            barmode="group",
            yaxis2=dict(
                overlaying="y",
                side="right",
                showgrid=False,
                title="NPM %",
            ),
        )
        show(fig, 380, "Scale & margin")

    with b:
        radar = sc.dropna(subset=["Score"])
        if len(radar):
            fig = go.Figure(
                go.Scatterpolar(
                    r=radar["Score"].tolist() + [radar["Score"].iloc[0]],
                    theta=radar["Ratio"].tolist() + [radar["Ratio"].iloc[0]],
                    fill="toself",
                )
            )
            fig.update_layout(
                polar=dict(radialaxis=dict(range=[0, 100])),
            )
            show(fig, 380, "Ratio health radar")
        else:
            st.info("Insufficient scorecard data for radar chart.")

    st.subheader("Automated commentary")

    rev_cagr = cagr(hist["revenue"][0], hist["revenue"][-1])
    ni_cagr = cagr(hist["netIncome"][0], hist["netIncome"][-1])

    peak_ni = np.nanmax(pd.to_numeric(hist["netIncome"], errors="coerce"))
    current_ni = clean_number(hist["netIncome"][-1])
    drawdown = pct_change(current_ni, peak_ni)

    current_ratio = clean_number(hist["current"][-1])
    de = clean_number(hist["debtEq"][-1])
    interest = clean_number(hist["interest"][-1])
    receivables_turn = clean_number(hist["receivablesTurn"][-1])

    notes = []

    if np.isfinite(rev_cagr) and np.isfinite(ni_cagr):
        notes.append(
            f"Revenue CAGR FY21–25 is **{rev_cagr:.1f}%**; "
            f"net income CAGR is **{ni_cagr:.1f}%**."
        )

    if np.isfinite(drawdown):
        if drawdown < -0.1:
            notes.append(
                f"FY2025 net income is approximately **{abs(drawdown):.1f}% "
                f"below the five-year peak**."
            )
        else:
            notes.append("FY2025 net income is at or very close to the five-year peak.")

    if np.isfinite(current_ratio):
        notes.append(
            f"Liquidity: current ratio is **{current_ratio:.2f}x** "
            f"against the teaching benchmark of 1.50x."
        )

    if np.isfinite(de) and np.isfinite(interest):
        notes.append(
            f"Leverage: debt/equity is **{de:.2f}x** and "
            f"interest coverage is **{interest:.1f}x**."
        )

    if np.isfinite(receivables_turn) and receivables_turn > 0:
        notes.append(
            f"Approximate receivable days are **{365 / receivables_turn:.0f} days**."
        )

    for note in notes:
        st.markdown("• " + note)

    st.subheader("Historical dataset")
    st.dataframe(
        D.style.format("{:,.2f}"),
        use_container_width=True,
    )


# ============================================================
# TRENDS EXPLORER
# ============================================================

elif page == "Trends Explorer":
    st.header("Trends Explorer")

    picks = st.multiselect(
        "Metrics",
        list(LBL.values()),
        default=["NPM (%)", "ROA (%)", "ROE (%)"],
    )

    norm = st.toggle("Index to FY2021 = 100", False)

    if not picks:
        st.info("Select at least one metric.")
    else:
        X = D[picks].copy()

        if norm:
            base = X.iloc[0].replace(0, np.nan)
            X = X.divide(base) * 100

        lines(
            X,
            picks,
            "Selected metrics" + (" (indexed)" if norm else ""),
            420,
        )

        if len(picks) > 1:
            cm = X.corr()
            fig = go.Figure(
                go.Heatmap(
                    z=cm.values,
                    x=cm.columns,
                    y=cm.index,
                    zmin=-1,
                    zmax=1,
                    colorscale="RdBu",
                    text=np.round(cm.values, 2),
                    texttemplate="%{text}",
                )
            )
            show(fig, 420, "Correlation matrix")


# ============================================================
# RATIO SCORECARD
# ============================================================

elif page == "Ratio Scorecard":
    st.header("Ratio Scorecard")

    sc = scorecard(company)

    st.dataframe(
        style_scorecard(sc),
        use_container_width=True,
        hide_index=True,
    )

    if len(sc):
        show(
            px.bar(
                sc,
                x="Ratio",
                y="Score",
                color="Score",
                color_continuous_scale="RdYlGn",
                range_color=[0, 100],
            ),
            360,
            "Score by ratio",
        )

    st.caption(
        "Benchmarks are generic teaching thresholds, not sector norms. "
        "The score is a transparent heuristic and is not an investment recommendation."
    )

    t1, t2, t3 = st.tabs(["Liquidity", "Solvency", "Efficiency"])

    with t1:
        lines(D, ["Current Ratio", "Quick Ratio"], "Liquidity")

    with t2:
        lines(D, ["Debt/Equity", "Interest Coverage"], "Solvency")

    with t3:
        lines(
            D,
            ["Asset Turnover", "Inventory Turnover", "Receivables Turnover"],
            "Turnover",
        )

        turnover = clean_number(hist["receivablesTurn"][-1])
        prev_turnover = clean_number(hist["receivablesTurn"][-2])

        if turnover > 0 and prev_turnover > 0:
            days = 365 / turnover
            prev_days = 365 / prev_turnover
            st.metric(
                "Receivable days (365/turnover)",
                f"{days:.0f}",
                f"{days - prev_days:+.0f} vs FY24",
                delta_color="inverse",
            )


# ============================================================
# DUPONT ANALYSIS
# ============================================================

elif page == "DuPont Analysis":
    st.header("DuPont Analysis")

    st.latex(r"ROE = NPM \times Asset\ Turnover \times Equity\ Multiplier")

    rows = []

    for i, year in enumerate(YEARS):
        npm = clean_number(hist["npm"][i])
        at = clean_number(hist["assetTurn"][i])
        roa = clean_number(hist["roa"][i])
        roe = clean_number(hist["roe"][i])

        equity_multiplier = safe_div(roe, roa)

        # NPM is percentage while asset turnover is a multiple.
        implied_roa = npm * at

        rows.append(
            [
                year,
                npm,
                at,
                equity_multiplier,
                implied_roa,
                roa,
                roe,
            ]
        )

    dup = pd.DataFrame(
        rows,
        columns=[
            "Year",
            "NPM (%)",
            "Asset Turnover",
            "Equity Multiplier (ROE/ROA)",
            "Implied ROA (NPM×AT)",
            "Reported ROA",
            "Reported ROE",
        ],
    ).set_index("Year")

    st.dataframe(
        dup.style.format("{:.2f}"),
        use_container_width=True,
    )

    gap = np.nanmax(
        np.abs(
            dup["Implied ROA (NPM×AT)"].to_numpy()
            - dup["Reported ROA"].to_numpy()
        )
    )

    if np.isfinite(gap):
        if gap < 1:
            st.success(
                f"Maximum gap between NPM×AT and reported ROA: {gap:.2f} percentage points."
            )
        else:
            st.warning(
                f"Maximum gap between NPM×AT and reported ROA: {gap:.2f} percentage points. "
                "Check the asset basis and averaging conventions."
            )

    base = dup.iloc[0]
    end = dup.iloc[-1]

    components = {}
    for name, column in [
        ("Margin", "NPM (%)"),
        ("Turnover", "Asset Turnover"),
        ("Leverage", "Equity Multiplier (ROE/ROA)"),
    ]:
        a = clean_number(base[column])
        b = clean_number(end[column])
        if a > 0 and b > 0:
            components[name] = math.log(b / a)

    total = sum(components.values())

    if components and total != 0:
        show(
            go.Figure(
                go.Bar(
                    x=list(components),
                    y=[v / total * 100 for v in components.values()],
                )
            ),
            320,
            "Share of ROE change FY21→FY25 (log decomposition, %)",
        )

    lines(dup, ["Reported ROE", "NPM (%)"], "ROE vs margin")


# ============================================================
# GROWTH ANALYSIS
# ============================================================

elif page == "Growth Analysis":
    st.header("Growth Analysis")

    keys = ["revenue", "netIncome", "eps", "roe", "current"]

    rows = []

    for key in keys:
        start = clean_number(hist[key][0])
        end = clean_number(hist[key][-1])

        rows.append(
            [
                LBL[key],
                start,
                end,
                pct_change(end, start),
                cagr(start, end),
            ]
        )

    growth_df = pd.DataFrame(
        rows,
        columns=[
            "Metric",
            "FY2021",
            "FY2025",
            "Total change (%)",
            "CAGR (%)",
        ],
    )

    st.dataframe(
        growth_df.style.format(
            {
                "FY2021": "{:,.2f}",
                "FY2025": "{:,.2f}",
                "Total change (%)": "{:+.1f}",
                "CAGR (%)": "{:+.1f}",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

    yoy = pd.DataFrame(
        {
            LBL[key]: [
                pct_change(hist[key][i], hist[key][i - 1])
                for i in range(1, len(YEARS))
            ]
            for key in keys
        },
        index=YEARS[1:],
    ).T

    fig = go.Figure(
        go.Heatmap(
            z=yoy.values,
            x=yoy.columns,
            y=yoy.index,
            colorscale="RdYlGn",
            zmid=0,
            text=np.round(yoy.values, 1),
            texttemplate="%{text}%",
        )
    )
    show(fig, 340, "Year-on-year change heatmap")


# ============================================================
# VERTICAL ANALYSIS
# ============================================================

elif page == "Vertical Analysis":
    st.header("Vertical / Common-Size Analysis")

    vt = company.get("vertical", {})

    if not vt:
        st.info("No common-size data supplied for this company.")
    else:
        a, b = st.columns(2)

        income_keys = [
            key
            for key in [
                "Cost of Revenue",
                "Gross Profit",
                "Operating Income",
                "Net Income",
            ]
            if key in vt
        ]

        balance_keys = [
            key
            for key in [
                "Current Assets",
                "Net PPE",
                "Total Liabilities",
                "Total Equity",
            ]
            if key in vt
        ]

        with a:
            if income_keys:
                show(
                    go.Figure(
                        go.Bar(
                            x=[vt[k] for k in income_keys],
                            y=income_keys,
                            orientation="h",
                        )
                    ),
                    300,
                    "Income statement (% revenue)",
                )
            else:
                st.info("No income-statement common-size data.")

        with b:
            if balance_keys:
                show(
                    go.Figure(
                        go.Bar(
                            x=[vt[k] for k in balance_keys],
                            y=balance_keys,
                            orientation="h",
                        )
                    ),
                    300,
                    "Balance sheet common-size data",
                )
            else:
                st.info("No balance-sheet common-size data.")


# ============================================================
# PEER COMPARISON
# ============================================================

elif page == "Peer Comparison":
    st.header("Peer Comparison")

    rows = []

    for symbol, x in ALL.items():
        rows.append(
            [
                symbol,
                vget(x, "revenue"),
                vget(x, "netIncome"),
                vget(x, "eps"),
                vget(x, "pe"),
                vget(x, "current"),
                vget(x, "npm"),
                vget(x, "roe"),
                vget(x, "debtEq"),
                cagr(x["historical"]["revenue"][0], x["historical"]["revenue"][-1]),
            ]
        )

    peer = pd.DataFrame(
        rows,
        columns=[
            "Company",
            "Revenue",
            "PAT",
            "EPS",
            "P/E",
            "Current",
            "NPM %",
            "ROE %",
            "D/E",
            "Rev CAGR %",
        ],
    ).set_index("Company")

    st.dataframe(
        peer.style.format("{:,.2f}"),
        use_container_width=True,
    )

    a, b = st.columns(2)

    with a:
        fig = go.Figure()

        for symbol, x in ALL.items():
            base = clean_number(x["historical"]["revenue"][0])

            if base > 0:
                fig.add_trace(
                    go.Scatter(
                        x=YEARS,
                        y=np.array(x["historical"]["revenue"]) / base * 100,
                        name=symbol,
                        mode="lines+markers",
                    )
                )

        show(fig, 360, "Revenue indexed (FY2021 = 100)")

    with b:
        cols = ["NPM %", "ROE %", "Current", "Rev CAGR %"]

        if len(peer) > 0:
            mins = peer[cols].min()
            ranges = (peer[cols].max() - mins).replace(0, 1)
            normalised = (peer[cols] - mins) / ranges

            fig = go.Figure()

            for symbol in normalised.index:
                values = normalised.loc[symbol].tolist()

                fig.add_trace(
                    go.Scatterpolar(
                        r=values + [values[0]],
                        theta=cols + [cols[0]],
                        name=symbol,
                        fill="toself",
                        opacity=.5,
                    )
                )

            show(fig, 360, "Relative profile (min–max normalised)")

    st.info(
        "Descriptive comparison only. Accounting basis, business mix, commodity exposure, "
        "and capital structure can differ across companies."
    )


# ============================================================
# INDUSTRY / PESTEL
# ============================================================

elif page == "Industry / PESTEL":
    st.header("Industry / PESTEL")

    pestel = [
        (
            "Political / Regulatory",
            "Exploration blocks, permits, fiscal terms, royalties, taxation, "
            "and policy consistency can affect project economics.",
        ),
        (
            "Economic",
            "Oil and gas prices, inflation, interest rates, exchange rates, "
            "and energy demand influence margins and capital expenditure.",
        ),
        (
            "Social",
            "Population, industrial activity, and household energy demand "
            "can influence consumption patterns.",
        ),
        (
            "Technological",
            "Seismic imaging, reservoir analytics, automation, and advanced "
            "extraction technologies can affect recovery and cost.",
        ),
        (
            "Environmental",
            "Emissions requirements, climate policy, water management, and "
            "methane management can affect operations.",
        ),
        (
            "Legal / Geopolitical",
            "Contracts, security conditions, joint-venture rules, and regional "
            "instability can affect operational continuity.",
        ),
    ]

    cols = st.columns(3)

    for i, (title, text) in enumerate(pestel):
        with cols[i % 3]:
            st.markdown(
                f'<div class="card"><b>{title}</b><br>{text}</div>',
                unsafe_allow_html=True,
            )


# ============================================================
# RISK DASHBOARD
# ============================================================

elif page == "Risk Dashboard":
    st.header("Risk Dashboard")
    st.caption("Transparent educational heuristics based on the supplied dataset.")

    de = clean_number(hist["debtEq"][-1])
    cr = clean_number(hist["current"][-1])
    ic = clean_number(hist["interest"][-1])

    npm_values = pd.to_numeric(hist["npm"], errors="coerce")
    npm_mean = npm_values.mean()
    npm_std = npm_values.std(ddof=0)

    volatility = (
        npm_std / npm_mean * 100
        if np.isfinite(npm_mean) and npm_mean != 0
        else np.nan
    )

    receivables_turn = clean_number(hist["receivablesTurn"][-1])
    receivable_days = (
        365 / receivables_turn if receivables_turn > 0 else np.nan
    )

    peak_ni = np.nanmax(pd.to_numeric(hist["netIncome"], errors="coerce"))
    current_ni = clean_number(hist["netIncome"][-1])

    drawdown = (
        (1 - current_ni / peak_ni) * 100
        if peak_ni > 0 and np.isfinite(current_ni)
        else np.nan
    )

    submitted_revenue = clean_number(hist["revenue"][-1])
    verified_revenue = vget(company, "revenue")

    revenue_gap = (
        abs(submitted_revenue / verified_revenue - 1) * 100
        if verified_revenue > 0
        else np.nan
    )

    risk_rows = [
        [
            "Leverage",
            np.clip(de * 50, 0, 100) if np.isfinite(de) else np.nan,
            f"D/E {de:.2f}x" if np.isfinite(de) else "N/A",
        ],
        [
            "Liquidity",
            np.clip(100 - cr * 25, 0, 100) if np.isfinite(cr) else np.nan,
            f"Current {cr:.2f}x" if np.isfinite(cr) else "N/A",
        ],
        [
            "Interest cover",
            np.clip(100 - ic * 8, 0, 100) if np.isfinite(ic) else np.nan,
            f"{ic:.1f}x" if np.isfinite(ic) else "N/A",
        ],
        [
            "Margin volatility",
            np.clip(volatility * 4, 0, 100)
            if np.isfinite(volatility)
            else np.nan,
            f"CV of NPM {volatility:.1f}%"
            if np.isfinite(volatility)
            else "N/A",
        ],
        [
            "Receivables / circular debt",
            np.clip(receivable_days / 2, 0, 100)
            if np.isfinite(receivable_days)
            else np.nan,
            f"{receivable_days:.0f} days"
            if np.isfinite(receivable_days)
            else "N/A",
        ],
        [
            "Earnings drawdown",
            np.clip(drawdown * 2, 0, 100)
            if np.isfinite(drawdown)
            else np.nan,
            f"{drawdown:.1f}% below peak"
            if np.isfinite(drawdown)
            else "N/A",
        ],
        [
            "Data reliability",
            np.clip(revenue_gap * 3, 0, 100)
            if np.isfinite(revenue_gap)
            else np.nan,
            f"Revenue gap {revenue_gap:.1f}%"
            if np.isfinite(revenue_gap)
            else "N/A",
        ],
    ]

    risk_df = pd.DataFrame(
        risk_rows,
        columns=["Risk", "Score", "Evidence"],
    )

    risk_df["Level"] = pd.cut(
        risk_df["Score"],
        [-1, 33, 66, 101],
        labels=["🟢 Low", "🟡 Medium", "🔴 High"],
    )

    a, b = st.columns([2, 3])

    with a:
        st.dataframe(
            risk_df.style.format({"Score": "{:.0f}"}),
            use_container_width=True,
            hide_index=True,
        )

    with b:
        chart_df = risk_df.dropna(subset=["Score"])

        if len(chart_df):
            show(
                px.bar(
                    chart_df,
                    x="Score",
                    y="Risk",
                    orientation="h",
                    color="Score",
                    color_continuous_scale="RdYlGn_r",
                    range_color=[0, 100],
                ),
                380,
                "Risk indicator scores",
            )

    st.markdown(
        "**Structural E&P risks:** commodity price/volume, PKR/USD exposure "
        "on imported capex, reserve depletion, receivables/circular-debt "
        "collections, fiscal-policy changes, and operational continuity."
    )

    st.warning(
        "Scores are transparent heuristics for classroom analysis, not forecasts "
        "or investment advice."
    )


# ============================================================
# DCF & MONTE CARLO
# ============================================================

elif page == "DCF & Monte Carlo":
    st.header("DCF Valuation")
    st.caption("Illustrative academic model — not investment advice.")

    sh = shares(company)

    pe = vget(company, "pe")
    eps = vget(company, "eps")
    market_proxy = pe * eps if np.isfinite(pe) and np.isfinite(eps) else np.nan

    rev0 = vget(company, "revenue")

    if not np.isfinite(sh) or sh <= 0:
        st.error(
            "DCF requires a positive implied share count. Check FY2025 PAT and EPS."
        )
        st.stop()

    if not np.isfinite(rev0) or rev0 <= 0:
        st.error("DCF requires positive FY2025 revenue.")
        st.stop()

    a, b = st.columns([1, 2])

    default_growth = cagr(hist["revenue"][0], hist["revenue"][-1])
    if not np.isfinite(default_growth):
        default_growth = 5.0

    default_margin = (
        clean_number(company["vertical"].get("Operating Income", 35.0))
        if company.get("vertical")
        else 35.0
    )

    with a:
        growth = st.number_input(
            "Revenue growth (%)",
            value=float(np.clip(default_growth, 0, 20)),
            step=.5,
        )

        margin = st.number_input(
            "EBIT margin (%)",
            value=float(np.clip(default_margin, 1, 80)),
            step=.5,
        )

        tax = st.number_input(
            "Tax rate (%)",
            value=39.0,
            min_value=0.0,
            max_value=100.0,
            step=1.0,
        )

        capex = st.number_input(
            "Capex (% revenue)",
            value=8.0,
            min_value=0.0,
            step=.5,
        )

        wc = st.number_input(
            "WC drag (% revenue)",
            value=2.0,
            min_value=-20.0,
            step=.5,
        )

        wacc = st.number_input(
            "WACC (%)",
            value=14.0,
            min_value=.1,
            max_value=100.0,
            step=.5,
        )

        terminal_growth = st.number_input(
            "Terminal growth (%)",
            value=3.0,
            min_value=-10.0,
            max_value=20.0,
            step=.25,
        )

        net_debt = st.number_input(
            "Net debt (PKR m)",
            value=0.0,
            step=1000.0,
        )

        st.caption(
            f"Implied shares ≈ {sh:,.0f}m "
            f"(PAT ÷ EPS). "
            f"Market price proxy = P/E × EPS = "
            f"PKR {market_proxy:,.1f}."
            if np.isfinite(market_proxy)
            else f"Implied shares ≈ {sh:,.0f}m (PAT ÷ EPS)."
        )

    if wacc <= terminal_growth:
        st.error("WACC must exceed terminal growth.")
        st.stop()

    try:
        result = dcf(
            rev0,
            growth,
            margin,
            tax,
            capex,
            wc,
            wacc,
            terminal_growth,
            net_debt,
            sh,
        )
    except Exception as exc:
        st.error(f"DCF calculation could not be completed: {exc}")
        st.stop()

    with b:
        k = st.columns(3)

        k[0].metric(
            "Enterprise value",
            f"{fmt(result['ev'])}m",
        )

        k[1].metric(
            "Model value / share",
            f"PKR {result['ps']:,.1f}",
        )

        if np.isfinite(market_proxy) and market_proxy != 0:
            k[2].metric(
                "vs market proxy",
                f"{(result['ps'] / market_proxy - 1) * 100:+.1f}%",
            )
        else:
            k[2].metric("vs market proxy", "N/A")

        waterfall = go.Figure(
            go.Waterfall(
                x=[
                    "PV explicit FCF",
                    "PV terminal",
                    "Net debt",
                    "Equity",
                ],
                measure=["relative", "relative", "relative", "total"],
                y=[
                    result["pv"],
                    result["pvtv"],
                    -net_debt,
                    0,
                ],
            )
        )

        show(waterfall, 300, "Value bridge (PKR m)")

        terminal_share = safe_div(result["pvtv"], result["ev"]) * 100

        if np.isfinite(terminal_share):
            st.caption(
                f"Terminal value contributes approximately {terminal_share:.0f}% of EV."
            )

    forecast_df = pd.DataFrame(
        result["rows"],
        columns=["Year", "Revenue", "EBIT", "FCF", "Discounted FCF"],
    )

    st.dataframe(
        forecast_df.style.format("{:,.0f}"),
        use_container_width=True,
        hide_index=True,
    )

    t1, t2 = st.tabs(
        ["Sensitivity (WACC × terminal growth)", "Monte Carlo"]
    )

    with t1:
        ws = np.arange(wacc - 3, wacc + 3.1, 1.0)
        gs = np.arange(
            max(-5, terminal_growth - 2),
            terminal_growth + 2.1,
            1.0,
        )

        Z = []

        for tg_value in gs:
            row = []

            for w in ws:
                if w <= tg_value:
                    row.append(np.nan)
                else:
                    try:
                        row.append(
                            dcf(
                                rev0,
                                growth,
                                margin,
                                tax,
                                capex,
                                wc,
                                w,
                                tg_value,
                                net_debt,
                                sh,
                            )["ps"]
                        )
                    except Exception:
                        row.append(np.nan)

            Z.append(row)

        show(
            go.Figure(
                go.Heatmap(
                    z=Z,
                    x=[f"{w:.1f}%" for w in ws],
                    y=[f"{t:.1f}%" for t in gs],
                    colorscale="RdYlGn",
                    text=np.round(np.array(Z, dtype=float), 0),
                    texttemplate="%{text}",
                )
            ),
            360,
            "Value per share (PKR)",
        )

    with t2:
        simulations = st.slider(
            "Simulations",
            500,
            5000,
            2000,
            500,
        )

        rng = np.random.default_rng(42)
        outputs = []

        for _ in range(simulations):
            w = rng.normal(wacc, 1.5)
            tg_sim = rng.normal(terminal_growth, .75)
            growth_sim = rng.normal(growth, 3)
            margin_sim = rng.normal(margin, 4)

            if w - tg_sim <= 2:
                continue

            try:
                value = dcf(
                    rev0,
                    growth_sim,
                    margin_sim,
                    tax,
                    capex,
                    wc,
                    w,
                    tg_sim,
                    net_debt,
                    sh,
                )["ps"]

                if np.isfinite(value):
                    outputs.append(value)
            except Exception:
                continue

        outputs = np.asarray(outputs, dtype=float)

        if len(outputs) < 10:
            st.warning(
                "Too few valid Monte Carlo simulations were generated. "
                "Adjust WACC/terminal-growth assumptions."
            )
        else:
            p5, median, p95 = np.percentile(outputs, [5, 50, 95])

            fig = go.Figure(
                go.Histogram(
                    x=outputs,
                    nbinsx=50,
                )
            )

            if np.isfinite(market_proxy):
                fig.add_vline(
                    x=market_proxy,
                    annotation_text="Market proxy",
                )

            show(
                fig,
                340,
                "Distribution of value per share (PKR)",
            )

            probability = (
                np.mean(outputs > market_proxy) * 100
                if np.isfinite(market_proxy)
                else np.nan
            )

            st.write(
                f"P5 **{p5:,.0f}** | "
                f"Median **{median:,.0f}** | "
                f"P95 **{p95:,.0f}** | "
                + (
                    f"P(value > market) = **{probability:.0f}%**"
                    if np.isfinite(probability)
                    else "Market comparison unavailable."
                )
            )


# ============================================================
# RELATIVE VALUATION
# ============================================================

elif page == "Relative Valuation":
    st.header("Relative Valuation")

    rows = []

    for symbol, x in ALL.items():
        pe = vget(x, "pe")
        eps = vget(x, "eps")
        div_yield = vget(x, "dividendYield")
        roe = vget(x, "roe")

        implied_price = pe * eps if np.isfinite(pe) and np.isfinite(eps) else np.nan

        rows.append(
            [
                symbol,
                pe,
                eps,
                implied_price,
                div_yield,
                roe,
            ]
        )

    relative = pd.DataFrame(
        rows,
        columns=[
            "Company",
            "P/E",
            "EPS",
            "Implied price",
            "Div yield %",
            "ROE %",
        ],
    ).set_index("Company")

    st.dataframe(
        relative.style.format("{:,.2f}"),
        use_container_width=True,
    )

    scatter_df = relative.reset_index().dropna(
        subset=["ROE %", "P/E"]
    )

    if len(scatter_df):
        fig = px.scatter(
            scatter_df,
            x="ROE %",
            y="P/E",
            size="Div yield %",
            text="Company",
            size_max=40,
        )
        fig.update_traces(textposition="top center")
        show(fig, 380, "P/E vs ROE (bubble = dividend yield)")
    else:
        st.info("Insufficient peer data for the scatter plot.")

    pe_values = pd.to_numeric(relative["P/E"], errors="coerce").dropna()

    if len(pe_values):
        median_pe = pe_values.median()
        target_eps = vget(company, "eps")

        if np.isfinite(target_eps):
            st.info(
                f"Peer median P/E = {median_pe:.2f}x. "
                f"Applying that multiple mechanically to {sel}'s EPS gives "
                f"PKR {median_pe * target_eps:,.1f} per share. "
                "This is a descriptive multiple exercise; growth, risk, "
                "accounting basis, and business mix also matter."
            )


# ============================================================
# SCENARIO ANALYSIS
# ============================================================

elif page == "Scenario Analysis":
    st.header("Bear / Base / Bull Scenarios")
    st.caption(
        "Scenario labels describe model assumptions only; they are not predictions."
    )

    a, b, d, e = st.columns(4)

    base_growth = a.number_input(
        "Base growth (%)",
        value=6.0,
        step=.5,
    )

    base_margin = b.number_input(
        "Base net margin (%)",
        value=float(clean_number(hist["npm"][-1], 10)),
        step=.5,
    )

    shock = d.number_input(
        "Shock (%)",
        value=10.0,
        min_value=0.0,
        step=.5,
    )

    horizon = e.slider(
        "Horizon (years)",
        1,
        5,
        3,
    )

    sh = shares(company)

    if not np.isfinite(sh) or sh <= 0:
        st.error("Scenario analysis requires a valid positive implied share count.")
        st.stop()

    cases = {
        "Bear": (
            base_growth - shock,
            max(1, base_margin - shock / 2),
        ),
        "Base": (
            base_growth,
            base_margin,
        ),
        "Bull": (
            base_growth + shock,
            base_margin + shock / 2,
        ),
    }

    fig = go.Figure()
    cols = st.columns(3)

    base_revenue = vget(company, "revenue")
    base_eps = vget(company, "eps")

    for col, (name, (growth_rate, margin_rate)) in zip(
        cols,
        cases.items(),
    ):
        path = [
            base_revenue * (1 + growth_rate / 100) ** t
            for t in range(horizon + 1)
        ]

        profit = path[-1] * margin_rate / 100
        eps = profit / sh

        fig.add_trace(
            go.Scatter(
                x=[2025 + t for t in range(horizon + 1)],
                y=path,
                name=name,
                mode="lines+markers",
            )
        )

        col.subheader(name)
        col.metric(
            f"Revenue FY{2025 + horizon}",
            f"{fmt(path[-1])}m",
        )
        col.metric(
            "Profit",
            f"{fmt(profit)}m",
        )

        eps_delta = (
            pct_change(eps, base_eps)
            if np.isfinite(base_eps)
            else np.nan
        )

        col.metric(
            "EPS",
            f"PKR {eps:,.2f}",
            f"{eps_delta:+.1f}% vs FY25"
            if np.isfinite(eps_delta)
            else "N/A",
        )

    show(fig, 340, "Revenue paths")


# ============================================================
# DATA INTEGRITY
# ============================================================

elif page == "Data Integrity":
    st.header("Data Integrity & Reconciliation")

    rows = []

    for symbol, x in DEMO.items():
        for key, label in [
            ("revenue", "Revenue"),
            ("netIncome", "PAT"),
            ("eps", "EPS"),
            ("pe", "P/E"),
            ("current", "Current ratio"),
            ("roe", "ROE"),
        ]:
            if key not in x.get("verified2025", {}):
                continue

            submitted = clean_number(x["historical"][key][-1])
            verified_value = clean_number(x["verified2025"][key])

            variance = (
                (submitted / verified_value - 1) * 100
                if verified_value != 0
                else np.nan
            )

            if not np.isfinite(variance):
                status = "⚪ N/A"
            elif abs(variance) < .5:
                status = "✅ Verified"
            elif abs(variance) < 5:
                status = "🟡 Minor"
            else:
                status = "🔴 Major"

            rows.append(
                [
                    symbol,
                    label,
                    submitted,
                    verified_value,
                    variance,
                    status,
                ]
            )

    integrity = pd.DataFrame(
        rows,
        columns=[
            "Company",
            "Metric",
            "Submitted",
            "Verified",
            "Variance %",
            "Status",
        ],
    )

    st.dataframe(
        integrity.style.format(
            {
                "Submitted": "{:,.2f}",
                "Verified": "{:,.2f}",
                "Variance %": "{:+.2f}",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

    if len(integrity):
        show(
            px.bar(
                integrity,
                x="Metric",
                y="Variance %",
                color="Company",
                barmode="group",
            ),
            320,
            "Submitted vs verified variance",
        )

    st.subheader("Internal consistency — selected company")

    consistency = []

    for i, year in enumerate(YEARS):
        revenue = clean_number(hist["revenue"][i])
        net_income = clean_number(hist["netIncome"][i])
        reported_npm = clean_number(hist["npm"][i])

        implied_npm = (
            net_income / revenue * 100
            if revenue != 0
            else np.nan
        )

        consistency.append(
            [
                year,
                reported_npm,
                implied_npm,
                reported_npm - implied_npm
                if np.isfinite(reported_npm) and np.isfinite(implied_npm)
                else np.nan,
            ]
        )

    consistency_df = pd.DataFrame(
        consistency,
        columns=[
            "Year",
            "Reported NPM",
            "NI/Revenue",
            "Gap (pp)",
        ],
    )

    st.dataframe(
        consistency_df.style.format("{:.2f}"),
        use_container_width=True,
        hide_index=True,
    )

    st.info(
        "Suggested source priority for a production system: "
        "audited issuer annual report → PSX issuer page → licensed data provider. "
        "The demo dataset in this application is not a live market feed."
    )


# ============================================================
# IMPORT & EXPORT
# ============================================================

elif page == "Import & Export":
    st.header("Import Company")

    template = {
        "symbol": "NEWCO",
        "name": "Example Company",
        "years": YEARS,
        **{key: [1, 2, 3, 4, 5] for key in HK},
        "source": "Source / URL",
    }

    template.update(
        revenue=[100, 110, 120, 130, 140],
        netIncome=[10, 12, 14, 15, 16],
        npm=[10, 10.91, 11.67, 11.54, 11.43],
        roa=[5, 5.5, 6, 6.2, 6.5],
        roe=[8, 9, 10, 10.5, 11],
        current=[2, 2.1, 2.2, 2.3, 2.4],
        quick=[1.8, 1.9, 2, 2.1, 2.2],
        debtEq=[.5, .48, .45, .42, .4],
        interest=[4, 4.5, 5, 5.2, 5.5],
        assetTurn=[.5, .52, .54, .56, .58],
        inventoryTurn=[5, 5.2, 5.4, 5.6, 5.8],
        receivablesTurn=[4, 4.1, 4.2, 4.3, 4.4],
        pe=[10, 9.5, 9, 8.5, 8],
        eps=[2, 2.4, 2.8, 3, 3.2],
        dividendYield=[2, 2.2, 2.4, 2.5, 2.6],
    )

    st.markdown(
        "Upload a JSON file or edit the example JSON below. "
        "All 15 historical metrics require exactly five values."
    )

    uploaded = st.file_uploader(
        "Upload JSON",
        type=["json"],
        key="company_json_upload",
    )

    raw = (
        uploaded.read().decode("utf-8")
        if uploaded is not None
        else st.text_area(
            "…or paste JSON",
            json.dumps(template, indent=2),
            height=420,
        )
    )

    if st.button(
        "Validate & add company",
        type="primary",
        key="validate_add_company",
    ):
        try:
            payload = json.loads(raw)

            if not isinstance(payload, dict):
                raise ValueError("Top-level JSON must be an object.")

            required = set(template.keys())
            missing = sorted(required - set(payload))

            if missing:
                st.error("Missing fields: " + ", ".join(missing))
            elif not isinstance(payload.get("years"), list):
                st.error("years must be a list.")
            elif payload["years"] != YEARS:
                st.error(
                    f"years must exactly match {YEARS}, "
                    "from oldest to newest."
                )
            elif any(
                not isinstance(payload.get(key), list)
                or len(payload[key]) != 5
                for key in HK
            ):
                st.error("Every historical metric must contain exactly 5 values.")
            elif not str(payload.get("symbol", "")).strip():
                st.error("symbol cannot be empty.")
            elif not str(payload.get("name", "")).strip():
                st.error("name cannot be empty.")
            else:
                # Convert numeric series and reject non-numeric values.
                numeric_data = {}

                for key in HK:
                    converted = [
                        clean_number(value)
                        for value in payload[key]
                    ]

                    if any(not np.isfinite(value) for value in converted):
                        raise ValueError(
                            f"{key} contains a non-numeric or invalid value."
                        )

                    numeric_data[key] = converted

                # Check internal NPM consistency.
                npm_gaps = []

                for i in range(5):
                    revenue = numeric_data["revenue"][i]
                    net_income = numeric_data["netIncome"][i]
                    npm = numeric_data["npm"][i]

                    if revenue != 0:
                        npm_gaps.append(
                            abs(net_income / revenue * 100 - npm)
                        )

                if npm_gaps and max(npm_gaps) > 2:
                    st.warning(
                        "NPM differs from NI/Revenue by more than 2 percentage "
                        "points in at least one year. The company will still be "
                        "added after validation."
                    )

                symbol = str(payload["symbol"]).strip().upper()
                name = str(payload["name"]).strip()
                source = str(payload.get("source", "User supplied")).strip()

                custom_company = mk(
                    name,
                    "User-imported company.",
                    [numeric_data[key] for key in HK],
                    {
                        "revenue": numeric_data["revenue"][-1],
                        "netIncome": numeric_data["netIncome"][-1],
                        "eps": numeric_data["eps"][-1],
                        "pe": numeric_data["pe"][-1],
                    },
                    None,
                    [(source, source if source.startswith("http") else "")],
                )

                ok, reason = validate_company_structure(custom_company)

                if not ok:
                    st.error(f"Validation failed: {reason}")
                else:
                    st.session_state.custom[symbol] = custom_company
                    st.success(
                        f"{symbol} added successfully. "
                        "Refresh the page or use the sidebar company selector."
                    )

        except json.JSONDecodeError as exc:
            st.error(f"Invalid JSON: {exc}")
        except Exception as exc:
            st.error(f"Could not import company: {exc}")

    st.header("Export")

    export_a, export_b, export_c = st.columns(3)

    export_a.download_button(
        "⬇ Dataset (CSV)",
        D.to_csv().encode("utf-8"),
        f"{sel}_dataset.csv",
        "text/csv",
        key="download_dataset",
    )

    export_b.download_button(
        "⬇ Scorecard (CSV)",
        scorecard(company).to_csv(index=False).encode("utf-8"),
        f"{sel}_scorecard.csv",
        "text/csv",
        key="download_scorecard",
    )

    export_c.download_button(
        "⬇ Company JSON",
        json.dumps(
            {
                "symbol": sel,
                "name": company["name"],
                "years": YEARS,
                **{
                    key: company["historical"][key]
                    for key in HK
                },
                "verified2025": company.get("verified2025", {}),
                "vertical": company.get("vertical", {}),
                "sources": company.get("sources", []),
            },
            indent=2,
        ).encode("utf-8"),
        f"{sel}_company.json",
        "application/json",
        key="download_company_json",
    )

    st.subheader("Current imported companies")

    if st.session_state.custom:
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "Symbol": symbol,
                        "Company": x["name"],
                        "Source": (
                            x["sources"][0][0]
                            if x.get("sources")
                            else "N/A"
                        ),
                    }
                    for symbol, x in st.session_state.custom.items()
                ]
            ),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No custom companies have been imported in this session.")


# ============================================================
# REFERENCES
# ============================================================

elif page == "References":
    st.header("References")

    sources = company.get("sources", [])

    if not sources:
        st.info("No references have been supplied for this company.")
    else:
        for title, url in sources:
            safe_url = str(url).strip()

            if safe_url.startswith(("http://", "https://")):
                st.markdown(
                    f"""
<div class="card">
<b>{title}</b><br>
<a href="{safe_url}" target="_blank">{safe_url}</a>
</div>
""",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
<div class="card">
<b>{title}</b>
</div>
""",
                    unsafe_allow_html=True,
                )

    st.subheader("Recommended production architecture")

    st.code(
        """Streamlit UI
    ↓
Authorized backend / data adapter
    ↓
PSX feed | annual-report parser | cached dataset
    ↓
Normalization + source metadata
    ↓
Financial ratio engine
    ↓
Charts / valuation / scenarios / exports""",
        language="text",
    )

    st.warning(
        "Never place data-provider credentials, API keys, passwords, or "
        "private tokens in frontend code or a public GitHub repository."
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "COMSATS University Islamabad • Business Finance • "
    "Instructor: Miss Sania Khalid • Student: Muhammad Abubakar"
)

st.caption(
    f"Generated {datetime.now():%Y-%m-%d %H:%M} | "
    "FY2021–FY2025 | "
    "requires: streamlit pandas numpy plotly matplotlib"
)

if not MATPLOTLIB_AVAILABLE:
    st.caption(
        "ℹ️ Matplotlib is not installed. The application will still run, "
        "but Pandas gradient styling is disabled. Add matplotlib to "
        "requirements.txt for full styling."
    )
