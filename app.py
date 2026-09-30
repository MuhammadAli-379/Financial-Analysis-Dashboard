# -*- coding: utf-8 -*-
"""
PSX Financial Analysis Lab — COMSATS University Islamabad
Run:  streamlit run app.py      (keep .streamlit/config.toml next to this file)
"""

from __future__ import annotations

import io
import json
import math
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="PSX Financial Analysis Lab", page_icon="📊",
                   layout="wide", initial_sidebar_state="expanded")

# ============================================================
# DESIGN SYSTEM — flat, light, one accent, no effects
# ============================================================

CSS = """
:root{--bg:#F5F6F8;--surface:#fff;--line:#E2E5EA;--text:#18212F;--muted:#667085;
--accent:#1F4FD8;--pos:#0E8A5F;--neg:#C43D3D;--warn:#B7791F}
html,body,.stApp{background:var(--bg);color:var(--text);
 font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,"Helvetica Neue",Arial,sans-serif}
.block-container{max-width:1440px;padding:1.2rem 2rem 3rem}
[data-testid="stHeader"]{background:transparent}
#MainMenu,footer{visibility:hidden}
[data-testid="stSidebar"]{background:#fff;border-right:1px solid var(--line)}
[data-testid="stSidebar"] .block-container{padding:1rem}
h1,h2,h3{letter-spacing:-.01em}

/* top bar */
.brand{display:flex;align-items:center;gap:10px;padding-top:.35rem}
.brand-mark{width:30px;height:30px;border-radius:6px;background:var(--accent);color:#fff;
 display:flex;align-items:center;justify-content:center;font-weight:700;font-size:.8rem}
.brand-name{font-weight:650;font-size:.98rem;line-height:1.1}
.brand-sub{color:var(--muted);font-size:.72rem}

/* page header */
.ph{margin:.9rem 0 1.1rem;padding-bottom:.9rem;border-bottom:1px solid var(--line)}
.ph-ctx{display:flex;align-items:center;gap:8px;color:var(--muted);font-size:.78rem;margin-bottom:.35rem}
.tick{background:#E8EEFC;color:var(--accent);font-weight:700;padding:1px 8px;border-radius:4px;font-size:.74rem}
.ph h1{font-size:1.65rem;font-weight:650;margin:0;padding:0;line-height:1.2}
.ph p{color:var(--muted);font-size:.9rem;margin:.25rem 0 0}

/* panels */
.panel{background:var(--surface);border:1px solid var(--line);border-radius:8px;padding:16px 18px;margin-bottom:12px}
.label{color:var(--muted);font-size:.7rem;font-weight:600;letter-spacing:.06em;text-transform:uppercase;margin-bottom:6px}
.body{color:#344054;font-size:.86rem;line-height:1.55}
.h3{font-size:.98rem;font-weight:650;margin:1.1rem 0 .5rem}
.sub{color:var(--muted);font-size:.8rem;margin:-.35rem 0 .6rem}

/* metrics */
[data-testid="stMetric"]{background:var(--surface);border:1px solid var(--line);border-radius:8px;padding:12px 16px}
[data-testid="stMetricLabel"] p{color:var(--muted)!important;font-size:.72rem!important;font-weight:600;
 text-transform:uppercase;letter-spacing:.05em}
[data-testid="stMetricValue"]{font-size:1.45rem!important;font-weight:650!important;font-variant-numeric:tabular-nums}

/* rows */
.ins{display:flex;gap:10px;align-items:flex-start;padding:9px 0;border-bottom:1px solid #EEF0F3;
 font-size:.87rem;color:#344054}
.ins:last-child{border-bottom:none}
.dot{width:8px;height:8px;border-radius:50%;margin-top:.42rem;flex:none;background:#98A2B3}
.dot.good{background:var(--pos)}.dot.warn{background:var(--warn)}.dot.bad{background:var(--neg)}
.badge{display:inline-block;padding:1px 8px;border-radius:4px;font-size:.72rem;font-weight:600}
.b-good{background:#E6F4EE;color:var(--pos)}.b-warn{background:#FBF1DD;color:var(--warn)}
.b-bad{background:#FBE8E8;color:var(--neg)}.b-neu{background:#EEF0F3;color:#475467}

/* widgets */
[data-testid="stDataFrame"],[data-testid="stPlotlyChart"]{border:1px solid var(--line);border-radius:8px;
 overflow:hidden;background:var(--surface)}
[data-testid="stPlotlyChart"]{padding:6px}
[data-testid="stAlert"]{border-radius:8px}
[data-testid="stExpander"]{border:1px solid var(--line);border-radius:8px;background:var(--surface)}
.stButton>button,.stDownloadButton>button{border-radius:6px;font-weight:550}
.footer{color:#98A2B3;font-size:.72rem;text-align:center;margin-top:2.5rem;padding-top:1rem;
 border-top:1px solid var(--line)}
@media(max-width:900px){.block-container{padding:1rem}.ph h1{font-size:1.35rem}}
"""
st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)

FONT = "-apple-system,Segoe UI,Inter,Roboto,Arial,sans-serif"
PALETTE = ["#1F4FD8", "#0E8A5F", "#B7791F", "#5B6B85", "#C43D3D", "#7C93C9"]
C_POS, C_NEG, C_WARN, C_ACC = "#0E8A5F", "#C43D3D", "#B7791F", "#1F4FD8"
DIVERGE = [[0, C_NEG], [.5, "#FFFFFF"], [1, C_POS]]

# ============================================================
# CONSTANTS
# ============================================================

YEARS = [2021, 2022, 2023, 2024, 2025]
HK = ["revenue", "netIncome", "npm", "roa", "roe", "current", "quick", "debtEq", "interest",
      "assetTurn", "inventoryTurn", "receivablesTurn", "pe", "eps", "dividendYield"]
LBL = dict(zip(HK, ["Revenue (PKR m)", "Net Income (PKR m)", "NPM (%)", "ROA (%)", "ROE (%)",
                    "Current Ratio", "Quick Ratio", "Debt/Equity", "Interest Coverage", "Asset Turnover",
                    "Inventory Turnover", "Receivables Turnover", "P/E", "EPS", "Dividend Yield (%)"]))
RULES = {"current": (1.5, "hi"), "quick": (1.0, "hi"), "debtEq": (1.0, "lo"), "interest": (3.0, "hi"),
         "npm": (10.0, "hi"), "roa": (5.0, "hi"), "roe": (12.0, "hi"), "assetTurn": (0.3, "hi"),
         "receivablesTurn": (4.0, "hi")}

# ============================================================
# HELPERS
# ============================================================


def clean_number(v: Any, default: float = np.nan) -> float:
    if v is None or isinstance(v, bool):
        return default
    try:
        if isinstance(v, str):
            v = v.replace(",", "").replace("%", "").strip()
        r = float(v)
        return r if np.isfinite(r) else default
    except Exception:
        return default


def safe_div(a: Any, b: Any, default: float = np.nan) -> float:
    a, b = clean_number(a), clean_number(b)
    return default if not (np.isfinite(a) and np.isfinite(b)) or b == 0 else a / b


def fmt(x: Any, d: int = 0) -> str:
    x = clean_number(x)
    return "N/A" if not np.isfinite(x) else f"{x:,.{d}f}"


def pct_change(new: Any, old: Any) -> float:
    new, old = clean_number(new), clean_number(old)
    return np.nan if not (np.isfinite(new) and np.isfinite(old)) or old == 0 else (new / old - 1) * 100


def cagr(a: Any, b: Any, n: int = 4) -> float:
    a, b = clean_number(a), clean_number(b)
    if not (np.isfinite(a) and np.isfinite(b)) or a <= 0 or b <= 0 or n <= 0:
        return np.nan
    return ((b / a) ** (1 / n) - 1) * 100


def safe_mean(v: Any) -> float:
    arr = pd.to_numeric(pd.Series(v), errors="coerce").to_numpy(dtype=float)
    return float(np.nanmean(arr)) if np.isfinite(arr).any() else np.nan


def light(s: float) -> str:
    s = clean_number(s)
    return "N/A" if not np.isfinite(s) else "Strong" if s >= 70 else "Watch" if s >= 45 else "Weak"


def badge(text: str) -> str:
    cls = {"Strong": "good", "Low": "good", "Verified": "good", "Watch": "warn", "Medium": "warn",
           "Minor": "warn", "Weak": "bad", "High": "bad", "Major": "bad"}.get(text, "neu")
    return f'<span class="badge b-{cls}">{text}</span>'


def mk(name, desc, rows, ver, vert, src) -> Dict[str, Any]:
    return {"name": name, "description": desc, "historical": dict(zip(HK, rows)),
            "verified2025": ver or {}, "vertical": vert or {}, "sources": src}


def validate_company_structure(c: Dict[str, Any]) -> Tuple[bool, str]:
    if not isinstance(c, dict):
        return False, "Company record must be an object."
    miss = {"name", "historical", "verified2025", "vertical", "sources"} - set(c)
    if miss:
        return False, "Missing fields: " + ", ".join(sorted(miss))
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
    d = {"Year": YEARS}
    for k in HK:
        d[LBL[k]] = pd.to_numeric(pd.Series(c["historical"][k]), errors="coerce").to_numpy()
    return pd.DataFrame(d).set_index("Year")


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


# ---------- UI helpers ----------


def header(title: str, desc: str):
    st.markdown(f'<div class="ph"><div class="ph-ctx"><span class="tick">{sel}</span>'
                f'<span>{company["name"]}</span><span>·</span><span>FY2021–FY2025 · PKR millions</span></div>'
                f'<h1>{title}</h1><p>{desc}</p></div>', unsafe_allow_html=True)


def h3(title: str, sub: str = ""):
    st.markdown(f'<div class="h3">{title}</div>' + (f'<div class="sub">{sub}</div>' if sub else ""),
                unsafe_allow_html=True)


def panel(label: str, body: str, min_h: int = 0):
    st.markdown(f'<div class="panel" style="min-height:{min_h}px"><div class="label">{label}</div>'
                f'<div class="body">{body}</div></div>', unsafe_allow_html=True)


def insights(items: List[Tuple[str, str]]):
    html = "".join(f'<div class="ins"><span class="dot {k}"></span><span>{t}</span></div>' for k, t in items)
    st.markdown(f'<div class="panel">{html}</div>', unsafe_allow_html=True)


def switch(options: List[str], key: str) -> str:
    """Segmented control: only the chosen view is computed (keeps pages fast)."""
    v = st.segmented_control("View", options, default=options[0], key=key, label_visibility="collapsed")
    return v or options[0]


_n = [0]


def show(fig: go.Figure, height: int = 360, title: Optional[str] = None):
    fig.update_layout(
        template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=height,
        margin=dict(l=8, r=8, t=46 if title else 14, b=8), colorway=PALETTE,
        font=dict(family=FONT, size=12, color="#344054"),
        title=dict(text=title, x=0, xanchor="left", font=dict(size=13.5, color="#18212F")) if title else None,
        legend=dict(orientation="h", y=1.12, x=0, font=dict(size=11)),
        hoverlabel=dict(bgcolor="#fff", bordercolor="#D0D5DD", font=dict(color="#18212F", size=12)))
    fig.update_xaxes(gridcolor="#EEF0F3", linecolor="#D0D5DD", zeroline=False)
    fig.update_yaxes(gridcolor="#EEF0F3", linecolor="#D0D5DD", zeroline=False)
    _n[0] += 1
    st.plotly_chart(fig, width="stretch", key=f"pc{_n[0]}", config={"displaylogo": False, "displayModeBar": False})


def lines(df: pd.DataFrame, cols: List[str], title: str, height: int = 360, bar: bool = False):
    fig = go.Figure()
    for i, c in enumerate(cols):
        if c not in df.columns:
            continue
        y, col = pd.to_numeric(df[c], errors="coerce"), PALETTE[i % len(PALETTE)]
        if bar:
            fig.add_trace(go.Bar(x=df.index, y=y, name=c, marker_color=col))
        else:
            fig.add_trace(go.Scatter(x=df.index, y=y, name=c, mode="lines+markers",
                                     line=dict(width=2.5, color=col), marker=dict(size=6)))
    if not fig.data:
        st.info("No valid data available for this chart.")
        return
    if bar:
        fig.update_layout(barmode="group")
    fig.update_xaxes(dtick=1)
    show(fig, height, title)


# ============================================================
# VALUATION ENGINE (vectorised)
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
    return {"rows": rows, "pv": pv, "tv": tv, "pvtv": pvtv, "ev": ev, "eq": ev - net_debt, "ps": (ev - net_debt) / sh}


def dcf_vec(rev0, g, m, tax, capex, wc, w, tg, nd, sh, years: int = 5):
    """Value/share for arrays of (g, m, w, tg) — replaces slow Python loops."""
    g, m, w, tg = np.broadcast_arrays(*[np.asarray(a, dtype=float) for a in (g, m, w, tg)])
    t = np.arange(1, years + 1).reshape((-1,) + (1,) * g.ndim)
    rev = rev0 * (1 + g / 100) ** t
    fcf = rev * m / 100 * (1 - tax / 100) - rev * (capex + wc) / 100
    pv = (fcf / (1 + w / 100) ** t).sum(axis=0)
    with np.errstate(divide="ignore", invalid="ignore"):
        tv = fcf[-1] * (1 + tg / 100) / ((w - tg) / 100)
        out = (pv + tv / (1 + w / 100) ** years - nd) / sh
    return np.where(w > tg, out, np.nan)


@st.cache_data(show_spinner=False)
def run_mc(rev0, growth, margin, tax, capex, wc, wacc, tg, nd, sh, n) -> np.ndarray:
    r = np.random.default_rng(42)
    w, g2 = r.normal(wacc, 1.5, n), r.normal(tg, .75, n)
    gr, mg = r.normal(growth, 3, n), r.normal(margin, 4, n)
    v = dcf_vec(rev0, gr, mg, tax, capex, wc, w, g2, nd, sh)
    v = np.where(w - g2 > 2, v, np.nan)
    return v[np.isfinite(v)]


def default_dcf(c: Dict[str, Any]) -> Dict[str, float]:
    g = cagr(c["historical"]["revenue"][0], c["historical"]["revenue"][-1])
    g = float(np.clip(g if np.isfinite(g) else 5.0, 0, 20))
    m = clean_number(c.get("vertical", {}).get("Operating Income", 35.0), 35.0)
    return dict(growth=g, margin=float(np.clip(m, 1, 80)), tax=39.0, capex=8.0, wc=2.0, wacc=14.0, tg=3.0, net_debt=0.0)


def base_dcf_value(c: Dict[str, Any]) -> float:
    sh, rev0 = shares(c), vget(c, "revenue")
    if not (np.isfinite(sh) and sh > 0 and np.isfinite(rev0) and rev0 > 0):
        return np.nan
    p = default_dcf(c)
    try:
        return dcf(rev0, p["growth"], p["margin"], p["tax"], p["capex"], p["wc"], p["wacc"], p["tg"], p["net_debt"], sh)["ps"]
    except Exception:
        return np.nan


# ============================================================
# DEMO DATA
# ============================================================

DEMO = {
    "OGDC": mk("Oil & Gas Development Company Limited",
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
    "PPL": mk("Pakistan Petroleum Limited", "Major Pakistani exploration and production company.",
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
    "MARI": mk("Mari Energies Limited", "Pakistani E&P company formerly Mari Petroleum Company Limited.",
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
# DATASET + TOP BAR
# ============================================================

st.session_state.setdefault("custom", {})
ALL: Dict[str, Dict[str, Any]] = {}
for _s, _c in {**DEMO, **st.session_state.custom}.items():
    _ok, _why = validate_company_structure(_c)
    if _ok:
        ALL[_s] = _c
    else:
        st.warning(f"Skipping invalid company **{_s}**: {_why}")
if not ALL:
    st.error("No valid company data is available.")
    st.stop()

_l, _r = st.columns([3, 1.3], vertical_alignment="center")
with _l:
    st.markdown('<div class="brand"><div class="brand-mark">PSX</div><div><div class="brand-name">'
                'Financial Analysis Lab</div><div class="brand-sub">COMSATS University Islamabad · '
                'Department of Management Sciences</div></div></div>', unsafe_allow_html=True)
with _r:
    sel = st.selectbox("Company", list(ALL), format_func=lambda x: f"{x} — {ALL[x]['name']}",
                       label_visibility="collapsed", key="company_select")

company = ALL[sel]
hist = company["historical"]
D = hdf(company)
SC = scorecard(company)
HEALTH = safe_mean(SC["Score"]) if len(SC) else np.nan
EPS, PE, ROE = vget(company, "eps"), vget(company, "pe"), vget(company, "roe")

# ============================================================
# PAGES
# ============================================================


def build_commentary() -> List[Tuple[str, str]]:
    out: List[Tuple[str, str]] = []
    rc, nc = cagr(hist["revenue"][0], hist["revenue"][-1]), cagr(hist["netIncome"][0], hist["netIncome"][-1])
    if np.isfinite(rc):
        out.append(("good" if rc > 5 else "warn", f"Revenue CAGR FY21–25 is <b>{rc:.1f}%</b>."))
    if np.isfinite(nc):
        out.append(("good" if nc > 5 else "warn", f"Net income CAGR FY21–25 is <b>{nc:.1f}%</b>."))
    ni = pd.to_numeric(pd.Series(hist["netIncome"]), errors="coerce")
    peak, cur = float(ni.max()), clean_number(hist["netIncome"][-1])
    if peak > 0 and np.isfinite(cur):
        dd = (1 - cur / peak) * 100
        out.append(("bad" if dd > 25 else "warn", f"FY2025 net income is <b>{dd:.1f}% below</b> its peak "
                    f"(FY{YEARS[int(ni.values.argmax())]}).") if dd > 1 else ("good", "FY2025 net income is at or near its five-year peak."))
    cr = vget(company, "current")
    if np.isfinite(cr):
        out.append(("good" if cr >= 1.5 else "warn", f"Current ratio <b>{cr:.2f}x</b> vs 1.50x teaching benchmark."))
    de, ic = vget(company, "debtEq"), vget(company, "interest")
    if np.isfinite(de) and np.isfinite(ic):
        out.append(("good" if de <= 1 else "bad", f"Leverage <b>{de:.2f}x D/E</b>; interest cover <b>{ic:.1f}x</b>."))
    rt = vget(company, "receivablesTurn")
    if np.isfinite(rt) and rt > 0:
        out.append(("warn" if 365 / rt > 90 else "", f"Approximate receivable days: <b>{365 / rt:.0f}</b>."))
    return out


def page_executive():
    header("Executive Overview", "Five-year performance, profitability, liquidity and analytical health.")
    r25, r24 = vget(company, "revenue"), clean_number(hist["revenue"][-2])
    p25, p24 = vget(company, "netIncome"), clean_number(hist["netIncome"][-2])
    rg, pg = pct_change(r25, r24), pct_change(p25, p24)
    k = st.columns(6)
    k[0].metric("Revenue", f"{fmt(r25)}m", f"{rg:+.1f}% YoY" if np.isfinite(rg) else None)
    k[1].metric("Net income", f"{fmt(p25)}m", f"{pg:+.1f}% YoY" if np.isfinite(pg) else None)
    k[2].metric("EPS", fmt(EPS, 2))
    k[3].metric("P/E", f"{fmt(PE, 2)}x")
    k[4].metric("ROE", f"{fmt(ROE, 1)}%")
    k[5].metric("Ratio health", f"{fmt(HEALTH)} / 100" if np.isfinite(HEALTH) else "N/A",
                help="Average of the nine educational ratio scores. " + light(HEALTH))
    st.write("")
    a, b = st.columns([1.6, 1])
    with a:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=YEARS, y=hist["revenue"], name="Revenue", marker_color="#C9D5F3"))
        fig.add_trace(go.Bar(x=YEARS, y=hist["netIncome"], name="Net income", marker_color=C_ACC))
        fig.add_trace(go.Scatter(x=YEARS, y=hist["npm"], name="Net margin %", yaxis="y2", mode="lines+markers",
                                 line=dict(color=C_WARN, width=2.5)))
        fig.update_layout(barmode="group", yaxis2=dict(overlaying="y", side="right", showgrid=False, ticksuffix="%"))
        fig.update_xaxes(dtick=1)
        show(fig, 380, "Scale and profitability (PKR m)")
    with b:
        s = SC.dropna(subset=["Score"]).sort_values("Score")
        if len(s):
            colors = [C_POS if v >= 70 else C_WARN if v >= 45 else C_NEG for v in s["Score"]]
            fig = go.Figure(go.Bar(x=s["Score"], y=s["Ratio"], orientation="h", marker_color=colors,
                                   text=s["Score"].astype(int), textposition="outside"))
            fig.update_xaxes(range=[0, 110])
            show(fig, 380, "Ratio scores (0–100)")
    a, b = st.columns([1, 1.5])
    with a:
        h3("Key observations")
        insights(build_commentary())
    with b:
        h3("Historical dataset")
        st.dataframe(D.T.style.format("{:,.2f}"), width="stretch", height=330)


def page_trends():
    header("Financial Trends", "Historical movements, indexed performance and metric relationships.")
    picks = st.multiselect("Metrics", list(LBL.values()), default=["NPM (%)", "ROA (%)", "ROE (%)"])
    c1, c2 = st.columns([1, 1])
    norm = c1.toggle("Index to FY2021 = 100", False)
    kind = c2.segmented_control("Chart", ["Line", "Bar"], default="Line", label_visibility="collapsed") or "Line"
    if not picks:
        st.info("Select at least one metric.")
        return
    X = D[picks].copy()
    if norm:
        X = X.divide(X.iloc[0].replace(0, np.nan)) * 100
    lines(X, picks, "Selected metrics" + (" (indexed)" if norm else ""), 400, bar=(kind == "Bar"))
    if len(picks) > 1:
        cm = X.corr()
        fig = go.Figure(go.Heatmap(z=cm.values, x=cm.columns, y=cm.index, zmin=-1, zmax=1,
                                   colorscale=[[0, C_NEG], [.5, "#FFFFFF"], [1, C_ACC]],
                                   text=np.round(cm.values, 2), texttemplate="%{text}"))
        show(fig, 400, "Correlation matrix (five observations — interpret cautiously)")


def page_scorecard():
    header("Ratio Scorecard", "Educational scorecard across liquidity, solvency, profitability and efficiency.")
    if SC.empty:
        st.warning("Insufficient ratio data.")
        return
    st.dataframe(SC, width="stretch", hide_index=True, column_config={
        "FY2025": st.column_config.NumberColumn(format="%.2f"), "FY2024": st.column_config.NumberColumn(format="%.2f"),
        "Δ YoY": st.column_config.NumberColumn(format="%+.2f"),
        "Benchmark": st.column_config.NumberColumn(format="%.2f"),
        "Score": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%d")})
    st.caption("Benchmarks are generic teaching thresholds, not sector recommendations. Scores are heuristics, "
               "not investment advice.")
    v = switch(["Liquidity", "Solvency", "Efficiency"], "sc_view")
    if v == "Liquidity":
        lines(D, ["Current Ratio", "Quick Ratio"], "Liquidity")
    elif v == "Solvency":
        lines(D, ["Debt/Equity", "Interest Coverage"], "Solvency")
    else:
        lines(D, ["Asset Turnover", "Inventory Turnover", "Receivables Turnover"], "Turnover")
        t, pt = vget(company, "receivablesTurn"), clean_number(hist["receivablesTurn"][-2])
        if t > 0 and pt > 0:
            st.metric("Receivable days", f"{365 / t:.0f}", f"{365 / t - 365 / pt:+.0f} vs FY24", delta_color="inverse")


def page_dupont():
    header("DuPont Analysis", "Decompose ROE into margin, asset efficiency and financial leverage.")
    st.latex(r"ROE = NPM \times Asset\ Turnover \times Equity\ Multiplier")
    rows = []
    for i, y in enumerate(YEARS):
        npm, at = clean_number(hist["npm"][i]), clean_number(hist["assetTurn"][i])
        roa, roe = clean_number(hist["roa"][i]), clean_number(hist["roe"][i])
        rows.append([y, npm, at, safe_div(roe, roa), npm * at, roa, roe])
    dup = pd.DataFrame(rows, columns=["Year", "NPM (%)", "Asset Turnover", "Equity Multiplier", "Implied ROA",
                                      "Reported ROA", "Reported ROE"]).set_index("Year")
    st.dataframe(dup.style.format("{:.2f}"), width="stretch")
    gap = np.nanmax(np.abs(dup["Implied ROA"].to_numpy() - dup["Reported ROA"].to_numpy()))
    if np.isfinite(gap):
        (st.success if gap < 1 else st.warning)(f"Maximum NPM × turnover vs reported ROA gap: {gap:.2f} pp."
                                                + ("" if gap < 1 else " Check asset basis and averaging conventions."))
    comps = {}
    for name, col in [("Margin", "NPM (%)"), ("Turnover", "Asset Turnover"), ("Leverage", "Equity Multiplier")]:
        a, b = clean_number(dup.iloc[0][col]), clean_number(dup.iloc[-1][col])
        if a > 0 and b > 0:
            comps[name] = math.log(b / a)
    tot = sum(comps.values())
    c1, c2 = st.columns(2)
    with c1:
        if comps and abs(tot) > 1e-9:
            vals = [v / tot * 100 for v in comps.values()]
            fig = go.Figure(go.Bar(x=list(comps), y=vals, marker_color=PALETTE[:len(comps)],
                                   text=[f"{v:.0f}%" for v in vals], textposition="outside"))
            show(fig, 340, "Share of ROE change FY21→FY25 (log decomposition)")
    with c2:
        lines(dup, ["Reported ROE", "NPM (%)"], "ROE vs margin", 340)


def page_growth():
    header("Growth Analysis", "CAGR, total growth and year-over-year change across key indicators.")
    keys = ["revenue", "netIncome", "eps", "roe", "current"]
    rows = []
    for k in keys:
        s, e = clean_number(hist[k][0]), clean_number(hist[k][-1])
        rows.append([LBL[k], s, e, pct_change(e, s), cagr(s, e)])
    g = pd.DataFrame(rows, columns=["Metric", "FY2021", "FY2025", "Total change (%)", "CAGR (%)"])
    st.dataframe(g.style.format({"FY2021": "{:,.2f}", "FY2025": "{:,.2f}", "Total change (%)": "{:+.1f}",
                                 "CAGR (%)": "{:+.1f}"}, na_rep="N/A"), width="stretch", hide_index=True)
    yoy = pd.DataFrame({LBL[k]: [pct_change(hist[k][i], hist[k][i - 1]) for i in range(1, 5)] for k in keys},
                       index=YEARS[1:]).T
    lim = float(np.nanmax(np.abs(yoy.values))) if np.isfinite(yoy.values).any() else 1
    fig = go.Figure(go.Heatmap(z=yoy.values, x=[f"FY{y}" for y in yoy.columns], y=yoy.index, colorscale=DIVERGE,
                               zmin=-lim, zmax=lim, text=np.round(yoy.values, 1), texttemplate="%{text}%"))
    show(fig, 340, "Year-over-year change (%)")


def page_vertical():
    header("Vertical Analysis", "Common-size income-statement and balance-sheet composition.")
    vt = company.get("vertical", {})
    if not vt:
        st.info("No common-size data supplied.")
        return
    cols = st.columns(2)
    for col, keys, color, title in [
            (cols[0], ["Cost of Revenue", "Gross Profit", "Operating Income", "Net Income"], C_ACC,
             "Income statement (% of revenue)"),
            (cols[1], ["Current Assets", "Net PPE", "Total Liabilities", "Total Equity"], C_POS,
             "Balance sheet (% of total)")]:
        ks = [k for k in keys if k in vt]
        with col:
            if ks:
                fig = go.Figure(go.Bar(x=[vt[k] for k in ks], y=ks, orientation="h", marker_color=color,
                                       text=[f"{vt[k]:.1f}%" for k in ks], textposition="outside"))
                fig.update_yaxes(autorange="reversed")
                fig.update_xaxes(range=[0, 115])
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
    header("Peer Comparison", "Compare indicators across the companies in the active dataset.")
    peer = peer_table()
    st.dataframe(peer.style.format("{:,.2f}", na_rep="N/A"), width="stretch")
    a, b = st.columns(2)
    with a:
        fig = go.Figure()
        for i, (s, x) in enumerate(ALL.items()):
            base = clean_number(x["historical"]["revenue"][0])
            if base > 0:
                fig.add_trace(go.Scatter(x=YEARS, y=np.array(x["historical"]["revenue"], dtype=float) / base * 100,
                                         name=s, mode="lines+markers", line=dict(width=2.5, color=PALETTE[i % 6])))
        fig.update_xaxes(dtick=1)
        show(fig, 360, "Revenue indexed to FY2021 = 100")
    with b:
        m = peer[["NPM %", "ROE %"]].reset_index().melt("Company", var_name="Metric", value_name="Value")
        show(px.bar(m, x="Company", y="Value", color="Metric", barmode="group", color_discrete_sequence=PALETTE),
             360, "Net margin and ROE (%)")
    if len(peer) > 1:
        rank = peer[["NPM %", "ROE %", "Current", "Rev CAGR %"]].rank(ascending=False).mean(axis=1).sort_values()
        insights([("good", f"Best average rank across margin, ROE, liquidity and growth: <b>{rank.index[0]}</b>.")])
    st.caption("Descriptive comparison only. Accounting basis, business mix, commodity exposure and capital "
               "structure differ across companies.")


def page_pestel():
    header("Industry / PESTEL", "External forces affecting Pakistani exploration and production companies.")
    items = [("Political / Regulatory", "Exploration blocks, permits, fiscal terms, royalties and taxation affect project economics.", "High"),
             ("Economic", "Oil and gas prices, inflation, interest rates and PKR/USD influence margins.", "High"),
             ("Social", "Population growth, industrial activity and household energy demand shape consumption.", "Medium"),
             ("Technological", "Seismic imaging, reservoir analytics and automation affect recovery and cost.", "Medium"),
             ("Environmental", "Emission rules, climate policy, water and methane management affect operations.", "Medium"),
             ("Legal / Geopolitical", "Contracts, security conditions and joint ventures affect operational continuity.", "High")]
    cols = st.columns(3)
    for i, (t, txt, imp) in enumerate(items):
        with cols[i % 3]:
            panel(t, f"{txt}<div style='margin-top:10px'>Impact: {badge(imp)}</div>", 140)


def page_risk():
    header("Risk Dashboard", "Leverage, liquidity, margin, earnings and data-quality indicators.")
    st.caption("Transparent educational heuristics — not forecasts or investment advice.")
    de, cr, ic = vget(company, "debtEq"), vget(company, "current"), vget(company, "interest")
    npm = pd.Series(pd.to_numeric(hist["npm"], errors="coerce"))
    vol = npm.std(ddof=0) / npm.mean() * 100 if npm.mean() else np.nan
    rt = vget(company, "receivablesTurn")
    rd = 365 / rt if rt > 0 else np.nan
    ni = pd.to_numeric(pd.Series(hist["netIncome"]), errors="coerce")
    cn = clean_number(hist["netIncome"][-1])
    dd = (1 - cn / ni.max()) * 100 if ni.max() > 0 and np.isfinite(cn) else np.nan
    vr = vget(company, "revenue")
    gap = abs(clean_number(hist["revenue"][-1]) / vr - 1) * 100 if vr > 0 else np.nan
    spec = [("Leverage", de, lambda v: v * 50, lambda v: f"D/E {v:.2f}x"),
            ("Liquidity", cr, lambda v: 100 - v * 25, lambda v: f"Current {v:.2f}x"),
            ("Interest cover", ic, lambda v: 100 - v * 8, lambda v: f"{v:.1f}x"),
            ("Margin volatility", vol, lambda v: v * 4, lambda v: f"NPM CV {v:.1f}%"),
            ("Receivables", rd, lambda v: v / 2, lambda v: f"{v:.0f} days"),
            ("Earnings drawdown", dd, lambda v: v * 2, lambda v: f"{v:.1f}% below peak"),
            ("Data reliability", gap, lambda v: v * 3, lambda v: f"Revenue gap {v:.1f}%")]
    rows = [[n, float(np.clip(f(v), 0, 100)) if np.isfinite(v) else np.nan, t(v) if np.isfinite(v) else "N/A"]
            for n, v, f, t in spec]
    rdf = pd.DataFrame(rows, columns=["Risk", "Score", "Evidence"])
    rdf["Level"] = pd.cut(rdf["Score"], [-1, 33, 66, 101], labels=["Low", "Medium", "High"]).astype(str).replace("nan", "N/A")
    a, b = st.columns([1, 1.5])
    with a:
        st.metric("Composite risk score", f"{rdf['Score'].mean():.0f} / 100", help="Higher means riskier.")
        st.dataframe(rdf, width="stretch", hide_index=True, column_config={
            "Score": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%d")})
    with b:
        c = rdf.dropna(subset=["Score"]).sort_values("Score")
        colors = [C_POS if v <= 33 else C_WARN if v <= 66 else C_NEG for v in c["Score"]]
        fig = go.Figure(go.Bar(x=c["Score"], y=c["Risk"], orientation="h", marker_color=colors,
                               text=c["Score"].round(0).astype(int), textposition="outside"))
        fig.update_xaxes(range=[0, 110])
        show(fig, 380, "Risk indicator scores (higher = riskier)")
    panel("Structural E&P risk themes", "Commodity price and volume exposure, PKR/USD exposure on imported capex, "
          "reserve depletion, receivables and circular-debt collections, fiscal-policy changes and operational continuity.")


def page_dcf():
    header("DCF & Monte Carlo", "Discounted cash flow, sensitivities, tornado and simulated valuation ranges.")
    st.caption("Illustrative academic model — not investment advice.")
    sh, rev0 = shares(company), vget(company, "revenue")
    pe_price = PE * EPS if np.isfinite(PE) and np.isfinite(EPS) else np.nan
    if not (np.isfinite(sh) and sh > 0 and np.isfinite(rev0) and rev0 > 0):
        st.error("DCF needs positive FY2025 revenue and a positive implied share count (PAT ÷ EPS).")
        return
    d0 = default_dcf(company)
    a, b = st.columns([1, 2.2])
    with a:
        st.markdown('<div class="label">Assumptions</div>', unsafe_allow_html=True)
        growth = st.number_input("Revenue growth (%)", value=d0["growth"], step=.5)
        margin = st.number_input("EBIT margin (%)", value=d0["margin"], step=.5)
        tax = st.number_input("Tax rate (%)", value=d0["tax"], min_value=0.0, max_value=100.0, step=1.0)
        capex = st.number_input("Capex (% revenue)", value=d0["capex"], min_value=0.0, step=.5)
        wc = st.number_input("Working-capital drag (% revenue)", value=d0["wc"], min_value=-20.0, step=.5)
        wacc = st.number_input("WACC (%)", value=d0["wacc"], min_value=.1, max_value=100.0, step=.5)
        tg = st.number_input("Terminal growth (%)", value=d0["tg"], min_value=-10.0, max_value=20.0, step=.25)
        nd = st.number_input("Net debt (PKR m)", value=0.0, step=1000.0)
        st.caption(f"Implied shares ≈ {sh:,.0f}m (PAT ÷ EPS)."
                   + (f" P/E-implied price PKR {pe_price:,.1f}." if np.isfinite(pe_price) else ""))
    if wacc <= tg:
        with b:
            st.error("WACC must exceed terminal growth.")
        return
    res = dcf(rev0, growth, margin, tax, capex, wc, wacc, tg, nd, sh)
    with b:
        k = st.columns(3)
        k[0].metric("Enterprise value", f"{fmt(res['ev'])}m")
        k[1].metric("Model value / share", f"PKR {res['ps']:,.1f}")
        k[2].metric("Vs P/E-implied price", f"{(res['ps'] / pe_price - 1) * 100:+.1f}%"
                    if np.isfinite(pe_price) and pe_price else "N/A")
        wf = go.Figure(go.Waterfall(x=["PV explicit FCF", "PV terminal value", "Net debt", "Equity value"],
                                    measure=["relative", "relative", "relative", "total"],
                                    y=[res["pv"], res["pvtv"], -nd, 0], connector=dict(line=dict(color="#D0D5DD")),
                                    increasing=dict(marker=dict(color=C_ACC)), decreasing=dict(marker=dict(color=C_NEG)),
                                    totals=dict(marker=dict(color="#5B6B85"))))
        show(wf, 300, "Value bridge (PKR m)")
        ts = safe_div(res["pvtv"], res["ev"]) * 100
        if np.isfinite(ts):
            (st.warning if ts > 75 else st.caption)(f"Terminal value contributes about {ts:.0f}% of enterprise value.")
    f = pd.DataFrame(res["rows"], columns=["Year", "Revenue", "EBIT", "FCF", "Discounted FCF"])
    f["Year"] = [f"FY{2025 + int(t)}E" for t in f["Year"]]
    st.dataframe(f.style.format({c: "{:,.0f}" for c in f.columns if c != "Year"}), width="stretch", hide_index=True)

    v = switch(["Sensitivity", "Tornado", "Monte Carlo"], "dcf_view")
    if v == "Sensitivity":
        ws, gs = np.arange(wacc - 3, wacc + 3.1, 1.0), np.arange(max(-5, tg - 2), tg + 2.1, 1.0)
        W, G = np.meshgrid(ws, gs)
        Z = dcf_vec(rev0, growth, margin, tax, capex, wc, W, G, nd, sh)
        txt = [["" if not np.isfinite(x) else f"{x:,.0f}" for x in r] for r in Z]
        fig = go.Figure(go.Heatmap(z=Z, x=[f"{w:.1f}%" for w in ws], y=[f"{g:.1f}%" for g in gs],
                                   colorscale=[[0, "#F3D3D3"], [.5, "#FFFFFF"], [1, "#CDE9DE"]],
                                   text=txt, texttemplate="%{text}", showscale=False))
        fig.update_xaxes(title="WACC")
        fig.update_yaxes(title="Terminal growth")
        show(fig, 360, "Value per share (PKR)")
    elif v == "Tornado":
        base = res["ps"]
        shocks = {"WACC ±2pp": ("wacc", 2), "Growth ±3pp": ("growth", 3), "EBIT margin ±4pp": ("margin", 4),
                  "Capex ±3pp": ("capex", 3), "Terminal growth ±1pp": ("tg", 1)}
        rows = []
        for name, (key, d) in shocks.items():
            vs = []
            for sg in (-1, 1):
                p = dict(growth=growth, margin=margin, capex=capex, wacc=wacc, tg=tg)
                p[key] += sg * d
                vs.append(float(dcf_vec(rev0, p["growth"], p["margin"], tax, p["capex"], wc, p["wacc"], p["tg"], nd, sh)))
            rows.append((name, np.nanmin(vs) - base, np.nanmax(vs) - base))
        rows.sort(key=lambda r: abs(r[2] - r[1]))
        fig = go.Figure()
        fig.add_trace(go.Bar(y=[r[0] for r in rows], x=[r[1] for r in rows], orientation="h", name="Downside", marker_color=C_NEG))
        fig.add_trace(go.Bar(y=[r[0] for r in rows], x=[r[2] for r in rows], orientation="h", name="Upside", marker_color=C_POS))
        fig.update_layout(barmode="relative")
        show(fig, 320, f"Change in value per share vs base (PKR {base:,.1f})")
    else:
        n = st.select_slider("Simulations", [500, 1000, 2000, 5000, 10000], value=2000)
        out = run_mc(rev0, growth, margin, tax, capex, wc, wacc, tg, nd, sh, n)
        if len(out) < 10:
            st.warning("Too few valid simulations. Adjust WACC or terminal growth.")
        else:
            p5, med, p95 = np.percentile(out, [5, 50, 95])
            fig = go.Figure(go.Histogram(x=out, nbinsx=50, marker_color=C_ACC, opacity=.85))
            fig.add_vline(x=med, line_color=C_POS, line_dash="dash", annotation_text="Median")
            if np.isfinite(pe_price):
                fig.add_vline(x=pe_price, line_color=C_WARN, annotation_text="P/E implied")
            show(fig, 340, "Distribution of model value per share (PKR)")
            m = st.columns(4)
            m[0].metric("5th percentile", f"{p5:,.0f}")
            m[1].metric("Median", f"{med:,.0f}")
            m[2].metric("95th percentile", f"{p95:,.0f}")
            m[3].metric("P(value > P/E price)", f"{np.mean(out > pe_price) * 100:.0f}%" if np.isfinite(pe_price) else "N/A")


def page_relative():
    header("Relative Valuation", "P/E, EPS, dividend yield and ROE across peers, with an indicative value range.")
    rows = []
    for s, x in ALL.items():
        pe, eps = vget(x, "pe"), vget(x, "eps")
        rows.append([s, pe, eps, pe * eps if np.isfinite(pe) and np.isfinite(eps) else np.nan,
                     vget(x, "dividendYield"), vget(x, "roe")])
    rel = pd.DataFrame(rows, columns=["Company", "P/E", "EPS", "P/E implied price", "Div yield %", "ROE %"]).set_index("Company")
    st.dataframe(rel.style.format("{:,.2f}", na_rep="N/A"), width="stretch")
    a, b = st.columns(2)
    with a:
        sd = rel.reset_index().dropna(subset=["ROE %", "P/E"])
        if len(sd):
            sd["Div yield %"] = sd["Div yield %"].fillna(0).clip(lower=.1)
            fig = px.scatter(sd, x="ROE %", y="P/E", size="Div yield %", text="Company", size_max=34)
            fig.update_traces(textposition="top center", marker=dict(color=C_ACC, opacity=.75))
            show(fig, 360, "P/E vs ROE (bubble = dividend yield)")
    with b:
        pes = pd.to_numeric(rel["P/E"], errors="coerce").dropna()
        if len(pes) and np.isfinite(EPS):
            med = pes.median()
            items = [("Own P/E × EPS", PE * EPS if np.isfinite(PE) else np.nan), ("Peer-median P/E × EPS", med * EPS),
                     ("DCF (default assumptions)", base_dcf_value(company))]
            items = [(n, v) for n, v in items if np.isfinite(v)]
            fig = go.Figure(go.Bar(x=[v for _, v in items], y=[n for n, _ in items], orientation="h",
                                   marker_color=PALETTE[:len(items)], text=[f"{v:,.0f}" for _, v in items],
                                   textposition="outside"))
            fig.update_yaxes(autorange="reversed")
            show(fig, 360, f"Indicative value per share — {sel} (PKR)")
    st.caption("Mechanical multiples ignore growth, risk, accounting basis and business mix — a descriptive exercise only.")


def page_scenarios():
    header("Scenario Analysis", "How alternative growth and margin assumptions affect revenue and EPS.")
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
    colors = {"Bear": C_NEG, "Base": C_ACC, "Bull": C_POS}
    base_rev = vget(company, "revenue")
    fig, cols, table = go.Figure(), st.columns(3), []
    for col, (name, (g, m)) in zip(cols, cases.items()):
        path = [base_rev * (1 + g / 100) ** t for t in range(hz + 1)]
        profit = path[-1] * m / 100
        eps = profit / sh
        fig.add_trace(go.Scatter(x=[f"FY{2025 + t}" for t in range(hz + 1)], y=path, name=name, mode="lines+markers",
                                 line=dict(color=colors[name], width=2.5)))
        table.append([name, g, m, path[-1], profit, eps])
        with col:
            panel(name, f"Growth {g:.1f}% · Net margin {m:.1f}%")
            st.metric(f"Revenue FY{2025 + hz}", f"{fmt(path[-1])}m")
            st.metric("Net profit", f"{fmt(profit)}m")
            dl = pct_change(eps, EPS) if np.isfinite(EPS) else np.nan
            st.metric("EPS", f"PKR {eps:,.2f}", f"{dl:+.1f}% vs FY25" if np.isfinite(dl) else None)
    show(fig, 340, "Revenue scenario paths (PKR m)")


def page_integrity():
    header("Data Integrity", "Reconcile submitted figures with verified FY2025 values and internal relationships.")
    st.caption("Submitted historical values and verified FY2025 snapshots are kept separate; differences can come "
               "from restatements, consolidation, units or methodology.")
    rows = []
    for s, x in DEMO.items():
        for k, lab in [("revenue", "Revenue"), ("netIncome", "PAT"), ("eps", "EPS"), ("pe", "P/E"),
                       ("current", "Current ratio"), ("roe", "ROE")]:
            if k not in x.get("verified2025", {}):
                continue
            sub, ver = clean_number(x["historical"][k][-1]), clean_number(x["verified2025"][k])
            var = (sub / ver - 1) * 100 if ver != 0 else np.nan
            stt = "N/A" if not np.isfinite(var) else "Verified" if abs(var) < .5 else "Minor" if abs(var) < 5 else "Major"
            rows.append([s, lab, sub, ver, var, stt])
    ig = pd.DataFrame(rows, columns=["Company", "Metric", "Submitted", "Verified", "Variance %", "Status"])
    a, b = st.columns([1.2, 1])
    with a:
        st.dataframe(ig.style.format({"Submitted": "{:,.2f}", "Verified": "{:,.2f}", "Variance %": "{:+.2f}"}),
                     width="stretch", hide_index=True, height=360)
    with b:
        if len(ig):
            show(px.bar(ig, x="Metric", y="Variance %", color="Company", barmode="group",
                        color_discrete_sequence=PALETTE), 360, "Submitted vs verified variance (%)")
    h3("Internal consistency", f"{sel}: reported net margin vs net income ÷ revenue.")
    rows = []
    for i, y in enumerate(YEARS):
        rev, ni, npm = clean_number(hist["revenue"][i]), clean_number(hist["netIncome"][i]), clean_number(hist["npm"][i])
        imp = ni / rev * 100 if rev != 0 else np.nan
        rows.append([y, npm, imp, npm - imp if np.isfinite(npm) and np.isfinite(imp) else np.nan])
    cdf = pd.DataFrame(rows, columns=["Year", "Reported NPM", "NI / Revenue", "Gap (pp)"])
    st.dataframe(cdf.style.format({c: "{:.2f}" for c in cdf.columns if c != "Year"}), width="stretch", hide_index=True)
    st.caption("Recommended source priority: audited annual report → PSX issuer page → licensed data provider. "
               "The demo dataset is not a live market feed.")


def build_report() -> str:
    L = [f"# {sel} — {company['name']}", f"_Generated {datetime.now():%Y-%m-%d %H:%M} · PSX Financial Analysis Lab_", "",
         "## Key figures (FY2025)", f"- Revenue: PKR {fmt(vget(company, 'revenue'))}m",
         f"- Net income: PKR {fmt(vget(company, 'netIncome'))}m", f"- EPS {fmt(EPS, 2)} | P/E {fmt(PE, 2)}x | ROE {fmt(ROE, 1)}%",
         f"- Ratio health: {fmt(HEALTH)}/100 ({light(HEALTH)})", "", "## Observations"]
    L += [f"- {re.sub('<[^>]+>', '', t)}" for _, t in build_commentary()]
    L += ["", "## Scorecard", "```", SC.to_string(index=False), "```", "", "_Educational output — not investment advice._"]
    return "\n".join(L)


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
    header("Import & Export", "Import company datasets and export analysis results.")
    panel("JSON import", "Upload a JSON company record or edit the template. All 15 metrics need exactly five values, "
          "ordered FY2021 → FY2025.")
    tpl = {"symbol": "NEWCO", "name": "Example Company", "years": YEARS, **{k: [1, 2, 3, 4, 5] for k in HK},
           "source": "Source / URL"}
    tpl.update(revenue=[100, 110, 120, 130, 140], netIncome=[10, 12, 14, 15, 16], npm=[10, 10.91, 11.67, 11.54, 11.43],
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
        raw = st.text_area("Or paste JSON", json.dumps(tpl, indent=2), height=380)
    if st.button("Validate and add company", type="primary", key="add_company"):
        try:
            p = json.loads(raw)
            if not isinstance(p, dict):
                raise ValueError("Top-level JSON must be an object.")
            miss = sorted(set(tpl) - set(p))
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
            gaps = [abs(nd["netIncome"][i] / nd["revenue"][i] * 100 - nd["npm"][i]) for i in range(5) if nd["revenue"][i] != 0]
            if gaps and max(gaps) > 2:
                st.warning("NPM differs from NI/Revenue by more than 2 pp in at least one year.")
            src = str(p.get("source", "User supplied")).strip()
            cc = mk(name, "User-imported company.", [nd[k] for k in HK],
                    {k: nd[k][-1] for k in ("revenue", "netIncome", "eps", "pe")}, None, [(src, src if src.startswith("http") else "")])
            ok, why = validate_company_structure(cc)
            if not ok:
                raise ValueError(why)
            st.session_state.custom[sym] = cc
            st.success(f"{sym} added. Choose it from the company selector.")
        except json.JSONDecodeError as exc:
            st.error(f"Invalid JSON: {exc}")
        except Exception as exc:
            st.error(f"Could not import company: {exc}")
    h3("Export", f"Download the active company ({sel}).")
    c = st.columns(4)
    c[0].download_button("Dataset (CSV)", D.to_csv().encode("utf-8"), f"{sel}_dataset.csv", "text/csv", key="dl1", width="stretch")
    c[1].download_button("Scorecard (CSV)", SC.to_csv(index=False).encode("utf-8"), f"{sel}_scorecard.csv", "text/csv", key="dl2", width="stretch")
    c[2].download_button("Company (JSON)", json.dumps(
        {"symbol": sel, "name": company["name"], "years": YEARS, **{k: hist[k] for k in HK},
         "verified2025": company.get("verified2025", {}), "vertical": company.get("vertical", {}),
         "sources": company.get("sources", [])}, indent=2).encode("utf-8"), f"{sel}_company.json", "application/json",
        key="dl3", width="stretch")
    c[3].download_button("Report (Markdown)", build_report().encode("utf-8"), f"{sel}_report.md", "text/markdown", key="dl4", width="stretch")
    xb = excel_bytes()
    if xb:
        st.download_button("Excel workbook", xb, f"{sel}_analysis.xlsx",
                           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="dl5")
    h3("Imported companies")
    if st.session_state.custom:
        st.dataframe(pd.DataFrame([{"Symbol": s, "Company": x["name"], "Source": x["sources"][0][0] if x.get("sources") else "N/A"}
                                   for s, x in st.session_state.custom.items()]), width="stretch", hide_index=True)
        if st.button("Remove all imported companies", key="clear_custom"):
            st.session_state.custom = {}
            st.rerun()
    else:
        st.caption("No custom companies imported in this session.")


def page_refs():
    header("References", "Company sources and recommended production architecture.")
    srcs = company.get("sources", [])
    if not srcs:
        st.info("No references supplied.")
    for title, url in srcs:
        u = str(url).strip()
        link = (f'<a href="{u}" target="_blank" rel="noopener noreferrer" style="color:#1F4FD8;word-break:break-all">{u}</a>'
                if u.startswith(("http://", "https://")) else "")
        panel(title, link)
    h3("Recommended production architecture")
    st.code("Streamlit UI\n    ↓\nAuthorized backend / data adapter\n    ↓\nPSX feed | annual-report parser | cached dataset\n"
            "    ↓\nNormalization + source metadata\n    ↓\nFinancial ratio engine\n    ↓\nCharts / valuation / scenarios / exports",
            language="text")
    st.caption("Never place data-provider credentials, API keys or tokens in frontend code or a public repository.")


# ============================================================
# NAVIGATION
# ============================================================

P = st.Page
nav = st.navigation({
    "Overview": [P(page_executive, title="Executive Overview", icon=":material/dashboard:", url_path="overview", default=True)],
    "Performance": [
        P(page_trends, title="Trends", icon=":material/show_chart:", url_path="trends"),
        P(page_growth, title="Growth", icon=":material/trending_up:", url_path="growth"),
        P(page_dupont, title="DuPont", icon=":material/account_tree:", url_path="dupont"),
        P(page_vertical, title="Vertical Analysis", icon=":material/pie_chart:", url_path="vertical")],
    "Assessment": [
        P(page_scorecard, title="Ratio Scorecard", icon=":material/fact_check:", url_path="scorecard"),
        P(page_risk, title="Risk", icon=":material/shield:", url_path="risk"),
        P(page_peers, title="Peer Comparison", icon=":material/compare_arrows:", url_path="peers"),
        P(page_pestel, title="Industry / PESTEL", icon=":material/public:", url_path="pestel")],
    "Valuation": [
        P(page_dcf, title="DCF & Monte Carlo", icon=":material/calculate:", url_path="dcf"),
        P(page_relative, title="Relative Valuation", icon=":material/balance:", url_path="relative"),
        P(page_scenarios, title="Scenarios", icon=":material/insights:", url_path="scenarios")],
    "Data": [
        P(page_integrity, title="Data Integrity", icon=":material/rule:", url_path="integrity"),
        P(page_io, title="Import & Export", icon=":material/swap_vert:", url_path="io"),
        P(page_refs, title="References", icon=":material/menu_book:", url_path="references")],
})

with st.sidebar:
    st.caption("Demo dataset · FY2021–FY2025 · not a live market feed")

nav.run()

st.markdown('<div class="footer">COMSATS University Islamabad · Business Finance · Instructor: Miss Sania Khalid · '
            'Student: Muhammad Abubakar<br>Academic / illustrative use only — not investment advice.</div>',
            unsafe_allow_html=True)
