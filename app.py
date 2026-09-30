# -*- coding: utf-8 -*-
"""
PSX Financial Analysis Lab  (v2)
COMSATS University Islamabad

Run:  streamlit run app.py
requirements.txt:
    streamlit>=1.50
    pandas
    numpy
    plotly
    matplotlib
    openpyxl
"""

from __future__ import annotations

import io
import json
import math
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

try:
    import matplotlib  # noqa: F401
    MPL = True
except Exception:
    MPL = False

st.set_page_config(
    page_title="PSX Financial Analysis Lab",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# THEME (single, clean stylesheet)
# ============================================================

CSS = """
:root{
  --text:#f2f8ff; --soft:#c5d7e8; --muted:#8299b0;
  --cyan:#54d6ff; --blue:#2498ff; --violet:#8b7cff;
  --green:#35e59a; --yellow:#ffd166; --red:#ff637c;
  --line:rgba(100,190,255,.16); --line2:rgba(92,200,255,.40);
}
.stApp{
  background:
   radial-gradient(circle at 8% 4%,rgba(36,152,255,.16),transparent 28%),
   radial-gradient(circle at 92% 8%,rgba(139,124,255,.15),transparent 26%),
   radial-gradient(circle at 55% 95%,rgba(53,229,154,.06),transparent 30%),
   linear-gradient(135deg,#020611,#040a16 45%,#020712);
  color:var(--text);
}
.stApp::before{
  content:"";position:fixed;inset:0;pointer-events:none;z-index:0;
  background-image:linear-gradient(rgba(92,200,255,.025) 1px,transparent 1px),
                   linear-gradient(90deg,rgba(92,200,255,.025) 1px,transparent 1px);
  background-size:42px 42px;
  mask-image:linear-gradient(to bottom,rgba(0,0,0,.9),rgba(0,0,0,.2));
}
[data-testid="stAppViewContainer"]{position:relative;z-index:1}
.block-container{max-width:1550px;padding-top:2.4rem;padding-bottom:4rem;animation:fadeUp .6s ease-out}
@keyframes fadeUp{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}

.stApp,.stApp p,.stApp label,.stApp li,.stApp h1,.stApp h2,.stApp h3,.stApp h4,
.stApp span,[data-testid="stMarkdownContainer"] *,[data-testid="stMetricValue"] *,
[data-testid="stMetricLabel"] *{color:var(--text)!important}
.small-note,.stCaption,[data-testid="stCaptionContainer"] *{color:var(--muted)!important;font-size:.77rem}

[data-testid="stHeader"]{background:rgba(2,6,17,.72)!important;backdrop-filter:blur(18px);
  border-bottom:1px solid rgba(92,200,255,.08)}
[data-testid="stHeader"] *{color:#9eb5c9!important;fill:#9eb5c9!important}

/* sidebar */
[data-testid="stSidebar"]{background:linear-gradient(180deg,rgba(4,11,25,.95),rgba(3,8,19,.92))!important;
  border-right:1px solid rgba(92,200,255,.14);backdrop-filter:blur(24px)}
[data-testid="stSidebar"] *{color:var(--text)!important}
.sidebar-brand{padding:.8rem .7rem 1rem}
.brand-icon{display:inline-flex;width:48px;height:48px;align-items:center;justify-content:center;
  border-radius:15px;background:linear-gradient(135deg,#159cf4,#695cf6);font-size:1.4rem;
  box-shadow:0 10px 35px rgba(21,156,244,.28);border:1px solid rgba(255,255,255,.18)}
.brand-title{font-size:1.04rem;font-weight:850;margin-top:.7rem}
.brand-subtitle{color:#718ba3!important;font-size:.72rem;line-height:1.55}
.sidebar-section{color:var(--cyan)!important;font-size:.65rem;font-weight:850;letter-spacing:1.7px;
  text-transform:uppercase;margin:1rem .35rem .45rem}
[data-testid="stSidebar"] div[role="radiogroup"]{gap:.28rem}
[data-testid="stSidebar"] label[data-baseweb="radio"]{width:100%;background:transparent!important;
  border:1px solid transparent!important;border-radius:11px!important;padding:.5rem .68rem!important;
  margin:0!important;transition:all .2s ease}
[data-testid="stSidebar"] label[data-baseweb="radio"]:hover{background:rgba(30,71,105,.32)!important;
  border-color:rgba(92,200,255,.14)!important;transform:translateX(3px)}
[data-testid="stSidebar"] label[data-baseweb="radio"]:has(input:checked){
  background:linear-gradient(90deg,rgba(27,151,218,.24),rgba(108,82,225,.15))!important;
  border:1px solid rgba(92,200,255,.30)!important;box-shadow:inset 3px 0 0 #54d6ff}
[data-testid="stSidebar"] label[data-baseweb="radio"]:has(input:checked) p{color:#72dbff!important;font-weight:800!important}
[data-testid="stSidebar"] label[data-baseweb="radio"] p{color:#a9bdd0!important;font-size:.8rem!important;margin:0!important}
[data-testid="stSidebar"] label[data-baseweb="radio"]>div:first-child{display:none!important}

/* hero */
.hero{position:relative;overflow:hidden;padding:1.6rem 1.75rem;border:1px solid rgba(92,200,255,.22);
  border-radius:22px;background:linear-gradient(135deg,rgba(17,42,69,.78),rgba(7,18,35,.72));
  margin-bottom:1.3rem;box-shadow:0 25px 70px rgba(0,0,0,.28),inset 0 1px 0 rgba(255,255,255,.06);
  backdrop-filter:blur(22px)}
.hero::before{content:"";position:absolute;width:420px;height:420px;right:-170px;top:-220px;border-radius:50%;
  background:radial-gradient(circle,rgba(84,214,255,.18),rgba(139,124,255,.08) 42%,transparent 70%);
  animation:glow 9s ease-in-out infinite alternate}
@keyframes glow{to{transform:translate(-35px,30px) scale(1.12)}}
.hero>*{position:relative;z-index:2}
.hero-kicker{color:#54d6ff!important;font-size:.68rem;font-weight:850;letter-spacing:1.8px;text-transform:uppercase}
.hero-title{font-size:1.75rem;font-weight:900;margin:.3rem 0;letter-spacing:-.4px;
  background:linear-gradient(90deg,#fff,#9be8ff 52%,#b8aaff);-webkit-background-clip:text;
  background-clip:text;-webkit-text-fill-color:transparent}
.hero-description{color:#91abc1!important;font-size:.88rem}
.chips{display:flex;flex-wrap:wrap;gap:.45rem;margin-top:.8rem}
.chip{padding:.22rem .65rem;border-radius:999px;font-size:.72rem;font-weight:700;
  border:1px solid var(--line);background:rgba(84,214,255,.07);color:#bfe9ff!important}
.warning{border-left:3px solid var(--yellow);background:linear-gradient(90deg,rgba(255,209,102,.09),rgba(255,209,102,.02));
  padding:.65rem .95rem;border-radius:10px;color:#f7e8ad!important;font-size:.77rem;margin-top:.9rem}
.warning *{color:#f7e8ad!important}

/* headings */
.page-kicker{color:var(--cyan)!important;font-size:.67rem;font-weight:850;letter-spacing:1.8px;text-transform:uppercase}
.page-title{font-size:2rem;font-weight:900;line-height:1.1;letter-spacing:-.7px;margin-bottom:.3rem;color:#f5f9ff!important}
.page-description{color:#8da7bc!important;font-size:.88rem;margin-bottom:1.1rem}

/* cards */
.card{position:relative;overflow:hidden;border:1px solid rgba(92,200,255,.13);border-radius:16px;
  padding:1rem 1.1rem;background:linear-gradient(145deg,rgba(15,36,61,.72),rgba(7,18,34,.65));
  margin-bottom:.7rem;box-shadow:0 18px 55px rgba(0,0,0,.28),inset 0 1px 0 rgba(255,255,255,.055);
  backdrop-filter:blur(18px);transition:transform .22s,border-color .22s,box-shadow .22s}
.card:hover{transform:translateY(-3px);border-color:rgba(92,200,255,.3)}
.card-title{color:#6edaff!important;font-size:.68rem;font-weight:850;letter-spacing:1.05px;text-transform:uppercase;margin-bottom:.28rem}
.card-value{font-size:1.38rem;font-weight:850}
.card-note{color:#829bb1!important;font-size:.74rem;margin-top:.2rem}
.card-body{color:#b8cbd9!important;font-size:.82rem;line-height:1.6}
.insight{border:1px solid var(--line);border-left:3px solid var(--cyan);border-radius:12px;
  padding:.6rem .9rem;margin:.35rem 0;background:rgba(10,29,49,.5);font-size:.85rem}
.insight.good{border-left-color:var(--green)} .insight.bad{border-left-color:var(--red)}
.insight.warn{border-left-color:var(--yellow)}

[data-testid="stMetric"]{position:relative;overflow:hidden;
  background:linear-gradient(145deg,rgba(16,39,65,.82),rgba(7,19,36,.72))!important;
  border:1px solid rgba(92,200,255,.17)!important;border-radius:15px!important;padding:.85rem .95rem!important;
  box-shadow:0 15px 40px rgba(0,0,0,.2);transition:transform .2s,border-color .2s}
[data-testid="stMetric"]:hover{transform:translateY(-3px);border-color:rgba(92,200,255,.42)!important}
[data-testid="stMetricLabel"]{color:#8ca8bd!important;font-size:.73rem!important}
[data-testid="stMetricValue"]{font-weight:900!important}

/* controls */
.stButton>button,.stDownloadButton>button{min-height:40px;border-radius:11px!important;
  border:1px solid rgba(92,200,255,.22)!important;
  background:linear-gradient(135deg,rgba(16,45,73,.82),rgba(8,25,46,.76))!important;
  color:#eef8ff!important;transition:all .18s}
.stButton>button:hover,.stDownloadButton>button:hover{transform:translateY(-2px);
  border-color:rgba(92,200,255,.6)!important;box-shadow:0 0 25px rgba(92,200,255,.12)}
.stButton>button[kind="primary"]{background:linear-gradient(135deg,#0aa9ed,#2678f2 48%,#785cf5)!important;
  border:1px solid rgba(151,232,255,.65)!important;color:#fff!important}
[data-baseweb="input"],[data-baseweb="base-input"],input,textarea{background:rgba(8,24,43,.72)!important;
  color:#edf7ff!important;border-radius:10px!important}
[data-baseweb="select"]>div{background:rgba(8,24,43,.75)!important;color:#eaf4ff!important;
  border:1px solid rgba(92,200,255,.18)!important;border-radius:10px!important}
[data-baseweb="popover"] *{background:#09192c!important;color:#eaf4ff!important}
button[data-baseweb="tab"]{color:#849db3!important;background:transparent!important}
button[data-baseweb="tab"][aria-selected="true"]{color:#5cd9ff!important;font-weight:800!important}
[data-baseweb="tab-highlight"]{background:linear-gradient(90deg,#54d6ff,#8b7cff)!important;height:2px!important}
[data-testid="stDataFrame"]{border:1px solid rgba(92,200,255,.15);border-radius:14px;overflow:hidden}
[data-testid="stPlotlyChart"]{padding:.3rem;border:1px solid rgba(92,200,255,.10);border-radius:16px;
  background:linear-gradient(145deg,rgba(10,29,49,.42),rgba(5,15,29,.28))}
[data-testid="stFileUploader"]{border:1px solid rgba(92,200,255,.18);border-radius:15px;padding:.45rem;
  background:rgba(12,31,53,.6)}
[data-testid="stFileUploader"] section{background:transparent!important;border:none!important}
[data-testid="stAlert"]{border-radius:12px!important;border:1px solid rgba(92,200,255,.14)!important}
[data-testid="stExpander"]{border:1px solid rgba(92,200,255,.13)!important;border-radius:13px!important;
  background:rgba(8,23,42,.55)!important}
.section-divider{height:1px;margin:1.2rem 0;
  background:linear-gradient(90deg,transparent,rgba(84,214,255,.3),rgba(139,124,255,.25),transparent)}
.footer{border-top:1px solid rgba(92,200,255,.12);margin-top:2.5rem;padding-top:1.2rem;text-align:center;
  color:#617b91!important;font-size:.72rem}
::-webkit-scrollbar{width:9px;height:9px}::-webkit-scrollbar-track{background:#020611}
::-webkit-scrollbar-thumb{background:linear-gradient(180deg,#155d83,#5148a0);border-radius:20px;border:2px solid #020611}
@media(max-width:900px){.block-container{padding:1.2rem .8rem 3rem}.page-title{font-size:1.5rem}.hero-title{font-size:1.3rem}}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
"""
st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)

# ============================================================
# CONSTANTS
# ============================================================

YEARS = [2021, 2022, 2023, 2024, 2025]

HK = ["revenue", "netIncome", "npm", "roa", "roe", "current", "quick", "debtEq",
      "interest", "assetTurn", "inventoryTurn", "receivablesTurn", "pe", "eps", "dividendYield"]

LBL = dict(zip(HK, [
    "Revenue (PKR m)", "Net Income (PKR m)", "NPM (%)", "ROA (%)", "ROE (%)",
    "Current Ratio", "Quick Ratio", "Debt/Equity", "Interest Coverage", "Asset Turnover",
    "Inventory Turnover", "Receivables Turnover", "P/E", "EPS", "Dividend Yield (%)",
]))

RULES = {
    "current": (1.5, "hi"), "quick": (1.0, "hi"), "debtEq": (1.0, "lo"),
    "interest": (3.0, "hi"), "npm": (10.0, "hi"), "roa": (5.0, "hi"),
    "roe": (12.0, "hi"), "assetTurn": (0.3, "hi"), "receivablesTurn": (4.0, "hi"),
}

PAGE_META = {
    "Executive Dashboard": ("🏠", "Executive Overview", "Five-year performance, profitability, liquidity and analytical health."),
    "Trends Explorer": ("📈", "Financial Trends", "Historical movements, indexed performance and metric relationships."),
    "Ratio Scorecard": ("🎯", "Ratio Scorecard", "Transparent educational scorecard for liquidity, solvency and efficiency."),
    "DuPont Analysis": ("🧩", "DuPont Analysis", "Decompose ROE into margin, asset efficiency and leverage."),
    "Growth Analysis": ("🚀", "Growth Analysis", "CAGR, total growth and year-over-year changes."),
    "Vertical Analysis": ("📊", "Vertical Analysis", "Common-size income-statement and balance-sheet composition."),
    "Peer Comparison": ("⚖️", "Peer Comparison", "Compare indicators across companies in the active dataset."),
    "Industry / PESTEL": ("🌐", "Industry / PESTEL", "External forces affecting Pakistani E&P companies."),
    "Risk Dashboard": ("🛡️", "Risk Dashboard", "Leverage, liquidity, margin, earnings and data-quality indicators."),
    "DCF & Monte Carlo": ("💰", "DCF & Monte Carlo", "Discounted cash flow, sensitivities, tornado and simulated ranges."),
    "Relative Valuation": ("💹", "Relative Valuation", "P/E, EPS, dividend yield and ROE across peers, plus a valuation range."),
    "Scenario Analysis": ("🔮", "Scenario Analysis", "How alternative growth and margin assumptions affect revenue and EPS."),
    "Data Integrity": ("🔍", "Data Integrity", "Reconcile submitted vs verified FY2025 values and internal consistency."),
    "Import & Export": ("📁", "Import & Export", "Import datasets; export CSV, JSON, Excel and a Markdown report."),
    "References": ("📚", "References", "Company sources and recommended production architecture."),
}
PAGES = list(PAGE_META)

PALETTE = ["#5cc8ff", "#42d392", "#9b8cff", "#ffd166", "#ff7b72", "#4dd0e1"]

# ============================================================
# HELPERS
# ============================================================


def clean_number(value: Any, default: float = np.nan) -> float:
    if value is None or isinstance(value, bool):
        return default
    try:
        if isinstance(value, str):
            value = value.replace(",", "").replace("%", "").strip()
        r = float(value)
        return r if np.isfinite(r) else default
    except Exception:
        return default


def safe_div(a: Any, b: Any, default: float = np.nan) -> float:
    a, b = clean_number(a), clean_number(b)
    if not np.isfinite(a) or not np.isfinite(b) or b == 0:
        return default
    return a / b


def fmt(x: Any, d: int = 0) -> str:
    x = clean_number(x)
    return "N/A" if not np.isfinite(x) else f"{x:,.{d}f}"


def pct_change(new: Any, old: Any) -> float:
    new, old = clean_number(new), clean_number(old)
    if not np.isfinite(new) or not np.isfinite(old) or old == 0:
        return np.nan
    return (new / old - 1) * 100


def cagr(a: Any, b: Any, n: int = 4) -> float:
    a, b = clean_number(a), clean_number(b)
    if not (np.isfinite(a) and np.isfinite(b)) or a <= 0 or b <= 0 or n <= 0:
        return np.nan
    return ((b / a) ** (1 / n) - 1) * 100


def safe_mean(values: Any) -> float:
    arr = pd.to_numeric(pd.Series(values), errors="coerce").to_numpy(dtype=float)
    return float(np.nanmean(arr)) if np.isfinite(arr).any() else np.nan


def light(s: float) -> str:
    s = clean_number(s)
    if not np.isfinite(s):
        return "⚪ N/A"
    return "🟢 Strong" if s >= 70 else "🟡 Watch" if s >= 45 else "🔴 Weak"


def mk(name, desc, rows, ver, vert, src) -> Dict[str, Any]:
    return {"name": name, "description": desc, "historical": dict(zip(HK, rows)),
            "verified2025": ver or {}, "vertical": vert or {}, "sources": src}


def validate_company_structure(c: Dict[str, Any]) -> Tuple[bool, str]:
    if not isinstance(c, dict):
        return False, "Company record must be an object."
    missing = {"name", "historical", "verified2025", "vertical", "sources"} - set(c)
    if missing:
        return False, "Missing fields: " + ", ".join(sorted(missing))
    h = c["historical"]
    if not isinstance(h, dict):
        return False, "historical must be an object."
    for k in HK:
        if k not in h:
            return False, f"Missing metric: {k}"
        if not isinstance(h[k], list) or len(h[k]) != len(YEARS):
            return False, f"{k} must contain exactly {len(YEARS)} values."
        if any(not np.isfinite(clean_number(v)) for v in h[k]):
            return False, f"{k} contains an invalid value."
    return True, ""


def vget(c: Dict[str, Any], key: str) -> float:
    ver, h = c.get("verified2025", {}), c.get("historical", {})
    if key in ver:
        return clean_number(ver[key])
    vals = h.get(key, [])
    return clean_number(vals[-1]) if vals else np.nan


def hdf(c: Dict[str, Any]) -> pd.DataFrame:
    data = {"Year": YEARS}
    for k in HK:
        data[LBL[k]] = pd.to_numeric(pd.Series(c["historical"][k]), errors="coerce").to_numpy()
    return pd.DataFrame(data).set_index("Year")


def shares(c: Dict[str, Any]) -> float:
    return safe_div(vget(c, "netIncome"), vget(c, "eps"))


def score(metric: str, value: Any) -> float:
    v = clean_number(value)
    if metric not in RULES or not np.isfinite(v):
        return np.nan
    thr, d = RULES[metric]
    if d == "hi":
        return float(np.clip(70 * v / thr, 0, 100))
    return 100.0 if v <= thr else float(np.clip(100 * thr / v, 0, 100))


def scorecard(c: Dict[str, Any]) -> pd.DataFrame:
    rows = []
    for k, (bench, d) in RULES.items():
        vals = pd.Series(pd.to_numeric(c["historical"].get(k, []), errors="coerce"))
        if len(vals) < 2:
            continue
        cur, prev = vget(c, k), clean_number(vals.iloc[-2])
        s = score(k, cur)
        rows.append([LBL[k], cur, prev, cur - prev if np.isfinite(cur) and np.isfinite(prev) else np.nan,
                     bench, "≥" if d == "hi" else "≤", round(s) if np.isfinite(s) else np.nan, light(s)])
    return pd.DataFrame(rows, columns=["Ratio", "FY2025", "FY2024", "Δ YoY", "Benchmark", "Rule", "Score", "Status"])


def style_scorecard(df: pd.DataFrame):
    try:
        s = df.style.format({"FY2025": "{:.2f}", "FY2024": "{:.2f}", "Δ YoY": "{:+.2f}",
                             "Benchmark": "{:.2f}", "Score": "{:.0f}"})
        if MPL and "Score" in df.columns:
            s = s.background_gradient(subset=["Score"], cmap="RdYlGn", vmin=0, vmax=100)
        return s
    except Exception:
        return df


# ---------- UI helpers ----------

def page_header(name: str):
    icon, title, desc = PAGE_META[name]
    st.markdown(f'<div class="page-kicker">{icon} {name}</div><div class="page-title">{title}</div>'
                f'<div class="page-description">{desc}</div>', unsafe_allow_html=True)


def section_title(title: str, sub: str = ""):
    s = f'<div class="small-note">{sub}</div>' if sub else ""
    st.markdown(f'<div style="margin:.8rem 0 .5rem"><div style="font-size:1.05rem;font-weight:800">{title}</div>{s}</div>',
                unsafe_allow_html=True)


def divider():
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)


def card(title: str, body: str, min_h: int = 0):
    st.markdown(f'<div class="card" style="min-height:{min_h}px"><div class="card-title">{title}</div>'
                f'<div class="card-body">{body}</div></div>', unsafe_allow_html=True)


def insight(text: str, kind: str = ""):
    st.markdown(f'<div class="insight {kind}">{text}</div>', unsafe_allow_html=True)


_chart_n = [0]


def show(fig: go.Figure, height: int = 380, title: Optional[str] = None):
    fig.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        height=height, margin=dict(l=10, r=10, t=55, b=10),
        font=dict(family="Inter, Arial, sans-serif", color="#dbeafe"),
        title=dict(text=title, font=dict(size=15, color="#eaf4ff")),
        legend=dict(orientation="h", y=1.12, font=dict(size=11)),
        hoverlabel=dict(bgcolor="#0b1d30", bordercolor="#2a526f", font_color="#eaf4ff"),
    )
    fig.update_xaxes(gridcolor="rgba(120,160,190,.10)", zerolinecolor="rgba(120,160,190,.15)")
    fig.update_yaxes(gridcolor="rgba(120,160,190,.10)", zerolinecolor="rgba(120,160,190,.15)")
    _chart_n[0] += 1
    st.plotly_chart(fig, width="stretch", key=f"pc_{_chart_n[0]}",
                    config={"displaylogo": False, "responsive": True})


def lines(df: pd.DataFrame, cols: List[str], title: str, height: int = 380, bar: bool = False):
    fig = go.Figure()
    for i, c in enumerate(cols):
        if c not in df.columns:
            continue
        y = pd.to_numeric(df[c], errors="coerce")
        col = PALETTE[i % len(PALETTE)]
        if bar:
            fig.add_trace(go.Bar(x=df.index, y=y, name=c, marker_color=col))
        else:
            fig.add_trace(go.Scatter(x=df.index, y=y, name=c, mode="lines+markers",
                                     line=dict(width=3, color=col), marker=dict(size=7, color=col)))
    if not fig.data:
        st.info("No valid data available for this chart.")
        return
    if bar:
        fig.update_layout(barmode="group")
    fig.update_xaxes(dtick=1)
    show(fig, height, title)


def gauge(value: float, title: str, height: int = 260):
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=value if np.isfinite(value) else 0,
        number=dict(suffix="/100", font=dict(size=34)),
        gauge=dict(axis=dict(range=[0, 100]), bar=dict(color="#54d6ff"),
                   bgcolor="rgba(0,0,0,0)", borderwidth=0,
                   steps=[dict(range=[0, 45], color="rgba(255,99,124,.28)"),
                          dict(range=[45, 70], color="rgba(255,209,102,.25)"),
                          dict(range=[70, 100], color="rgba(53,229,154,.25)")])))
    show(fig, height, title)


# ============================================================
# VALUATION ENGINE
# ============================================================


def dcf(rev0, growth, margin, tax, capex, wc, wacc, tg, net_debt, sh, years: int = 5) -> Dict[str, Any]:
    vals = [rev0, growth, margin, tax, capex, wc, wacc, tg, net_debt, sh]
    if not all(np.isfinite(clean_number(x)) for x in vals):
        raise ValueError("DCF inputs contain invalid numeric values.")
    if rev0 <= 0 or sh <= 0:
        raise ValueError("Revenue and shares must be positive.")
    if wacc <= tg:
        raise ValueError("WACC must exceed terminal growth.")
    rev, pv, rows = rev0, 0.0, []
    for t in range(1, years + 1):
        rev *= 1 + growth / 100
        ebit = rev * margin / 100
        fcf = ebit * (1 - tax / 100) - rev * (capex + wc) / 100
        d = fcf / (1 + wacc / 100) ** t
        pv += d
        rows.append([t, rev, ebit, fcf, d])
    tv = rows[-1][3] * (1 + tg / 100) / ((wacc - tg) / 100)
    pvtv = tv / (1 + wacc / 100) ** years
    ev = pv + pvtv
    eq = ev - net_debt
    return {"rows": rows, "pv": pv, "tv": tv, "pvtv": pvtv, "ev": ev, "eq": eq, "ps": eq / sh}


def default_dcf(c: Dict[str, Any]) -> Dict[str, float]:
    g = cagr(c["historical"]["revenue"][0], c["historical"]["revenue"][-1])
    g = float(np.clip(g if np.isfinite(g) else 5.0, 0, 20))
    m = clean_number(c.get("vertical", {}).get("Operating Income", 35.0), 35.0)
    return dict(growth=g, margin=float(np.clip(m, 1, 80)), tax=39.0, capex=8.0, wc=2.0,
                wacc=14.0, tg=3.0, net_debt=0.0)


def base_dcf_value(c: Dict[str, Any]) -> float:
    sh, rev0 = shares(c), vget(c, "revenue")
    if not (np.isfinite(sh) and sh > 0 and np.isfinite(rev0) and rev0 > 0):
        return np.nan
    p = default_dcf(c)
    try:
        return dcf(rev0, p["growth"], p["margin"], p["tax"], p["capex"], p["wc"], p["wacc"], p["tg"],
                   p["net_debt"], sh)["ps"]
    except Exception:
        return np.nan


# ============================================================
# DEMO DATA
# ============================================================

DEMO = {
    "OGDC": mk(
        "Oil & Gas Development Company Limited",
        "Large Pakistani upstream exploration and production company.",
        [[239774, 279816, 324282, 378423, 401178], [91534, 133430, 224617, 208976, 169903],
         [38.28, 39.88, 54.31, 45.07, 42.35], [9.57, 11.84, 15.77, 13.03, 10.27],
         [11.89, 15.28, 20.74, 16.71, 12.60], [6.40, 5.60, 5.96, 5.86, 8.97],
         [6.21, 5.45, 5.81, 5.73, 8.72], [0, 0, 0, 0, 0], [5.92, 9.75, 6.17, 3.74, 3.54],
         [.25, .30, .29, .29, .24], [5.08, 5.78, 6.15, 7.38, 5.53], [.63, .69, .67, .68, .61],
         [9.40, 7.07, 4.79, 4.73, 4.56], [21.28, 31.11, 52.23, 48.59, 39.50],
         [3.45, 3.30, 3.42, 4.40, 2.81]],
        {"revenue": 401178, "netIncome": 169904, "eps": 39.50, "pe": 5.58},
        {"Cost of Revenue": 42.28, "Gross Profit": 57.72, "Operating Income": 46.40, "Net Income": 42.35,
         "Current Assets": 42.47, "Net PPE": 57.53, "Total Liabilities": 25.06, "Total Equity": 74.94},
        [("PSX company page", "https://dps.psx.com.pk/company/OGDC"),
         ("OGDCL Financial Reports", "https://ogdcl.com/investors/financial-reports?language=en"),
         ("OGDCL Financial Highlights", "https://ogdcl.com/investors/financial-highlights")]),
    "PPL": mk(
        "Pakistan Petroleum Limited",
        "Major Pakistani exploration and production company.",
        [[149279, 203811, 288053, 291241, 244977], [52283, 54356, 97937, 114309, 89949],
         [35.02, 26.67, 33.75, 39.65, 36.72], [9.73, 8.65, 12.24, 12.65, 9.68],
         [13.44, 12.50, 17.98, 18.02, 12.76], [4.37, 3.52, 3.32, 3.55, 4.78],
         [4.31, 3.48, 3.28, 3.52, 4.72], [0, 0, 0, 0, 0], [17.25, 13.42, 12.89, 8.85, 6.55],
         [.28, .32, .36, .32, .26], [13.79, 12.99, 16.23, 14.78, 10.49], [.53, .56, .56, .50, .41],
         [6.25, 6.51, 4.48, 4.24, 4.54], [19.21, 19.98, 35.73, 42.44, 33.06],
         [2.92, 1.92, 3.75, 4.17, 3.33]],
        {"revenue": 242516, "netIncome": 92027, "eps": 33.82, "pe": 5.03, "current": 4.81, "roe": 13.0},
        {"Cost of Revenue": 37.72, "Gross Profit": 62.28, "Operating Income": 46.40, "Net Income": 36.72,
         "Current Assets": 75.53, "Net PPE": 15.54, "Total Liabilities": 24.14, "Total Equity": 75.86},
        [("PSX company page", "https://dps.psx.com.pk/company/PPL"),
         ("PPL Annual Report 2025", "https://www.ppl.com.pk/content/annual-report-2025"),
         ("PPL Financial Highlights", "https://www.ppl.com.pk/content/financial-highlights")]),
    "MARI": mk(
        "Mari Energies Limited",
        "Pakistani E&P company formerly Mari Petroleum Company Limited.",
        [[63703, 83135, 128221, 159731, 141486], [31445, 33064, 56129, 77288, 65369],
         [49.36, 39.77, 43.77, 48.39, 46.20], [20.91, 17.86, 22.05, 22.30, 15.36],
         [27.22, 25.27, 33.33, 34.36, 23.87], [3.61, 2.26, 1.98, 2.79, 2.97],
         [3.49, 2.17, 1.86, 2.66, 2.78], [0, .01, .01, 0, .04], [10.27, 19.77, 17.21, 10.50, 7.86],
         [.42, .45, .50, .46, .33], [5.12, 4.93, 3.76, 4.04, 3.17], [2.27, 2.57, 2.08, 1.97, 1.63],
         [13.36, 13.80, 9.63, 8.54, 9.18], [26.19, 27.54, 46.75, 64.37, 54.45],
         [4.48, 3.63, 3.63, 4.69, 4.34]],
        {"revenue": 177097, "netIncome": 65136, "eps": 54.25, "pe": 11.56, "current": 2.81, "quick": 2.59,
         "roe": 26.23, "assetTurn": .46, "dividendYield": 7.20},
        {"Cost of Revenue": 28.37, "Gross Profit": 71.63, "Operating Income": 55.03, "Net Income": 36.78,
         "Current Assets": 47.90, "Net PPE": 47.33, "Total Liabilities": 35.62, "Total Equity": 64.38},
        [("PSX company page", "https://dps.psx.com.pk/company/MARI"),
         ("MariEnergies Annual Reports", "https://www.marienergies.com.pk/investors-relations/financial-reports"),
         ("MariEnergies Financial Highlights", "https://www.marienergies.com.pk/investors-relations/financial-highlights")]),
}

# ============================================================
# SESSION + DATASET
# ============================================================

st.session_state.setdefault("custom", {})

ALL: Dict[str, Dict[str, Any]] = {}
for _sym, _c in {**DEMO, **st.session_state.custom}.items():
    _ok, _why = validate_company_structure(_c)
    if _ok:
        ALL[_sym] = _c
    else:
        st.warning(f"Skipping invalid company **{_sym}**: {_why}")

if not ALL:
    st.error("No valid company data is available.")
    st.stop()

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("""
      <div class="sidebar-brand"><div class="brand-icon">📊</div>
      <div class="brand-title">PSX Financial Lab</div>
      <div class="brand-subtitle">COMSATS University Islamabad<br>Five-Year Academic Analysis Engine</div></div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="sidebar-section">Company</div>', unsafe_allow_html=True)
    sel = st.selectbox("Company", list(ALL), format_func=lambda x: f"{x} — {ALL[x]['name']}",
                       label_visibility="collapsed")
    st.markdown('<div class="sidebar-section">Analysis Modules</div>', unsafe_allow_html=True)
    page = st.radio("Navigation", PAGES, format_func=lambda p: f"{PAGE_META[p][0]}  {p}",
                    label_visibility="collapsed", key="main_navigation")
    divider()
    st.markdown('<div class="small-note"><b>Dataset:</b> FY2021–FY2025<br><b>Mode:</b> Academic / illustrative<br>'
                '<b>Market feed:</b> Static demo data</div>', unsafe_allow_html=True)

company = ALL[sel]
hist = company["historical"]
D = hdf(company)
SC = scorecard(company)
HEALTH = safe_mean(SC["Score"]) if len(SC) else np.nan

# ============================================================
# HERO
# ============================================================

_icon = PAGE_META[page][0]
_eps, _pe, _roe = vget(company, "eps"), vget(company, "pe"), vget(company, "roe")
st.markdown(f"""
<div class="hero">
  <div class="hero-kicker">COMSATS UNIVERSITY ISLAMABAD • DEPARTMENT OF MANAGEMENT SCIENCES</div>
  <div class="hero-title">{_icon} PSX Five-Year Financial Analysis Dashboard</div>
  <div class="hero-description">{sel} — {company["name"]}</div>
  <div class="chips">
    <span class="chip">EPS {fmt(_eps, 2)}</span><span class="chip">P/E {fmt(_pe, 2)}x</span>
    <span class="chip">ROE {fmt(_roe, 1)}%</span><span class="chip">Health {light(HEALTH)}</span>
    <span class="chip">FY2021–FY2025</span>
  </div>
  <div class="warning"><b>Data-quality note:</b> submitted historical values and verified FY2025 snapshots are kept
  separate. Differences can come from restatements, consolidation, units or methodology. Review
  <b>Data Integrity</b> before using figures in a report.</div>
</div>""", unsafe_allow_html=True)

# ============================================================
# PAGES
# ============================================================


def build_commentary() -> List[Tuple[str, str]]:
    out: List[Tuple[str, str]] = []
    rc = cagr(hist["revenue"][0], hist["revenue"][-1])
    nc = cagr(hist["netIncome"][0], hist["netIncome"][-1])
    if np.isfinite(rc):
        out.append(("good" if rc > 5 else "warn", f"Revenue CAGR FY21–25 is <b>{rc:.1f}%</b>."))
    if np.isfinite(nc):
        out.append(("good" if nc > 5 else "warn", f"Net income CAGR FY21–25 is <b>{nc:.1f}%</b>."))
    ni = pd.to_numeric(pd.Series(hist["netIncome"]), errors="coerce")
    peak, cur = float(ni.max()), clean_number(hist["netIncome"][-1])
    if peak > 0 and np.isfinite(cur):
        dd = (1 - cur / peak) * 100
        if dd > 1:
            out.append(("bad" if dd > 25 else "warn",
                        f"FY2025 net income is <b>{dd:.1f}% below</b> its five-year peak "
                        f"(FY{YEARS[int(ni.values.argmax())]})."))
        else:
            out.append(("good", "FY2025 net income is at or near the five-year peak."))
    cr = vget(company, "current")
    if np.isfinite(cr):
        out.append(("good" if cr >= 1.5 else "warn", f"Current ratio is <b>{cr:.2f}x</b> vs a 1.50x teaching benchmark."))
    de, ic = vget(company, "debtEq"), vget(company, "interest")
    if np.isfinite(de) and np.isfinite(ic):
        out.append(("good" if de <= 1 else "bad", f"Leverage is <b>{de:.2f}x D/E</b> with interest cover of <b>{ic:.1f}x</b>."))
    rt = vget(company, "receivablesTurn")
    if np.isfinite(rt) and rt > 0:
        out.append(("warn" if 365 / rt > 90 else "", f"Approximate receivable days: <b>{365 / rt:.0f}</b>."))
    return out


def page_executive():
    page_header(page)
    st.caption(company["description"])
    r25, r24 = vget(company, "revenue"), clean_number(hist["revenue"][-2])
    p25, p24 = vget(company, "netIncome"), clean_number(hist["netIncome"][-2])
    rg, pg = pct_change(r25, r24), pct_change(p25, p24)
    k = st.columns(6)
    k[0].metric("Revenue", f"{fmt(r25)}m", f"{rg:+.1f}% YoY" if np.isfinite(rg) else None)
    k[1].metric("PAT", f"{fmt(p25)}m", f"{pg:+.1f}% YoY" if np.isfinite(pg) else None)
    k[2].metric("EPS", fmt(_eps, 2))
    k[3].metric("P/E", f"{fmt(_pe, 2)}x")
    k[4].metric("ROE", f"{fmt(_roe, 1)}%")
    k[5].metric("Health", f"{fmt(HEALTH)}/100" if np.isfinite(HEALTH) else "N/A", light(HEALTH), delta_color="off")
    divider()
    a, b = st.columns([1.7, 1])
    with a:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=YEARS, y=hist["revenue"], name="Revenue", marker_color="#1597d1"))
        fig.add_trace(go.Bar(x=YEARS, y=hist["netIncome"], name="Net income", marker_color="#42d392"))
        fig.add_trace(go.Scatter(x=YEARS, y=hist["npm"], name="NPM %", yaxis="y2", mode="lines+markers",
                                 line=dict(color="#ffd166", width=3)))
        fig.update_layout(barmode="group", yaxis2=dict(overlaying="y", side="right", showgrid=False, title="NPM %"))
        fig.update_xaxes(dtick=1)
        show(fig, 390, "Scale & profitability")
    with b:
        gauge(HEALTH, "Overall ratio health")
    c1, c2 = st.columns([1, 1.4])
    with c1:
        radar = SC.dropna(subset=["Score"])
        if len(radar):
            fig = go.Figure(go.Scatterpolar(
                r=radar["Score"].tolist() + [radar["Score"].iloc[0]],
                theta=radar["Ratio"].tolist() + [radar["Ratio"].iloc[0]],
                fill="toself", line=dict(color="#5cc8ff", width=2), fillcolor="rgba(92,200,255,.18)"))
            fig.update_layout(polar=dict(bgcolor="rgba(0,0,0,0)", radialaxis=dict(range=[0, 100],
                              gridcolor="rgba(150,180,200,.15)")))
            show(fig, 380, "Ratio health radar")
    with c2:
        section_title("Automated commentary", "Descriptive observations from the supplied dataset.")
        for kind, txt in build_commentary():
            insight(txt, kind)
    section_title("Historical dataset", "Submitted values FY2021–FY2025.")
    st.dataframe(D.style.format("{:,.2f}"), width="stretch")


def page_trends():
    page_header(page)
    picks = st.multiselect("Metrics", list(LBL.values()), default=["NPM (%)", "ROA (%)", "ROE (%)"])
    c1, c2 = st.columns(2)
    norm = c1.toggle("Index to FY2021 = 100", False)
    kind = c2.radio("Chart type", ["Line", "Bar"], horizontal=True, label_visibility="collapsed")
    if not picks:
        st.info("Select at least one metric.")
        return
    X = D[picks].copy()
    if norm:
        X = X.divide(X.iloc[0].replace(0, np.nan)) * 100
    lines(X, picks, "Selected metrics" + (" • Indexed" if norm else ""), 420, bar=(kind == "Bar"))
    if len(picks) > 1:
        cm = X.corr()
        fig = go.Figure(go.Heatmap(z=cm.values, x=cm.columns, y=cm.index, zmin=-1, zmax=1,
                                   colorscale=[[0, "#b83b5e"], [.5, "#10243a"], [1, "#42d392"]],
                                   text=np.round(cm.values, 2), texttemplate="%{text}"))
        show(fig, 420, "Correlation matrix (5 observations — interpret cautiously)")


def page_scorecard():
    page_header(page)
    if SC.empty:
        st.warning("Insufficient ratio data.")
        return
    st.dataframe(style_scorecard(SC), width="stretch", hide_index=True)
    fig = px.bar(SC, x="Ratio", y="Score", color="Score", color_continuous_scale=["#d9534f", "#ffd166", "#42d392"],
                 range_color=[0, 100])
    show(fig, 370, "Educational ratio score")
    st.caption("Benchmarks are generic teaching thresholds, not sector-specific recommendations. "
               "Scores are heuristics, not investment advice.")
    t1, t2, t3 = st.tabs(["💧 Liquidity", "🛡️ Solvency", "⚙️ Efficiency"])
    with t1:
        lines(D, ["Current Ratio", "Quick Ratio"], "Liquidity")
    with t2:
        lines(D, ["Debt/Equity", "Interest Coverage"], "Solvency")
    with t3:
        lines(D, ["Asset Turnover", "Inventory Turnover", "Receivables Turnover"], "Turnover")
        t, pt = vget(company, "receivablesTurn"), clean_number(hist["receivablesTurn"][-2])
        if t > 0 and pt > 0:
            st.metric("Receivable days", f"{365 / t:.0f}", f"{365 / t - 365 / pt:+.0f} vs FY24", delta_color="inverse")


def page_dupont():
    page_header(page)
    st.latex(r"ROE = NPM \times Asset\ Turnover \times Equity\ Multiplier")
    rows = []
    for i, y in enumerate(YEARS):
        npm, at = clean_number(hist["npm"][i]), clean_number(hist["assetTurn"][i])
        roa, roe = clean_number(hist["roa"][i]), clean_number(hist["roe"][i])
        rows.append([y, npm, at, safe_div(roe, roa), npm * at, roa, roe])
    dup = pd.DataFrame(rows, columns=["Year", "NPM (%)", "Asset Turnover", "Equity Multiplier",
                                      "Implied ROA", "Reported ROA", "Reported ROE"]).set_index("Year")
    st.dataframe(dup.style.format("{:.2f}"), width="stretch")
    gap = np.nanmax(np.abs(dup["Implied ROA"].to_numpy() - dup["Reported ROA"].to_numpy()))
    if np.isfinite(gap):
        (st.success if gap < 1 else st.warning)(
            f"Maximum NPM×AT vs reported ROA gap: {gap:.2f} pp."
            + ("" if gap < 1 else " Check asset-basis and averaging conventions."))
    comps = {}
    for name, col in [("Margin", "NPM (%)"), ("Turnover", "Asset Turnover"), ("Leverage", "Equity Multiplier")]:
        a, b = clean_number(dup.iloc[0][col]), clean_number(dup.iloc[-1][col])
        if a > 0 and b > 0:
            comps[name] = math.log(b / a)
    total = sum(comps.values())
    if comps and abs(total) > 1e-9:
        vals = [v / total * 100 for v in comps.values()]
        fig = go.Figure(go.Bar(x=list(comps), y=vals, marker_color=["#5cc8ff", "#42d392", "#9b8cff"][:len(comps)],
                               text=[f"{v:.0f}%" for v in vals], textposition="outside"))
        show(fig, 320, "Share of ROE change FY21→FY25 (log decomposition)")
    lines(dup, ["Reported ROE", "NPM (%)"], "ROE vs margin")


def page_growth():
    page_header(page)
    keys = ["revenue", "netIncome", "eps", "roe", "current"]
    rows = []
    for k in keys:
        s, e = clean_number(hist[k][0]), clean_number(hist[k][-1])
        rows.append([LBL[k], s, e, pct_change(e, s), cagr(s, e)])
    g = pd.DataFrame(rows, columns=["Metric", "FY2021", "FY2025", "Total change (%)", "CAGR (%)"])
    st.dataframe(g.style.format({"FY2021": "{:,.2f}", "FY2025": "{:,.2f}", "Total change (%)": "{:+.1f}",
                                 "CAGR (%)": "{:+.1f}"}), width="stretch", hide_index=True)
    yoy = pd.DataFrame({LBL[k]: [pct_change(hist[k][i], hist[k][i - 1]) for i in range(1, 5)] for k in keys},
                       index=YEARS[1:]).T
    fig = go.Figure(go.Heatmap(z=yoy.values, x=[f"FY{y}" for y in yoy.columns], y=yoy.index,
                               colorscale=[[0, "#d9534f"], [.5, "#10243a"], [1, "#42d392"]], zmid=0,
                               text=np.round(yoy.values, 1), texttemplate="%{text}%"))
    show(fig, 360, "Year-over-year change")


def page_vertical():
    page_header(page)
    vt = company.get("vertical", {})
    if not vt:
        st.info("No common-size data supplied.")
        return
    a, b = st.columns(2)
    for col, keys, color, title in [
        (a, ["Cost of Revenue", "Gross Profit", "Operating Income", "Net Income"], "#5cc8ff", "Income statement (% of revenue)"),
        (b, ["Current Assets", "Net PPE", "Total Liabilities", "Total Equity"], "#42d392", "Balance sheet (% of total)")]:
        ks = [k for k in keys if k in vt]
        with col:
            if ks:
                fig = go.Figure(go.Bar(x=[vt[k] for k in ks], y=ks, orientation="h", marker_color=color,
                                       text=[f"{vt[k]:.1f}%" for k in ks], textposition="outside"))
                fig.update_yaxes(autorange="reversed")
                show(fig, 320, title)
            else:
                st.info("No data.")


def peer_table() -> pd.DataFrame:
    rows = [[s, vget(x, "revenue"), vget(x, "netIncome"), vget(x, "eps"), vget(x, "pe"), vget(x, "current"),
             vget(x, "npm"), vget(x, "roe"), vget(x, "debtEq"),
             cagr(x["historical"]["revenue"][0], x["historical"]["revenue"][-1])] for s, x in ALL.items()]
    return pd.DataFrame(rows, columns=["Company", "Revenue", "PAT", "EPS", "P/E", "Current", "NPM %", "ROE %",
                                       "D/E", "Rev CAGR %"]).set_index("Company")


def page_peers():
    page_header(page)
    peer = peer_table()
    st.dataframe(peer.style.format("{:,.2f}", na_rep="N/A"), width="stretch")
    a, b = st.columns(2)
    with a:
        fig = go.Figure()
        for s, x in ALL.items():
            base = clean_number(x["historical"]["revenue"][0])
            if base > 0:
                fig.add_trace(go.Scatter(x=YEARS, y=np.array(x["historical"]["revenue"], dtype=float) / base * 100,
                                         name=s, mode="lines+markers", line=dict(width=3)))
        fig.update_xaxes(dtick=1)
        show(fig, 370, "Revenue indexed to FY2021 = 100")
    with b:
        cols = ["NPM %", "ROE %", "Current", "Rev CAGR %"]
        mins = peer[cols].min()
        rng = (peer[cols].max() - mins).replace(0, 1)
        norm = ((peer[cols] - mins) / rng).fillna(0)
        fig = go.Figure()
        for s in norm.index:
            v = norm.loc[s].tolist()
            fig.add_trace(go.Scatterpolar(r=v + [v[0]], theta=cols + [cols[0]], name=s, fill="toself", opacity=.45))
        show(fig, 370, "Relative profile (min-max scaled)")
    if len(peer) > 1:
        rank = peer[["NPM %", "ROE %", "Current", "Rev CAGR %"]].rank(ascending=False).mean(axis=1).sort_values()
        st.success(f"Best average rank on margin, ROE, liquidity and growth: **{rank.index[0]}**.")
    st.info("Descriptive comparison only. Accounting basis, business mix, commodity exposure and capital "
            "structure differ across companies.")


def page_pestel():
    page_header(page)
    items = [
        ("Political / Regulatory", "Exploration blocks, permits, fiscal terms, royalties, taxation and policy consistency affect project economics.", "High"),
        ("Economic", "Oil and gas prices, inflation, interest rates, PKR/USD and energy demand influence margins.", "High"),
        ("Social", "Population growth, industrial activity and household energy demand shape consumption.", "Medium"),
        ("Technological", "Seismic imaging, reservoir analytics, automation and extraction technology affect recovery and cost.", "Medium"),
        ("Environmental", "Emission rules, climate policy, water and methane management affect operations.", "Rising"),
        ("Legal / Geopolitical", "Contracts, security conditions, joint ventures and regional instability affect continuity.", "High"),
    ]
    cols = st.columns(3)
    for i, (t, txt, imp) in enumerate(items):
        with cols[i % 3]:
            card(f"{t} · <span style='color:#ffd166'>{imp}</span>", txt, 150)


def page_risk():
    page_header(page)
    st.caption("Transparent educational heuristics based on the supplied dataset.")
    de, cr, ic = vget(company, "debtEq"), vget(company, "current"), vget(company, "interest")
    npm = pd.Series(pd.to_numeric(hist["npm"], errors="coerce"))
    vol = npm.std(ddof=0) / npm.mean() * 100 if npm.mean() else np.nan
    rt = vget(company, "receivablesTurn")
    rd = 365 / rt if rt > 0 else np.nan
    ni = pd.to_numeric(pd.Series(hist["netIncome"]), errors="coerce")
    cur_ni = clean_number(hist["netIncome"][-1])
    dd = (1 - cur_ni / ni.max()) * 100 if ni.max() > 0 and np.isfinite(cur_ni) else np.nan
    vr = vget(company, "revenue")
    gap = abs(clean_number(hist["revenue"][-1]) / vr - 1) * 100 if vr > 0 else np.nan

    def ok(v, f, t):
        return float(np.clip(f(v), 0, 100)) if np.isfinite(v) else np.nan, (t(v) if np.isfinite(v) else "N/A")
    spec = [("Leverage", de, lambda v: v * 50, lambda v: f"D/E {v:.2f}x"),
            ("Liquidity", cr, lambda v: 100 - v * 25, lambda v: f"Current {v:.2f}x"),
            ("Interest cover", ic, lambda v: 100 - v * 8, lambda v: f"{v:.1f}x"),
            ("Margin volatility", vol, lambda v: v * 4, lambda v: f"NPM CV {v:.1f}%"),
            ("Receivables", rd, lambda v: v / 2, lambda v: f"{v:.0f} days"),
            ("Earnings drawdown", dd, lambda v: v * 2, lambda v: f"{v:.1f}%"),
            ("Data reliability", gap, lambda v: v * 3, lambda v: f"Revenue gap {v:.1f}%")]
    rows = [[n, *ok(v, f, t)] for n, v, f, t in spec]
    rdf = pd.DataFrame(rows, columns=["Risk", "Score", "Evidence"])
    rdf["Level"] = pd.cut(rdf["Score"], [-1, 33, 66, 101], labels=["🟢 Low", "🟡 Medium", "🔴 High"])
    overall = rdf["Score"].mean()
    a, b = st.columns([1, 1.5])
    with a:
        gauge(overall, "Composite risk (higher = riskier)", 240)
        st.dataframe(rdf.style.format({"Score": "{:.0f}"}, na_rep="N/A"), width="stretch", hide_index=True)
    with b:
        c = rdf.dropna(subset=["Score"])
        if len(c):
            fig = px.bar(c, x="Score", y="Risk", orientation="h", color="Score",
                         color_continuous_scale=["#42d392", "#ffd166", "#ff6b6b"], range_color=[0, 100])
            fig.update_yaxes(autorange="reversed")
            show(fig, 420, "Risk indicator scores")
    card("Structural E&P risk themes",
         "Commodity price and volume exposure, PKR/USD exposure on imported capex, reserve depletion, "
         "receivables / circular-debt collections, fiscal-policy changes and operational continuity.")
    st.warning("Risk scores are classroom heuristics, not forecasts or investment advice.")


def page_dcf():
    page_header(page)
    st.caption("Illustrative academic valuation model — not investment advice.")
    sh, rev0 = shares(company), vget(company, "revenue")
    pe_price = _pe * _eps if np.isfinite(_pe) and np.isfinite(_eps) else np.nan
    if not (np.isfinite(sh) and sh > 0):
        st.error("DCF needs a positive implied share count (PAT ÷ EPS).")
        return
    if not (np.isfinite(rev0) and rev0 > 0):
        st.error("DCF needs positive FY2025 revenue.")
        return
    d0 = default_dcf(company)
    a, b = st.columns([1, 2])
    with a:
        growth = st.number_input("Revenue growth (%)", value=d0["growth"], step=.5)
        margin = st.number_input("EBIT margin (%)", value=d0["margin"], step=.5)
        tax = st.number_input("Tax rate (%)", value=d0["tax"], min_value=0.0, max_value=100.0, step=1.0)
        capex = st.number_input("Capex (% revenue)", value=d0["capex"], min_value=0.0, step=.5)
        wc = st.number_input("WC drag (% revenue)", value=d0["wc"], min_value=-20.0, step=.5)
        wacc = st.number_input("WACC (%)", value=d0["wacc"], min_value=.1, max_value=100.0, step=.5)
        tg = st.number_input("Terminal growth (%)", value=d0["tg"], min_value=-10.0, max_value=20.0, step=.25)
        nd = st.number_input("Net debt (PKR m)", value=0.0, step=1000.0)
        st.caption(f"Implied shares ≈ {sh:,.0f}m (PAT ÷ EPS)."
                   + (f" P/E-implied price = PKR {pe_price:,.1f}." if np.isfinite(pe_price) else ""))
    if wacc <= tg:
        with b:
            st.error("WACC must exceed terminal growth.")
        return
    try:
        res = dcf(rev0, growth, margin, tax, capex, wc, wacc, tg, nd, sh)
    except Exception as exc:
        with b:
            st.error(f"DCF calculation failed: {exc}")
        return
    with b:
        k = st.columns(3)
        k[0].metric("Enterprise value", f"{fmt(res['ev'])}m")
        k[1].metric("Model value / share", f"PKR {res['ps']:,.1f}")
        if np.isfinite(pe_price) and pe_price != 0:
            k[2].metric("Vs P/E-implied price", f"{(res['ps'] / pe_price - 1) * 100:+.1f}%")
        else:
            k[2].metric("Vs P/E-implied price", "N/A")
        wf = go.Figure(go.Waterfall(
            x=["PV explicit FCF", "PV terminal", "Net debt", "Equity value"],
            measure=["relative", "relative", "relative", "total"],
            y=[res["pv"], res["pvtv"], -nd, 0],
            connector=dict(line=dict(color="#35556d")),
            increasing=dict(marker=dict(color="#42d392")), decreasing=dict(marker=dict(color="#ff6b6b")),
            totals=dict(marker=dict(color="#5cc8ff"))))
        show(wf, 320, "Value bridge (PKR m)")
        ts = safe_div(res["pvtv"], res["ev"]) * 100
        if np.isfinite(ts):
            (st.warning if ts > 75 else st.caption)(f"Terminal value contributes ≈ {ts:.0f}% of EV.")
    fdf = pd.DataFrame(res["rows"], columns=["Year", "Revenue", "EBIT", "FCF", "Discounted FCF"])
    fdf["Year"] = [f"FY{2025 + int(t)}E" for t in fdf["Year"]]
    st.dataframe(fdf.style.format({c: "{:,.0f}" for c in fdf.columns if c != "Year"}), width="stretch", hide_index=True)

    t1, t2, t3 = st.tabs(["🎯 Sensitivity", "🌪️ Tornado", "🎲 Monte Carlo"])
    with t1:
        ws = np.arange(wacc - 3, wacc + 3.1, 1.0)
        gs = np.arange(max(-5, tg - 2), tg + 2.1, 1.0)
        Z = [[dcf(rev0, growth, margin, tax, capex, wc, w, g, nd, sh)["ps"] if w > g else np.nan for w in ws] for g in gs]
        Z = np.array(Z, dtype=float)
        txt = [["" if not np.isfinite(v) else f"{v:,.0f}" for v in r] for r in Z]
        fig = go.Figure(go.Heatmap(z=Z, x=[f"{w:.1f}%" for w in ws], y=[f"{g:.1f}%" for g in gs],
                                   colorscale=[[0, "#ff6b6b"], [.5, "#ffd166"], [1, "#42d392"]],
                                   text=txt, texttemplate="%{text}"))
        fig.update_xaxes(title="WACC"); fig.update_yaxes(title="Terminal growth")
        show(fig, 380, "Value per share (PKR)")
    with t2:
        base = res["ps"]
        shocks = {"WACC ±2pp": ("wacc", 2), "Growth ±3pp": ("growth", 3), "EBIT margin ±4pp": ("margin", 4),
                  "Capex ±3pp": ("capex", 3), "Terminal g ±1pp": ("tg", 1)}
        p0 = dict(growth=growth, margin=margin, tax=tax, capex=capex, wc=wc, wacc=wacc, tg=tg)
        rows = []
        for name, (key, d) in shocks.items():
            vs = []
            for sgn in (-1, 1):
                p = dict(p0); p[key] += sgn * d
                try:
                    vs.append(dcf(rev0, p["growth"], p["margin"], p["tax"], p["capex"], p["wc"], p["wacc"], p["tg"], nd, sh)["ps"])
                except Exception:
                    vs.append(np.nan)
            rows.append((name, np.nanmin(vs) - base, np.nanmax(vs) - base))
        rows.sort(key=lambda r: abs(r[2] - r[1]))
        fig = go.Figure()
        fig.add_trace(go.Bar(y=[r[0] for r in rows], x=[r[1] for r in rows], orientation="h", name="Downside", marker_color="#ff6b6b"))
        fig.add_trace(go.Bar(y=[r[0] for r in rows], x=[r[2] for r in rows], orientation="h", name="Upside", marker_color="#42d392"))
        fig.update_layout(barmode="relative")
        show(fig, 340, f"Change in value/share vs base (PKR {base:,.1f})")
    with t3:
        n = st.slider("Simulations", 500, 5000, 2000, 500)
        rng = np.random.default_rng(42)
        out = []
        for _ in range(n):
            w, g2 = rng.normal(wacc, 1.5), rng.normal(tg, .75)
            gr, mg = rng.normal(growth, 3), rng.normal(margin, 4)
            if w - g2 <= 2:
                continue
            try:
                v = dcf(rev0, gr, mg, tax, capex, wc, w, g2, nd, sh)["ps"]
                if np.isfinite(v):
                    out.append(v)
            except Exception:
                continue
        out = np.asarray(out, dtype=float)
        if len(out) < 10:
            st.warning("Too few valid simulations. Adjust WACC or terminal growth.")
        else:
            p5, med, p95 = np.percentile(out, [5, 50, 95])
            fig = go.Figure(go.Histogram(x=out, nbinsx=50, marker_color="#5cc8ff", opacity=.85))
            fig.add_vline(x=med, line_color="#42d392", line_dash="dash", annotation_text="Median")
            if np.isfinite(pe_price):
                fig.add_vline(x=pe_price, line_color="#ffd166", line_width=2, annotation_text="P/E implied")
            show(fig, 360, "Distribution of model value per share")
            m = st.columns(4)
            m[0].metric("P5", f"{p5:,.0f}"); m[1].metric("Median", f"{med:,.0f}"); m[2].metric("P95", f"{p95:,.0f}")
            m[3].metric("P(value > P/E price)", f"{np.mean(out > pe_price) * 100:.0f}%" if np.isfinite(pe_price) else "N/A")


def page_relative():
    page_header(page)
    rows = []
    for s, x in ALL.items():
        pe, eps = vget(x, "pe"), vget(x, "eps")
        rows.append([s, pe, eps, pe * eps if np.isfinite(pe) and np.isfinite(eps) else np.nan,
                     vget(x, "dividendYield"), vget(x, "roe")])
    rel = pd.DataFrame(rows, columns=["Company", "P/E", "EPS", "P/E implied price", "Div yield %", "ROE %"]).set_index("Company")
    st.dataframe(rel.style.format("{:,.2f}", na_rep="N/A"), width="stretch")
    sd = rel.reset_index().dropna(subset=["ROE %", "P/E"])
    if len(sd):
        sd["Div yield %"] = sd["Div yield %"].fillna(0).clip(lower=.1)
        fig = px.scatter(sd, x="ROE %", y="P/E", size="Div yield %", text="Company", size_max=40)
        fig.update_traces(textposition="top center", marker=dict(color="#5cc8ff", line=dict(color="#d8f3ff", width=1)))
        show(fig, 390, "P/E vs ROE (bubble = dividend yield)")
    pes = pd.to_numeric(rel["P/E"], errors="coerce").dropna()
    if len(pes) and np.isfinite(_eps):
        med = pes.median()
        pe_own = _pe * _eps if np.isfinite(_pe) else np.nan
        dcf_v = base_dcf_value(company)
        items = [("Own P/E × EPS", pe_own), ("Peer-median P/E × EPS", med * _eps), ("DCF (default assumptions)", dcf_v)]
        items = [(n, v) for n, v in items if np.isfinite(v)]
        fig = go.Figure(go.Bar(x=[v for _, v in items], y=[n for n, _ in items], orientation="h",
                               marker_color=PALETTE[:len(items)], text=[f"{v:,.0f}" for _, v in items],
                               textposition="outside"))
        fig.update_yaxes(autorange="reversed")
        show(fig, 300, f"Indicative value per share — {sel} (PKR)")
        st.info(f"Peer median P/E = {med:.2f}x. Mechanical multiples ignore growth, risk, accounting basis and "
                "business mix — treat as a descriptive exercise.")


def page_scenarios():
    page_header(page)
    st.caption("Scenario labels describe model assumptions only; they are not predictions.")
    a, b, d, e = st.columns(4)
    bg = a.number_input("Base growth (%)", value=6.0, step=.5)
    bm = b.number_input("Base net margin (%)", value=float(clean_number(hist["npm"][-1], 10)), step=.5)
    shock = d.number_input("Shock (%)", value=10.0, min_value=0.0, step=.5)
    hz = e.slider("Horizon (years)", 1, 5, 3)
    sh = shares(company)
    if not (np.isfinite(sh) and sh > 0):
        st.error("Scenario analysis needs a positive implied share count.")
        return
    cases = {"Bear": (bg - shock, max(1, bm - shock / 2)), "Base": (bg, bm), "Bull": (bg + shock, bm + shock / 2)}
    colors = {"Bear": "#ff6b6b", "Base": "#5cc8ff", "Bull": "#42d392"}
    base_rev = vget(company, "revenue")
    fig, cols, summary = go.Figure(), st.columns(3), []
    for col, (name, (g, m)) in zip(cols, cases.items()):
        path = [base_rev * (1 + g / 100) ** t for t in range(hz + 1)]
        profit = path[-1] * m / 100
        eps = profit / sh
        fig.add_trace(go.Scatter(x=[f"FY{2025 + t}" for t in range(hz + 1)], y=path, name=name, mode="lines+markers",
                                 line=dict(color=colors[name], width=3)))
        summary.append([name, g, m, path[-1], profit, eps])
        with col:
            card(name, f"Growth {g:.1f}% • Margin {m:.1f}%")
            st.metric(f"Revenue FY{2025 + hz}", f"{fmt(path[-1])}m")
            st.metric("Profit", f"{fmt(profit)}m")
            dl = pct_change(eps, _eps) if np.isfinite(_eps) else np.nan
            st.metric("EPS", f"PKR {eps:,.2f}", f"{dl:+.1f}% vs FY25" if np.isfinite(dl) else None)
    show(fig, 360, "Revenue scenario paths (PKR m)")
    with st.expander("Scenario table"):
        st.dataframe(pd.DataFrame(summary, columns=["Case", "Growth %", "Margin %", "Revenue", "Profit", "EPS"])
                     .style.format({"Growth %": "{:.1f}", "Margin %": "{:.1f}", "Revenue": "{:,.0f}",
                                    "Profit": "{:,.0f}", "EPS": "{:,.2f}"}), width="stretch", hide_index=True)


def page_integrity():
    page_header(page)
    rows = []
    for s, x in DEMO.items():
        for k, lab in [("revenue", "Revenue"), ("netIncome", "PAT"), ("eps", "EPS"), ("pe", "P/E"),
                       ("current", "Current ratio"), ("roe", "ROE")]:
            if k not in x.get("verified2025", {}):
                continue
            sub, ver = clean_number(x["historical"][k][-1]), clean_number(x["verified2025"][k])
            var = (sub / ver - 1) * 100 if ver != 0 else np.nan
            st_ = "⚪ N/A" if not np.isfinite(var) else "✅ Verified" if abs(var) < .5 else "🟡 Minor" if abs(var) < 5 else "🔴 Major"
            rows.append([s, lab, sub, ver, var, st_])
    ig = pd.DataFrame(rows, columns=["Company", "Metric", "Submitted", "Verified", "Variance %", "Status"])
    st.dataframe(ig.style.format({"Submitted": "{:,.2f}", "Verified": "{:,.2f}", "Variance %": "{:+.2f}"}),
                 width="stretch", hide_index=True)
    if len(ig):
        show(px.bar(ig, x="Metric", y="Variance %", color="Company", barmode="group"), 340, "Submitted vs verified variance")
    section_title("Internal consistency", "Selected company — reported NPM vs NI / Revenue.")
    rows = []
    for i, y in enumerate(YEARS):
        rev, ni, npm = clean_number(hist["revenue"][i]), clean_number(hist["netIncome"][i]), clean_number(hist["npm"][i])
        imp = ni / rev * 100 if rev != 0 else np.nan
        rows.append([y, npm, imp, npm - imp if np.isfinite(npm) and np.isfinite(imp) else np.nan])
    cdf = pd.DataFrame(rows, columns=["Year", "Reported NPM", "NI / Revenue", "Gap (pp)"])
    st.dataframe(cdf.style.format({c: "{:.2f}" for c in cdf.columns if c != "Year"}), width="stretch", hide_index=True)
    st.info("Recommended source priority: audited issuer annual report → PSX issuer page → licensed data provider. "
            "The demo dataset is not a live market feed.")


def build_report() -> str:
    L = [f"# {sel} — {company['name']}", f"_Generated {datetime.now():%Y-%m-%d %H:%M} • PSX Financial Analysis Lab_", "",
         "## Key figures (FY2025)",
         f"- Revenue: PKR {fmt(vget(company, 'revenue'))}m", f"- PAT: PKR {fmt(vget(company, 'netIncome'))}m",
         f"- EPS: {fmt(_eps, 2)} | P/E: {fmt(_pe, 2)}x | ROE: {fmt(_roe, 1)}%",
         f"- Ratio health: {fmt(HEALTH)}/100 ({light(HEALTH)})", "", "## Commentary"]
    import re
    L += [f"- {re.sub('<[^>]+>', '', t)}" for _, t in build_commentary()]
    L += ["", "## Scorecard", SC.to_markdown(index=False) if hasattr(SC, "to_markdown") and _has_tabulate() else SC.to_string(index=False),
          "", "_Educational output — not investment advice._"]
    return "\n".join(L)


def _has_tabulate() -> bool:
    try:
        import tabulate  # noqa: F401
        return True
    except Exception:
        return False


def excel_bytes() -> Optional[bytes]:
    try:
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="openpyxl") as w:
            D.to_excel(w, sheet_name="Historical")
            SC.to_excel(w, sheet_name="Scorecard", index=False)
            peer_table().to_excel(w, sheet_name="Peers")
        return buf.getvalue()
    except Exception:
        return None


def page_io():
    page_header(page)
    card("JSON import", "Upload a JSON company record or edit the template. All 15 metrics need exactly five values "
                        "ordered FY2021 → FY2025.")
    template = {"symbol": "NEWCO", "name": "Example Company", "years": YEARS, **{k: [1, 2, 3, 4, 5] for k in HK},
                "source": "Source / URL"}
    template.update(
        revenue=[100, 110, 120, 130, 140], netIncome=[10, 12, 14, 15, 16], npm=[10, 10.91, 11.67, 11.54, 11.43],
        roa=[5, 5.5, 6, 6.2, 6.5], roe=[8, 9, 10, 10.5, 11], current=[2, 2.1, 2.2, 2.3, 2.4],
        quick=[1.8, 1.9, 2, 2.1, 2.2], debtEq=[.5, .48, .45, .42, .4], interest=[4, 4.5, 5, 5.2, 5.5],
        assetTurn=[.5, .52, .54, .56, .58], inventoryTurn=[5, 5.2, 5.4, 5.6, 5.8],
        receivablesTurn=[4, 4.1, 4.2, 4.3, 4.4], pe=[10, 9.5, 9, 8.5, 8], eps=[2, 2.4, 2.8, 3, 3.2],
        dividendYield=[2, 2.2, 2.4, 2.5, 2.6])
    up = st.file_uploader("Upload JSON", type=["json"], key="company_json_upload")
    if up is not None:
        try:
            raw = up.getvalue().decode("utf-8")
        except Exception:
            raw = ""
            st.error("Could not decode the file as UTF-8.")
    else:
        raw = st.text_area("Or paste JSON", json.dumps(template, indent=2), height=430)
    if st.button("Validate & Add Company", type="primary", key="add_company"):
        try:
            p = json.loads(raw)
            if not isinstance(p, dict):
                raise ValueError("Top-level JSON must be an object.")
            miss = sorted(set(template) - set(p))
            if miss:
                raise ValueError("Missing fields: " + ", ".join(miss))
            if p["years"] != YEARS:
                raise ValueError(f"years must equal {YEARS}.")
            if any(not isinstance(p[k], list) or len(p[k]) != 5 for k in HK):
                raise ValueError("Every metric must contain exactly 5 values.")
            sym, name = str(p["symbol"]).strip().upper(), str(p["name"]).strip()
            if not sym or not name:
                raise ValueError("symbol and name cannot be empty.")
            nd = {k: [clean_number(v) for v in p[k]] for k in HK}
            bad = [k for k in HK if any(not np.isfinite(v) for v in nd[k])]
            if bad:
                raise ValueError(f"Invalid values in: {', '.join(bad)}")
            gaps = [abs(nd["netIncome"][i] / nd["revenue"][i] * 100 - nd["npm"][i])
                    for i in range(5) if nd["revenue"][i] != 0]
            if gaps and max(gaps) > 2:
                st.warning("NPM differs from NI/Revenue by more than 2 pp in at least one year.")
            src = str(p.get("source", "User supplied")).strip()
            cc = mk(name, "User-imported company.", [nd[k] for k in HK],
                    {k: nd[k][-1] for k in ("revenue", "netIncome", "eps", "pe")}, None, None,
                    [(src, src if src.startswith("http") else "")])
            ok, why = validate_company_structure(cc)
            if not ok:
                raise ValueError(why)
            st.session_state.custom[sym] = cc
            st.success(f"{sym} added. Use the sidebar selector to load it.")
        except json.JSONDecodeError as exc:
            st.error(f"Invalid JSON: {exc}")
        except Exception as exc:
            st.error(f"Could not import company: {exc}")
    divider()
    section_title("Export", "Download the active company's dataset and analysis outputs.")
    c = st.columns(4)
    c[0].download_button("⬇ Dataset CSV", D.to_csv().encode("utf-8"), f"{sel}_dataset.csv", "text/csv", key="dl1")
    c[1].download_button("⬇ Scorecard CSV", SC.to_csv(index=False).encode("utf-8"), f"{sel}_scorecard.csv",
                         "text/csv", key="dl2")
    c[2].download_button("⬇ Company JSON", json.dumps(
        {"symbol": sel, "name": company["name"], "years": YEARS, **{k: hist[k] for k in HK},
         "verified2025": company.get("verified2025", {}), "vertical": company.get("vertical", {}),
         "sources": company.get("sources", [])}, indent=2).encode("utf-8"), f"{sel}_company.json",
        "application/json", key="dl3")
    c[3].download_button("⬇ Report (.md)", build_report().encode("utf-8"), f"{sel}_report.md", "text/markdown", key="dl4")
    xb = excel_bytes()
    if xb:
        st.download_button("⬇ Excel workbook (Historical / Scorecard / Peers)", xb, f"{sel}_analysis.xlsx",
                           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="dl5")
    section_title("Current imported companies")
    if st.session_state.custom:
        st.dataframe(pd.DataFrame([{"Symbol": s, "Company": x["name"],
                                    "Source": x["sources"][0][0] if x.get("sources") else "N/A"}
                                   for s, x in st.session_state.custom.items()]), width="stretch", hide_index=True)
        if st.button("Remove all imported companies", key="clear_custom"):
            st.session_state.custom = {}
            st.rerun()
    else:
        st.info("No custom companies imported in this session.")


def page_refs():
    page_header(page)
    srcs = company.get("sources", [])
    if not srcs:
        st.info("No references supplied.")
    for title, url in srcs:
        u = str(url).strip()
        link = (f'<a href="{u}" target="_blank" rel="noopener noreferrer" style="color:#5cc8ff!important;'
                f'font-size:.82rem;word-break:break-all">{u}</a>') if u.startswith(("http://", "https://")) else ""
        st.markdown(f'<div class="card"><div class="card-title">{title}</div>{link}</div>', unsafe_allow_html=True)
    section_title("Recommended production architecture")
    st.code("Streamlit UI\n    ↓\nAuthorized backend / data adapter\n    ↓\n"
            "PSX feed | annual-report parser | cached dataset\n    ↓\nNormalization + source metadata\n    ↓\n"
            "Financial ratio engine\n    ↓\nCharts / valuation / scenarios / exports", language="text")
    st.warning("Never place data-provider credentials, API keys or tokens in frontend code or a public repository.")


ROUTES = {
    "Executive Dashboard": page_executive, "Trends Explorer": page_trends, "Ratio Scorecard": page_scorecard,
    "DuPont Analysis": page_dupont, "Growth Analysis": page_growth, "Vertical Analysis": page_vertical,
    "Peer Comparison": page_peers, "Industry / PESTEL": page_pestel, "Risk Dashboard": page_risk,
    "DCF & Monte Carlo": page_dcf, "Relative Valuation": page_relative, "Scenario Analysis": page_scenarios,
    "Data Integrity": page_integrity, "Import & Export": page_io, "References": page_refs,
}

try:
    ROUTES[page]()
except Exception as exc:  # keep the shell alive if one module fails
    st.error(f"This module hit an unexpected error: {exc}")

st.markdown("""
<div class="footer"><b style="color:#7fa4bc!important">COMSATS University Islamabad</b>
• Business Finance • Instructor: Miss Sania Khalid • Student: Muhammad Abubakar<br><br>
PSX Financial Analysis Lab • FY2021–FY2025 • Academic / illustrative use</div>
""", unsafe_allow_html=True)
