# -*- coding: utf-8 -*-
"""
PSX Financial Analysis Lab
COMSATS University Islamabad

Single-file Streamlit financial analysis dashboard.

Run:
    streamlit run app.py

Recommended requirements:
    streamlit>=1.40
    pandas
    numpy
    plotly
    matplotlib
    openpyxl
    scikit-learn
"""

from __future__ import annotations

import json
import math
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# ============================================================
# OPTIONAL DEPENDENCY
# ============================================================

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


# ============================================================
# PREMIUM GLASSMORPHISM FINANCE UI
# ============================================================

st.markdown(
    """
<style>

/* =========================================================
   ROOT THEME
   ========================================================= */

:root {
    --bg: #020611;
    --bg2: #050b18;
    --panel: rgba(10, 22, 42, 0.68);
    --panel-strong: rgba(12, 28, 52, 0.88);

    --border: rgba(100, 190, 255, 0.16);
    --border-bright: rgba(92, 200, 255, 0.42);

    --text: #f2f8ff;
    --text-soft: #c5d7e8;
    --muted: #8299b0;

    --cyan: #54d6ff;
    --blue: #2498ff;
    --violet: #8b7cff;
    --purple: #b06cff;

    --green: #35e59a;
    --yellow: #ffd166;
    --red: #ff637c;

    --shadow:
        0 20px 70px rgba(0, 0, 0, .35);

    --glass-shadow:
        0 18px 55px rgba(0, 0, 0, .30),
        inset 0 1px 0 rgba(255,255,255,.055);
}


/* =========================================================
   GLOBAL
   ========================================================= */

html {
    scroll-behavior: smooth;
}

body {
    background: #020611;
}

.stApp {
    min-height: 100vh;

    background:
        radial-gradient(
            circle at 8% 5%,
            rgba(36, 152, 255, .16),
            transparent 27%
        ),
        radial-gradient(
            circle at 92% 8%,
            rgba(139, 124, 255, .15),
            transparent 25%
        ),
        radial-gradient(
            circle at 55% 90%,
            rgba(53, 229, 154, .055),
            transparent 28%
        ),
        linear-gradient(
            135deg,
            #020611 0%,
            #040a16 42%,
            #020712 100%
        );

    color: var(--text);
}


/* Financial-terminal grid */

.stApp::before {
    content: "";
    position: fixed;
    inset: 0;

    pointer-events: none;
    z-index: 0;

    background-image:
        linear-gradient(
            rgba(92, 200, 255, .025) 1px,
            transparent 1px
        ),
        linear-gradient(
            90deg,
            rgba(92, 200, 255, .025) 1px,
            transparent 1px
        );

    background-size: 42px 42px;

    mask-image:
        linear-gradient(
            to bottom,
            rgba(0,0,0,.95),
            rgba(0,0,0,.25)
        );
}


/* Floating ambient glow */

.stApp::after {
    content: "";

    position: fixed;

    width: 500px;
    height: 500px;

    right: -220px;
    bottom: -220px;

    border-radius: 50%;

    pointer-events: none;

    background:
        radial-gradient(
            circle,
            rgba(84,214,255,.10),
            transparent 68%
        );

    filter: blur(15px);

    animation:
        ambientFloat 12s ease-in-out infinite alternate;

    z-index: 0;
}

@keyframes ambientFloat {
    from {
        transform: translate3d(0, 0, 0);
    }

    to {
        transform: translate3d(-80px, -60px, 0);
    }
}


/* Main content above decorative layers */

[data-testid="stAppViewContainer"] {
    position: relative;
    z-index: 1;
}

.block-container {
    max-width: 1550px;

    padding-top: 2.5rem;
    padding-bottom: 4rem;

    animation:
        pageEntrance .65s ease-out;
}

@keyframes pageEntrance {
    from {
        opacity: 0;
        transform: translateY(14px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}


/* =========================================================
   TEXT
   ========================================================= */

.stApp,
.stApp p,
.stApp label,
.stApp li,
.stApp h1,
.stApp h2,
.stApp h3,
.stApp h4,
.stApp h5,
.stApp span,
[data-testid="stMarkdownContainer"] *,
[data-testid="stCaptionContainer"] *,
[data-testid="stMetricValue"] *,
[data-testid="stMetricLabel"] * {
    color: var(--text) !important;
}

.small-note {
    color: var(--muted) !important;
    font-size: .77rem;
}

.stCaption,
[data-testid="stCaptionContainer"] {
    color: var(--muted) !important;
}


/* =========================================================
   HEADER
   ========================================================= */

[data-testid="stHeader"] {
    background: rgba(2, 6, 17, .72) !important;

    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);

    border-bottom:
        1px solid rgba(92, 200, 255, .08);
}

[data-testid="stHeader"] * {
    color: #9eb5c9 !important;
    fill: #9eb5c9 !important;
}


/* =========================================================
   SIDEBAR — FROSTED GLASS
   ========================================================= */

[data-testid="stSidebar"] {
    background:
        linear-gradient(
            180deg,
            rgba(4, 11, 25, .94),
            rgba(3, 8, 19, .90)
        ) !important;

    border-right:
        1px solid rgba(92, 200, 255, .14);

    box-shadow:
        15px 0 50px rgba(0,0,0,.22);

    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: 1rem;
}

[data-testid="stSidebar"] * {
    color: var(--text) !important;
}


/* Sidebar decorative glow */

[data-testid="stSidebar"]::before {
    content: "";

    position: absolute;

    width: 230px;
    height: 230px;

    top: -100px;
    left: -100px;

    border-radius: 50%;

    background:
        radial-gradient(
            circle,
            rgba(36,152,255,.16),
            transparent 70%
        );

    pointer-events: none;
}


/* =========================================================
   SIDEBAR BRAND
   ========================================================= */

.sidebar-brand {
    position: relative;

    padding:
        .85rem
        .75rem
        1.15rem
        .75rem;

    margin-bottom: .5rem;
}

.sidebar-brand .brand-icon {
    display: inline-flex;

    width: 48px;
    height: 48px;

    align-items: center;
    justify-content: center;

    border-radius: 15px;

    background:
        linear-gradient(
            135deg,
            #159cf4,
            #695cf6
        );

    font-size: 1.45rem;

    box-shadow:
        0 10px 35px rgba(21,156,244,.28),
        0 0 25px rgba(105,92,246,.12);

    border:
        1px solid rgba(255,255,255,.18);
}

.sidebar-brand .brand-title {
    font-size: 1.04rem;

    font-weight: 850;

    margin-top: .7rem;

    letter-spacing: .1px;
}

.sidebar-brand .brand-subtitle {
    color: #718ba3 !important;

    font-size: .72rem;

    line-height: 1.55;

    margin-top: .18rem;
}


/* =========================================================
   SIDEBAR SECTION LABELS
   ========================================================= */

.sidebar-section {
    color: var(--cyan) !important;

    font-size: .65rem;

    font-weight: 850;

    letter-spacing: 1.7px;

    text-transform: uppercase;

    margin:
        1.05rem
        .35rem
        .45rem;
}


/* =========================================================
   SIDEBAR SELECT
   ========================================================= */

[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background:
        rgba(12, 29, 52, .72) !important;

    border:
        1px solid rgba(92,200,255,.16) !important;

    border-radius: 12px !important;

    min-height: 42px;

    box-shadow:
        inset 0 1px 0 rgba(255,255,255,.035),
        0 8px 25px rgba(0,0,0,.12);

    transition:
        border-color .2s ease,
        box-shadow .2s ease,
        transform .2s ease;
}

[data-testid="stSidebar"] [data-baseweb="select"] > div:hover {
    border-color:
        rgba(92,200,255,.48) !important;

    box-shadow:
        0 0 22px rgba(92,200,255,.08);
}

[data-testid="stSidebar"] [data-baseweb="select"] * {
    color: #eaf4ff !important;
}


/* =========================================================
   SIDEBAR NAVIGATION
   ========================================================= */

[data-testid="stSidebar"] div[role="radiogroup"] {
    gap: .30rem;
}

[data-testid="stSidebar"] label[data-baseweb="radio"] {
    width: 100%;

    background:
        transparent !important;

    border:
        1px solid transparent !important;

    border-radius: 11px !important;

    padding:
        .55rem
        .68rem !important;

    margin: 0 !important;

    transition:
        all .20s ease;

    position: relative;

    overflow: hidden;
}

[data-testid="stSidebar"] label[data-baseweb="radio"]::after {
    content: "";

    position: absolute;

    left: -120%;
    top: 0;

    width: 60%;
    height: 100%;

    background:
        linear-gradient(
            90deg,
            transparent,
            rgba(255,255,255,.08),
            transparent
        );

    transform: skewX(-20deg);

    transition: left .55s ease;

    pointer-events: none;
}

[data-testid="stSidebar"] label[data-baseweb="radio"]:hover::after {
    left: 130%;
}

[data-testid="stSidebar"] label[data-baseweb="radio"]:hover {
    background:
        rgba(30, 71, 105, .32) !important;

    border-color:
        rgba(92,200,255,.14) !important;

    transform:
        translateX(3px);
}

[data-testid="stSidebar"] label[data-baseweb="radio"]:has(input:checked) {
    background:
        linear-gradient(
            90deg,
            rgba(27,151,218,.24),
            rgba(108,82,225,.15)
        ) !important;

    border:
        1px solid rgba(92,200,255,.30) !important;

    box-shadow:
        inset 3px 0 0 #54d6ff,
        0 7px 22px rgba(0,0,0,.14),
        0 0 20px rgba(84,214,255,.06);
}

[data-testid="stSidebar"] label[data-baseweb="radio"]:has(input:checked) p {
    color: #72dbff !important;

    font-weight: 800 !important;
}

[data-testid="stSidebar"] label[data-baseweb="radio"] p {
    color: #a9bdd0 !important;

    font-size: .80rem !important;

    margin: 0 !important;
}

[data-testid="stSidebar"] label[data-baseweb="radio"] > div:first-child {
    display: none !important;
}


/* =========================================================
   HERO
   ========================================================= */

.hero {
    position: relative;

    overflow: hidden;

    padding:
        1.65rem
        1.75rem;

    border:
        1px solid rgba(92,200,255,.22);

    border-radius: 22px;

    background:
        linear-gradient(
            135deg,
            rgba(17, 42, 69, .78),
            rgba(7, 18, 35, .72)
        );

    margin-bottom: 1.35rem;

    box-shadow:
        0 25px 70px rgba(0,0,0,.28),
        inset 0 1px 0 rgba(255,255,255,.06);

    backdrop-filter:
        blur(22px);

    -webkit-backdrop-filter:
        blur(22px);

    animation:
        heroIn .75s ease-out;
}

@keyframes heroIn {
    from {
        opacity: 0;
        transform:
            translateY(-12px)
            scale(.985);
    }

    to {
        opacity: 1;
        transform:
            translateY(0)
            scale(1);
    }
}


/* Animated hero gradient */

.hero::before {
    content: "";

    position: absolute;

    width: 420px;
    height: 420px;

    right: -170px;
    top: -220px;

    border-radius: 50%;

    background:
        radial-gradient(
            circle,
            rgba(84,214,255,.18),
            rgba(139,124,255,.08) 42%,
            transparent 70%
        );

    animation:
        heroGlow 9s ease-in-out infinite alternate;
}

@keyframes heroGlow {
    from {
        transform: translate(0, 0) scale(1);
    }

    to {
        transform:
            translate(-35px, 30px)
            scale(1.12);
    }
}


/* Hero rings */

.hero::after {
    content: "";

    position: absolute;

    width: 240px;
    height: 240px;

    right: -100px;
    top: -95px;

    border-radius: 50%;

    border:
        1px solid rgba(92,200,255,.12);

    box-shadow:
        0 0 0 28px rgba(92,200,255,.025),
        0 0 0 56px rgba(92,200,255,.018),
        0 0 0 84px rgba(92,200,255,.012);

    pointer-events: none;
}

.hero > * {
    position: relative;
    z-index: 2;
}

.hero-kicker {
    color: #54d6ff !important;

    font-size: .68rem;

    font-weight: 850;

    letter-spacing: 1.8px;

    text-transform: uppercase;
}

.hero-title {
    font-size: 1.75rem;

    font-weight: 900;

    margin: .32rem 0;

    letter-spacing: -.4px;

    background:
        linear-gradient(
            90deg,
            #ffffff,
            #9be8ff 52%,
            #b8aaff
        );

    -webkit-background-clip: text;
    background-clip: text;

    -webkit-text-fill-color: transparent;
}

.hero-description {
    color: #91abc1 !important;

    font-size: .87rem;

    max-width: 900px;
}

.warning {
    border-left:
        3px solid var(--yellow);

    background:
        linear-gradient(
            90deg,
            rgba(255,209,102,.085),
            rgba(255,209,102,.025)
        );

    padding:
        .7rem
        .95rem;

    border-radius: 10px;

    color: #f7e8ad !important;

    font-size: .77rem;

    margin-top: .9rem;

    box-shadow:
        inset 0 0 20px rgba(255,209,102,.025);
}

.warning * {
    color: #f7e8ad !important;
}


/* =========================================================
   PAGE HEADERS
   ========================================================= */

.page-kicker {
    color: var(--cyan) !important;

    font-size: .67rem;

    font-weight: 850;

    letter-spacing: 1.8px;

    text-transform: uppercase;

    margin-bottom: .15rem;
}

.page-title {
    color: #f5f9ff !important;

    font-size: 2.05rem;

    font-weight: 900;

    line-height: 1.08;

    letter-spacing: -.7px;

    margin-bottom: .3rem;
}

.page-description {
    color: #8da7bc !important;

    font-size: .87rem;

    margin-bottom: 1.1rem;
}


/* =========================================================
   GLASS CARDS
   ========================================================= */

.card {
    position: relative;

    overflow: hidden;

    border:
        1px solid rgba(92,200,255,.13);

    border-radius: 16px;

    padding:
        1.05rem
        1.1rem;

    background:
        linear-gradient(
            145deg,
            rgba(15, 36, 61, .72),
            rgba(7, 18, 34, .65)
        );

    margin-bottom: .7rem;

    box-shadow:
        var(--glass-shadow);

    backdrop-filter:
        blur(18px);

    -webkit-backdrop-filter:
        blur(18px);

    transition:
        transform .22s ease,
        border-color .22s ease,
        box-shadow .22s ease;
}

.card::before {
    content: "";

    position: absolute;

    top: 0;
    left: -100%;

    width: 70%;
    height: 1px;

    background:
        linear-gradient(
            90deg,
            transparent,
            rgba(92,200,255,.75),
            transparent
        );

    transition:
        left .65s ease;
}

.card:hover::before {
    left: 130%;
}

.card:hover {
    transform:
        translateY(-4px);

    border-color:
        rgba(92,200,255,.30);

    box-shadow:
        0 25px 60px rgba(0,0,0,.30),
        0 0 25px rgba(92,200,255,.045),
        inset 0 1px 0 rgba(255,255,255,.06);
}

.card-title {
    color: #6edaff !important;

    font-size: .68rem;

    font-weight: 850;

    letter-spacing: 1.05px;

    text-transform: uppercase;

    margin-bottom: .28rem;
}

.card-value {
    color: #f5f9ff !important;

    font-size: 1.38rem;

    font-weight: 850;
}

.card-note {
    color: #829bb1 !important;

    font-size: .74rem;

    margin-top: .2rem;
}


/* =========================================================
   METRIC CARDS
   ========================================================= */

[data-testid="stMetric"] {
    position: relative;

    overflow: hidden;

    background:
        linear-gradient(
            145deg,
            rgba(16, 39, 65, .82),
            rgba(7, 19, 36, .72)
        ) !important;

    border:
        1px solid rgba(92,200,255,.17) !important;

    border-radius:
        15px !important;

    padding:
        .85rem
        .95rem !important;

    box-shadow:
        0 15px 40px rgba(0,0,0,.20),
        inset 0 1px 0 rgba(255,255,255,.045);

    backdrop-filter:
        blur(16px);

    -webkit-backdrop-filter:
        blur(16px);

    transition:
        transform .2s ease,
        border-color .2s ease,
        box-shadow .2s ease;
}

[data-testid="stMetric"]::after {
    content: "";

    position: absolute;

    width: 100px;
    height: 100px;

    right: -55px;
    top: -55px;

    border-radius: 50%;

    background:
        radial-gradient(
            circle,
            rgba(84,214,255,.13),
            transparent 68%
        );

    pointer-events: none;
}

[data-testid="stMetric"]:hover {
    transform:
        translateY(-4px);

    border-color:
        rgba(92,200,255,.42) !important;

    box-shadow:
        0 20px 50px rgba(0,0,0,.28),
        0 0 28px rgba(84,214,255,.07);
}

[data-testid="stMetricLabel"] {
    color: #8ca8bd !important;

    font-size: .73rem !important;
}

[data-testid="stMetricValue"] {
    color: #f4f9ff !important;

    font-weight: 900 !important;
}

[data-testid="stMetricDelta"] {
    font-weight: 750 !important;
}


/* =========================================================
   BUTTONS — GLASS + SHINE
   ========================================================= */

.stButton > button,
.stDownloadButton > button {
    position: relative;

    overflow: hidden;

    min-height: 40px;

    border-radius:
        11px !important;

    border:
        1px solid rgba(92,200,255,.22) !important;

    background:
        linear-gradient(
            135deg,
            rgba(16, 45, 73, .82),
            rgba(8, 25, 46, .76)
        ) !important;

    color:
        #eef8ff !important;

    box-shadow:
        0 9px 28px rgba(0,0,0,.18),
        inset 0 1px 0 rgba(255,255,255,.055);

    backdrop-filter:
        blur(12px);

    -webkit-backdrop-filter:
        blur(12px);

    transition:
        transform .18s ease,
        border-color .18s ease,
        box-shadow .18s ease,
        background .18s ease;
}

.stButton > button::before,
.stDownloadButton > button::before {
    content: "";

    position: absolute;

    top: 0;
    left: -130%;

    width: 65%;
    height: 100%;

    background:
        linear-gradient(
            90deg,
            transparent,
            rgba(255,255,255,.14),
            transparent
        );

    transform:
        skewX(-20deg);

    transition:
        left .65s ease;
}

.stButton > button:hover::before,
.stDownloadButton > button:hover::before {
    left: 140%;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    transform:
        translateY(-2px);

    border-color:
        rgba(92,200,255,.60) !important;

    background:
        linear-gradient(
            135deg,
            rgba(19, 76, 112, .90),
            rgba(42, 47, 105, .80)
        ) !important;

    box-shadow:
        0 13px 35px rgba(0,0,0,.27),
        0 0 25px rgba(92,200,255,.10);
}

.stButton > button:active,
.stDownloadButton > button:active {
    transform:
        translateY(1px)
        scale(.985);
}


/* Primary gradient button */

.stButton > button[kind="primary"] {
    background:
        linear-gradient(
            135deg,
            #0aa9ed 0%,
            #2678f2 48%,
            #785cf5 100%
        ) !important;

    border:
        1px solid rgba(151,232,255,.65) !important;

    color:
        #ffffff !important;

    box-shadow:
        0 10px 35px rgba(36,152,255,.26),
        0 0 25px rgba(120,92,245,.10),
        inset 0 1px 0 rgba(255,255,255,.22);
}

.stButton > button[kind="primary"]:hover {
    background:
        linear-gradient(
            135deg,
            #19b8f5,
            #3189ff,
            #886eff
        ) !important;

    box-shadow:
        0 15px 45px rgba(36,152,255,.35),
        0 0 35px rgba(120,92,245,.17);
}


/* =========================================================
   INPUTS
   ========================================================= */

[data-baseweb="input"],
[data-baseweb="base-input"] {
    background:
        rgba(8, 24, 43, .72) !important;

    border-radius:
        10px !important;
}

input,
textarea {
    background:
        rgba(8,24,43,.72) !important;

    color:
        #edf7ff !important;

    border:
        1px solid rgba(92,200,255,.16) !important;

    border-radius:
        10px !important;

    transition:
        border-color .2s ease,
        box-shadow .2s ease;
}

input:focus,
textarea:focus {
    border-color:
        rgba(92,200,255,.55) !important;

    box-shadow:
        0 0 0 3px rgba(92,200,255,.08),
        0 0 20px rgba(92,200,255,.05);
}


/* =========================================================
   SELECT BOXES
   ========================================================= */

[data-baseweb="select"] > div {
    background:
        rgba(8, 24, 43, .75) !important;

    color:
        #eaf4ff !important;

    border:
        1px solid rgba(92,200,255,.18) !important;

    border-radius:
        10px !important;

    transition:
        border-color .2s ease,
        box-shadow .2s ease;
}

[data-baseweb="select"] > div:hover {
    border-color:
        rgba(92,200,255,.48) !important;

    box-shadow:
        0 0 20px rgba(92,200,255,.06);
}

[data-baseweb="popover"] * {
    background:
        #09192c !important;

    color:
        #eaf4ff !important;
}


/* =========================================================
   SLIDERS
   ========================================================= */

[data-testid="stSlider"] [role="slider"] {
    background:
        linear-gradient(
            135deg,
            #54d6ff,
            #8b7cff
        ) !important;

    border:
        2px solid #eafaff !important;

    box-shadow:
        0 0 18px rgba(84,214,255,.32);
}

[data-testid="stSlider"] [data-baseweb="slider"] {
    padding-top: .5rem;
}

[data-testid="stSlider"] [data-baseweb="slider"] > div {
    background:
        rgba(255,255,255,.08);
}


/* =========================================================
   TABS
   ========================================================= */

button[data-baseweb="tab"] {
    color:
        #849db3 !important;

    background:
        transparent !important;

    border-radius:
        9px 9px 0 0;

    transition:
        color .2s ease,
        background .2s ease;
}

button[data-baseweb="tab"]:hover {
    color:
        #cbeeff !important;

    background:
        rgba(92,200,255,.045) !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color:
        #5cd9ff !important;

    font-weight:
        800 !important;

    background:
        linear-gradient(
            180deg,
            rgba(92,200,255,.09),
            transparent
        ) !important;
}

[data-baseweb="tab-highlight"] {
    background:
        linear-gradient(
            90deg,
            #54d6ff,
            #8b7cff
        ) !important;

    height:
        2px !important;

    box-shadow:
        0 0 12px rgba(84,214,255,.45);
}


/* =========================================================
   DATAFRAME / TABLES
   ========================================================= */

[data-testid="stDataFrame"] {
    border:
        1px solid rgba(92,200,255,.15);

    border-radius:
        14px;

    overflow:
        hidden;

    box-shadow:
        0 15px 40px rgba(0,0,0,.20);
}


/* =========================================================
   CHART CONTAINERS
   ========================================================= */

[data-testid="stPlotlyChart"] {
    position: relative;

    padding:
        .3rem;

    border:
        1px solid rgba(92,200,255,.10);

    border-radius:
        16px;

    background:
        linear-gradient(
            145deg,
            rgba(10,29,49,.42),
            rgba(5,15,29,.28)
        );

    box-shadow:
        inset 0 1px 0 rgba(255,255,255,.025),
        0 14px 45px rgba(0,0,0,.13);

    backdrop-filter:
        blur(12px);

    -webkit-backdrop-filter:
        blur(12px);

    transition:
        border-color .2s ease,
        transform .2s ease;
}

[data-testid="stPlotlyChart"]:hover {
    border-color:
        rgba(92,200,255,.20);

    transform:
        translateY(-2px);
}


/* =========================================================
   FILE UPLOADER — GLASS
   ========================================================= */

[data-testid="stFileUploader"] {
    border:
        1px solid rgba(92,200,255,.18);

    border-radius:
        15px;

    padding:
        .45rem;

    background:
        linear-gradient(
            145deg,
            rgba(12,31,53,.70),
            rgba(7,18,34,.60)
        );

    box-shadow:
        0 15px 40px rgba(0,0,0,.18);

    backdrop-filter:
        blur(15px);

    -webkit-backdrop-filter:
        blur(15px);
}

[data-testid="stFileUploader"] section {
    background:
        transparent !important;

    border:
        none !important;
}


/* =========================================================
   ALERTS
   ========================================================= */

[data-testid="stAlert"] {
    border-radius:
        12px !important;

    border:
        1px solid rgba(92,200,255,.14) !important;

    box-shadow:
        0 12px 35px rgba(0,0,0,.15);

    backdrop-filter:
        blur(12px);
}


/* =========================================================
   EXPANDERS
   ========================================================= */

[data-testid="stExpander"] {
    border:
        1px solid rgba(92,200,255,.13) !important;

    border-radius:
        13px !important;

    background:
        rgba(8,23,42,.55) !important;

    box-shadow:
        0 10px 35px rgba(0,0,0,.15);

    overflow:
        hidden;
}


/* =========================================================
   DIVIDERS
   ========================================================= */

.section-divider {
    height:
        1px;

    background:
        linear-gradient(
            90deg,
            transparent,
            rgba(84,214,255,.30),
            rgba(139,124,255,.25),
            transparent
        );

    margin:
        1.25rem 0;

    box-shadow:
        0 0 12px rgba(84,214,255,.06);
}


/* =========================================================
   FOOTER
   ========================================================= */

.footer {
    border-top:
        1px solid rgba(92,200,255,.12);

    margin-top:
        2.5rem;

    padding-top:
        1.2rem;

    text-align:
        center;

    color:
        #617b91 !important;

    font-size:
        .72rem;

    background:
        linear-gradient(
            90deg,
            transparent,
            rgba(92,200,255,.025),
            transparent
        );
}


/* =========================================================
   SCROLLBAR
   ========================================================= */

::-webkit-scrollbar {
    width: 9px;
    height: 9px;
}

::-webkit-scrollbar-track {
    background:
        #020611;
}

::-webkit-scrollbar-thumb {
    background:
        linear-gradient(
            180deg,
            #155d83,
            #5148a0
        );

    border-radius:
        20px;

    border:
        2px solid #020611;
}

::-webkit-scrollbar-thumb:hover {
    background:
        linear-gradient(
            180deg,
            #32bce9,
            #806cff
        );
}


/* =========================================================
   RESPONSIVE
   ========================================================= */

@media (max-width: 1100px) {

    .block-container {
        padding-top: 1.7rem;
    }

    .page-title {
        font-size: 1.7rem;
    }

    .hero-title {
        font-size: 1.5rem;
    }
}


@media (max-width: 900px) {

    .block-container {
        padding:
            1.2rem
            .8rem
            3rem;
    }

    .page-title {
        font-size: 1.5rem;
    }

    .hero-title {
        font-size: 1.3rem;
    }

    .hero {
        padding:
            1.2rem;
    }

    [data-testid="stMetric"] {
        margin-bottom:
            .55rem;
    }
}


/* =========================================================
   REDUCED MOTION ACCESSIBILITY
   ========================================================= */

@media (prefers-reduced-motion: reduce) {

    *,
    *::before,
    *::after {
        animation-duration:
            .01ms !important;

        animation-iteration-count:
            1 !important;

        transition-duration:
            .01ms !important;

        scroll-behavior:
            auto !important;
    }
}

</style>
""",
    unsafe_allow_html=True,
)


/* =========================================================
   GLOBAL
   ========================================================= */

:root {
    --bg: #06111f;
    --bg2: #081827;
    --panel: #0c1b2d;
    --panel2: #10243a;
    --border: #203b54;
    --border2: #2a526f;
    --text: #eaf4ff;
    --muted: #91aac0;
    --cyan: #5cc8ff;
    --cyan2: #1597d1;
    --green: #42d392;
    --yellow: #ffd166;
    --red: #ff6b6b;
    --purple: #9b8cff;
}

.stApp {
    background:
        radial-gradient(
            circle at 75% -10%,
            rgba(28, 139, 194, .13),
            transparent 35%
        ),
        linear-gradient(135deg, #06111f 0%, #071523 50%, #06111f 100%);
    color: var(--text);
}

.block-container {
    max-width: 1550px;
    padding-top: 2.5rem;
    padding-bottom: 3rem;
}

[data-testid="stHeader"] {
    background: rgba(6,17,31,.9) !important;
}

[data-testid="stHeader"] * {
    color: #8da7bc !important;
    fill: #8da7bc !important;
}

.stApp,
.stApp p,
.stApp label,
.stApp li,
.stApp h1,
.stApp h2,
.stApp h3,
.stApp h4,
.stApp h5,
.stApp span,
[data-testid="stMarkdownContainer"] *,
[data-testid="stCaptionContainer"] *,
[data-testid="stMetricValue"] *,
[data-testid="stMetricLabel"] * {
    color: var(--text) !important;
}


/* =========================================================
   SIDEBAR
   ========================================================= */

[data-testid="stSidebar"] {
    background:
        linear-gradient(
            180deg,
            #06111f 0%,
            #071523 60%,
            #06101c 100%
        ) !important;

    border-right: 1px solid #162c40;
}

[data-testid="stSidebar"] * {
    color: var(--text) !important;
}

.sidebar-brand {
    padding: .8rem .2rem 1rem .2rem;
}

.sidebar-brand .brand-icon {
    display: inline-flex;
    width: 42px;
    height: 42px;
    align-items: center;
    justify-content: center;
    border-radius: 12px;
    background: linear-gradient(135deg, #0c8dcc, #1551a8);
    font-size: 1.35rem;
    box-shadow: 0 8px 25px rgba(21,151,209,.25);
}

.sidebar-brand .brand-title {
    font-size: 1.03rem;
    font-weight: 800;
    margin-top: .65rem;
}

.sidebar-brand .brand-subtitle {
    color: #7894aa !important;
    font-size: .73rem;
    line-height: 1.45;
}

.sidebar-section {
    color: var(--cyan) !important;
    font-size: .68rem;
    font-weight: 800;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin: 1rem 0 .45rem;
}

[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background: #0b1b2d !important;
    border: 1px solid #28465f !important;
    border-radius: 10px !important;
}

[data-testid="stSidebar"] [data-baseweb="select"] * {
    color: #eaf4ff !important;
}

[data-testid="stSidebar"] hr {
    border-color: #1b344a !important;
}


/* =========================================================
   NAVIGATION
   ========================================================= */

[data-testid="stSidebar"] div[role="radiogroup"] {
    gap: .28rem;
}

[data-testid="stSidebar"] label[data-baseweb="radio"] {
    width: 100%;
    background: transparent !important;
    border: 1px solid transparent !important;
    border-radius: 10px !important;
    padding: .48rem .65rem !important;
    margin: 0 !important;
    transition:
        background .15s ease,
        border-color .15s ease,
        transform .15s ease;
}

[data-testid="stSidebar"] label[data-baseweb="radio"]:hover {
    background: #10263a !important;
    border-color: #24445d !important;
    transform: translateX(2px);
}

[data-testid="stSidebar"] label[data-baseweb="radio"]:has(input:checked) {
    background:
        linear-gradient(
            90deg,
            rgba(26,124,174,.30),
            rgba(14,45,68,.65)
        ) !important;
    border-color: #2f789d !important;
    box-shadow: inset 3px 0 0 #5cc8ff;
}

[data-testid="stSidebar"] label[data-baseweb="radio"]:has(input:checked) p {
    color: #65ceff !important;
    font-weight: 750 !important;
}

[data-testid="stSidebar"] label[data-baseweb="radio"] p {
    color: #afc4d7 !important;
    font-size: .82rem !important;
    margin: 0 !important;
}

[data-testid="stSidebar"] label[data-baseweb="radio"] > div:first-child {
    display: none !important;
}


/* =========================================================
   HERO
   ========================================================= */

.hero {
    position: relative;
    overflow: hidden;
    padding: 1.45rem 1.55rem;
    border: 1px solid #23445c;
    border-radius: 20px;
    background:
        radial-gradient(
            circle at 90% 20%,
            rgba(92,200,255,.12),
            transparent 30%
        ),
        linear-gradient(135deg, #10263c, #0a1929);
    margin-bottom: 1.2rem;
    box-shadow: 0 15px 45px rgba(0,0,0,.18);
}

.hero:after {
    content: "";
    position: absolute;
    width: 220px;
    height: 220px;
    right: -90px;
    top: -100px;
    border-radius: 50%;
    border: 1px solid rgba(92,200,255,.13);
    box-shadow:
        0 0 0 30px rgba(92,200,255,.025),
        0 0 0 60px rgba(92,200,255,.02);
}

.hero-kicker {
    color: #5cc8ff !important;
    font-size: .69rem;
    font-weight: 800;
    letter-spacing: 1.7px;
    text-transform: uppercase;
}

.hero-title {
    font-size: 1.65rem;
    font-weight: 850;
    margin: .3rem 0;
}

.hero-description {
    color: #8fa9be !important;
    font-size: .86rem;
    max-width: 900px;
}

.warning {
    border-left: 3px solid var(--yellow);
    background: rgba(255,209,102,.07);
    padding: .65rem .9rem;
    border-radius: 9px;
    color: #f7e8ad !important;
    font-size: .78rem;
    margin-top: .8rem;
}

.warning * {
    color: #f7e8ad !important;
}


/* =========================================================
   PAGE HEADERS
   ========================================================= */

.page-kicker {
    color: var(--cyan) !important;
    font-size: .68rem;
    font-weight: 850;
    letter-spacing: 1.7px;
    text-transform: uppercase;
    margin-bottom: .15rem;
}

.page-title {
    color: #f3f8fd !important;
    font-size: 2rem;
    font-weight: 850;
    line-height: 1.1;
    margin-bottom: .25rem;
}

.page-description {
    color: #8da7bc !important;
    font-size: .88rem;
    margin-bottom: 1.1rem;
}


/* =========================================================
   CARDS / METRICS
   ========================================================= */

.card {
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1rem 1.05rem;
    background:
        linear-gradient(145deg, #0e2034, #0a1929);
    margin-bottom: .65rem;
    box-shadow: 0 8px 24px rgba(0,0,0,.11);
}

.card-title {
    color: #6ed2ff !important;
    font-size: .7rem;
    font-weight: 800;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: .25rem;
}

.card-value {
    color: #f2f8ff !important;
    font-size: 1.35rem;
    font-weight: 800;
}

.card-note {
    color: #809bb0 !important;
    font-size: .75rem;
    margin-top: .2rem;
}

[data-testid="stMetric"] {
    background:
        linear-gradient(145deg, #10243a, #0b1a2b) !important;
    border: 1px solid #25475f !important;
    border-radius: 14px !important;
    padding: .8rem .9rem !important;
    box-shadow: 0 7px 22px rgba(0,0,0,.13);
    transition: transform .15s ease, border-color .15s ease;
}

[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    border-color: #3e7899 !important;
}

[data-testid="stMetricLabel"] {
    color: #8ca7ba !important;
    font-size: .75rem !important;
}

[data-testid="stMetricValue"] {
    color: #f3f8fd !important;
    font-weight: 800 !important;
}


/* =========================================================
   BUTTONS / INPUTS
   ========================================================= */

.stButton > button,
.stDownloadButton > button {
    border-radius: 9px !important;
    border: 1px solid #28516d !important;
    background: #0d2236 !important;
    color: #eaf4ff !important;
    transition: all .15s ease;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    background: #12334c !important;
    border-color: #5cc8ff !important;
}

.stButton > button[kind="primary"] {
    background:
        linear-gradient(135deg, #1498d4, #0874a7) !important;
    border-color: #47c5f2 !important;
    color: white !important;
}

[data-baseweb="input"],
[data-baseweb="base-input"],
input,
textarea {
    background: #0c1b2d !important;
    color: #eaf4ff !important;
    border-color: #28465f !important;
}

[data-baseweb="select"] > div {
    background: #0c1b2d !important;
    color: #eaf4ff !important;
    border-color: #28465f !important;
}

[data-baseweb="popover"] * {
    background: #0d1c2e !important;
    color: #eaf4ff !important;
}


/* =========================================================
   TABS
   ========================================================= */

button[data-baseweb="tab"] {
    color: #8fa8bb !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #5cc8ff !important;
}


/* =========================================================
   TABLES
   ========================================================= */

[data-testid="stDataFrame"] {
    border: 1px solid #203b54;
    border-radius: 12px;
    overflow: hidden;
}


/* =========================================================
   ALERTS
   ========================================================= */

[data-testid="stAlert"] {
    border-radius: 11px !important;
}


/* =========================================================
   FOOTER
   ========================================================= */

.footer {
    border-top: 1px solid #1d3549;
    margin-top: 2rem;
    padding-top: 1rem;
    text-align: center;
    color: #617c91 !important;
    font-size: .72rem;
}

.small-note {
    color: #7f9bb0 !important;
    font-size: .77rem;
}

.section-divider {
    height: 1px;
    background:
        linear-gradient(
            90deg,
            transparent,
            #29485f,
            transparent
        );
    margin: 1.1rem 0;
}


/* =========================================================
   MOBILE
   ========================================================= */

@media (max-width: 900px) {
    .block-container {
        padding-top: 1.4rem;
    }

    .page-title {
        font-size: 1.55rem;
    }

    .hero-title {
        font-size: 1.35rem;
    }
}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# CONSTANTS
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

PAGE_META = {
    "Executive Dashboard": (
        "🏠",
        "Executive Overview",
        "Five-year financial performance, profitability, liquidity and analytical health.",
    ),
    "Trends Explorer": (
        "📈",
        "Financial Trends",
        "Explore historical movements, indexed performance and relationships between metrics.",
    ),
    "Ratio Scorecard": (
        "🎯",
        "Ratio Scorecard",
        "A transparent educational scorecard covering liquidity, solvency and efficiency.",
    ),
    "DuPont Analysis": (
        "🧩",
        "DuPont Analysis",
        "Decompose ROE into profitability, asset efficiency and financial leverage.",
    ),
    "Growth Analysis": (
        "🚀",
        "Growth Analysis",
        "Compare CAGR, total growth and year-over-year changes across key indicators.",
    ),
    "Vertical Analysis": (
        "📊",
        "Vertical Analysis",
        "Examine income-statement and balance-sheet composition using common-size data.",
    ),
    "Peer Comparison": (
        "⚖️",
        "Peer Comparison",
        "Compare financial indicators across the companies in the active dataset.",
    ),
    "Industry / PESTEL": (
        "🌐",
        "Industry / PESTEL",
        "Review external forces affecting Pakistani exploration and production companies.",
    ),
    "Risk Dashboard": (
        "🛡️",
        "Risk Dashboard",
        "Review transparent indicators for leverage, liquidity, margins and data quality.",
    ),
    "DCF & Monte Carlo": (
        "💰",
        "DCF & Monte Carlo",
        "Explore discounted cash flow assumptions, sensitivities and simulated valuation ranges.",
    ),
    "Relative Valuation": (
        "💹",
        "Relative Valuation",
        "Compare P/E, EPS, dividend yield and ROE across the active peer set.",
    ),
    "Scenario Analysis": (
        "🔮",
        "Scenario Analysis",
        "Explore how alternative growth and margin assumptions affect future revenue and EPS.",
    ),
    "Data Integrity": (
        "🔍",
        "Data Integrity",
        "Reconcile submitted figures, verified FY2025 values and internal financial relationships.",
    ),
    "Import & Export": (
        "📁",
        "Import & Export",
        "Import company datasets and export analysis results for academic use.",
    ),
    "References": (
        "📚",
        "References",
        "Review company sources and the recommended production data architecture.",
    ),
}


# ============================================================
# DATA HELPERS
# ============================================================

def clean_number(value: Any, default: float = np.nan) -> float:
    if value is None:
        return default

    try:
        if isinstance(value, str):
            value = (
                value.replace(",", "")
                .replace("%", "")
                .strip()
            )

        result = float(value)

        return result if np.isfinite(result) else default

    except Exception:
        return default


def safe_div(
    a: Any,
    b: Any,
    default: float = np.nan,
) -> float:

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
    arr = pd.to_numeric(
        pd.Series(values),
        errors="coerce",
    ).to_numpy(dtype=float)

    return (
        float(np.nanmean(arr))
        if np.isfinite(arr).any()
        else np.nan
    )


def light(score_value: float) -> str:
    score_value = clean_number(score_value)

    if not np.isfinite(score_value):
        return "⚪ N/A"

    if score_value >= 70:
        return "🟢 Strong"

    if score_value >= 45:
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

    return {
        "name": name,
        "description": desc,
        "historical": dict(zip(HK, rows)),
        "verified2025": ver or {},
        "vertical": vert or {},
        "sources": src,
    }


def validate_company_structure(
    company: Dict[str, Any],
) -> Tuple[bool, str]:

    if not isinstance(company, dict):
        return False, "Company record must be a JSON object."

    required = {
        "name",
        "historical",
        "verified2025",
        "vertical",
        "sources",
    }

    missing = required - set(company)

    if missing:
        return (
            False,
            "Missing company fields: "
            + ", ".join(sorted(missing)),
        )

    hist = company["historical"]

    if not isinstance(hist, dict):
        return False, "historical must be an object."

    for key in HK:

        if key not in hist:
            return False, f"Missing historical metric: {key}"

        if (
            not isinstance(hist[key], list)
            or len(hist[key]) != len(YEARS)
        ):
            return (
                False,
                f"{key} must contain exactly {len(YEARS)} values.",
            )

        for value in hist[key]:
            if not np.isfinite(clean_number(value)):
                return (
                    False,
                    f"{key} contains an invalid numeric value.",
                )

    return True, ""


def vget(
    company: Dict[str, Any],
    key: str,
) -> float:

    hist = company.get("historical", {})
    verified = company.get("verified2025", {})

    if key in verified:
        return clean_number(verified[key])

    if key == "eps" and "epsRestated" in verified:
        return clean_number(verified["epsRestated"])

    values = hist.get(key, [])

    if values:
        return clean_number(values[-1])

    return np.nan


def hdf(company: Dict[str, Any]) -> pd.DataFrame:

    hist = company["historical"]

    data = {"Year": YEARS}

    for key in HK:
        data[LBL[key]] = pd.to_numeric(
            pd.Series(hist[key]),
            errors="coerce",
        ).to_numpy()

    return pd.DataFrame(data).set_index("Year")


def shares(company: Dict[str, Any]) -> float:
    return safe_div(
        vget(company, "netIncome"),
        vget(company, "eps"),
    )


def score(metric: str, value: Any) -> float:

    value = clean_number(value)

    if metric not in RULES or not np.isfinite(value):
        return np.nan

    threshold, direction = RULES[metric]

    if direction == "hi":
        return float(
            np.clip(
                70 * value / threshold,
                0,
                100,
            )
        )

    if value <= threshold:
        return 100.0

    return float(
        np.clip(
            100 * threshold / value,
            0,
            100,
        )
    )


def scorecard(company: Dict[str, Any]) -> pd.DataFrame:
    """
    IMPORTANT:
    pd.to_numeric(list) can return a NumPy array.
    Wrapping it in pd.Series ensures .iloc works.
    """

    hist = company["historical"]

    rows = []

    for key, (benchmark, direction) in RULES.items():

        values = pd.Series(
            pd.to_numeric(
                hist.get(key, []),
                errors="coerce",
            )
        )

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
                (
                    cur - prev
                    if np.isfinite(cur)
                    and np.isfinite(prev)
                    else np.nan
                ),
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


# ============================================================
# STYLING HELPERS
# ============================================================

def style_numeric(
    df: pd.DataFrame,
    decimals: int = 2,
):

    try:
        return df.style.format(
            f"{{:,.{decimals}f}}"
        )

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

        if (
            MATPLOTLIB_AVAILABLE
            and "Score" in df.columns
        ):
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
# PAGE UI HELPERS
# ============================================================

def page_header(
    page_name: str,
    company_symbol: Optional[str] = None,
):

    icon, title, description = PAGE_META[page_name]

    st.markdown(
        f"""
        <div class="page-kicker">
            {icon} {page_name}
        </div>

        <div class="page-title">
            {title}
        </div>

        <div class="page-description">
            {description}
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_title(
    title: str,
    subtitle: str = "",
):

    subtitle_html = (
        f'<div class="small-note">{subtitle}</div>'
        if subtitle
        else ""
    )

    st.markdown(
        f"""
        <div style="margin-top:.8rem;margin-bottom:.55rem">
            <div style="
                font-size:1.05rem;
                font-weight:800;
                color:#edf7ff;
            ">
                {title}
            </div>
            {subtitle_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(
    label: str,
    value: str,
    note: str = "",
):

    st.markdown(
        f"""
        <div class="card">
            <div class="card-title">{label}</div>
            <div class="card-value">{value}</div>
            <div class="card-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def style_fig(
    fig: go.Figure,
    height: int = 380,
    title: Optional[str] = None,
):

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=height,
        margin=dict(
            l=10,
            r=10,
            t=55,
            b=10,
        ),
        font=dict(
            family="Inter, Arial, sans-serif",
            color="#dbeafe",
        ),
        title=dict(
            text=title,
            font=dict(
                size=15,
                color="#eaf4ff",
            ),
        ),
        legend=dict(
            orientation="h",
            y=1.12,
            font=dict(size=11),
        ),
        hoverlabel=dict(
            bgcolor="#0b1d30",
            bordercolor="#2a526f",
            font_color="#eaf4ff",
        ),
    )

    fig.update_xaxes(
        gridcolor="rgba(120,160,190,.10)",
        zerolinecolor="rgba(120,160,190,.15)",
    )

    fig.update_yaxes(
        gridcolor="rgba(120,160,190,.10)",
        zerolinecolor="rgba(120,160,190,.15)",
    )

    return fig


def show(
    fig: go.Figure,
    height: int = 380,
    title: Optional[str] = None,
):

    st.plotly_chart(
        style_fig(
            fig,
            height,
            title,
        ),
        width="stretch",
        config={
            "displaylogo": False,
            "responsive": True,
        },
    )


def lines(
    df: pd.DataFrame,
    cols: List[str],
    title: str,
    height: int = 380,
    bar: bool = False,
):

    fig = go.Figure()

    colors = [
        "#5cc8ff",
        "#42d392",
        "#9b8cff",
        "#ffd166",
        "#ff7b72",
        "#4dd0e1",
    ]

    for i, col in enumerate(cols):

        if col not in df.columns:
            continue

        x = df.index
        y = pd.to_numeric(
            df[col],
            errors="coerce",
        )

        color = colors[i % len(colors)]

        if bar:
            fig.add_trace(
                go.Bar(
                    x=x,
                    y=y,
                    name=col,
                    marker_color=color,
                )
            )

        else:
            fig.add_trace(
                go.Scatter(
                    x=x,
                    y=y,
                    name=col,
                    mode="lines+markers",
                    line=dict(
                        width=3,
                        color=color,
                    ),
                    marker=dict(
                        size=7,
                        color=color,
                    ),
                )
            )

    if not fig.data:
        st.info("No valid data available for this chart.")
        return

    if bar:
        fig.update_layout(barmode="group")

    show(
        fig,
        height,
        title,
    )


# ============================================================
# DCF
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

    if not all(
        np.isfinite(clean_number(x))
        for x in inputs
    ):
        raise ValueError(
            "DCF inputs contain invalid numeric values."
        )

    if rev0 <= 0:
        raise ValueError(
            "Revenue must be positive."
        )

    if shares_outstanding <= 0:
        raise ValueError(
            "Shares outstanding must be positive."
        )

    if wacc <= terminal_growth:
        raise ValueError(
            "WACC must be greater than terminal growth."
        )

    if years < 1:
        raise ValueError(
            "Forecast horizon must be at least one year."
        )

    revenue = rev0
    pv = 0.0
    rows = []

    for t in range(1, years + 1):

        revenue *= 1 + growth / 100

        ebit = (
            revenue
            * margin
            / 100
        )

        fcf = (
            ebit
            * (1 - tax / 100)
            - revenue
            * (capex + wc)
            / 100
        )

        discount_factor = (
            1 + wacc / 100
        ) ** t

        discounted_fcf = (
            fcf / discount_factor
        )

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
        terminal_fcf
        * (1 + terminal_growth / 100)
        / ((wacc - terminal_growth) / 100)
    )

    pv_terminal = (
        terminal_value
        / (1 + wacc / 100) ** years
    )

    enterprise_value = (
        pv + pv_terminal
    )

    equity_value = (
        enterprise_value - net_debt
    )

    value_per_share = (
        equity_value
        / shares_outstanding
    )

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
            (
                "PSX company page",
                "https://dps.psx.com.pk/company/OGDC",
            ),
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
            (
                "PSX company page",
                "https://dps.psx.com.pk/company/PPL",
            ),
            (
                "PPL Annual Report 2025",
                "https://www.ppl.com.pk/content/annual-report-2025",
            ),
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
            (
                "PSX company page",
                "https://dps.psx.com.pk/company/MARI",
            ),
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
# SESSION DATA
# ============================================================

if "custom" not in st.session_state:
    st.session_state.custom = {}


# ============================================================
# VALIDATE ACTIVE DATASET
# ============================================================

ALL_RAW = {
    **DEMO,
    **st.session_state.custom,
}

ALL: Dict[str, Dict[str, Any]] = {}

for symbol, company_data in ALL_RAW.items():

    ok, reason = validate_company_structure(
        company_data
    )

    if ok:
        ALL[symbol] = company_data

    else:
        st.warning(
            f"Skipping invalid company **{symbol}**: {reason}"
        )


if not ALL:
    st.error(
        "No valid company data is available."
    )

    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div class="sidebar-brand">

            <div class="brand-icon">
                📊
            </div>

            <div class="brand-title">
                PSX Financial Lab
            </div>

            <div class="brand-subtitle">
                COMSATS University Islamabad<br>
                Five-Year Academic Analysis Engine
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sidebar-section">Company</div>',
        unsafe_allow_html=True,
    )

    symbols = list(ALL.keys())

    sel = st.selectbox(
        "Company",
        symbols,
        format_func=lambda x: (
            f"{x} — {ALL[x]['name']}"
        ),
        label_visibility="collapsed",
    )

    st.markdown(
        '<div class="sidebar-section">Analysis Modules</div>',
        unsafe_allow_html=True,
    )

    page = st.radio(
        "Navigation",
        PAGES,
        format_func=lambda p: (
            f"{PAGE_META[p][0]}  {p}"
        ),
        label_visibility="collapsed",
        key="main_navigation",
    )

    st.markdown(
        '<div class="section-divider"></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="small-note">
        <b>Dataset:</b> FY2021–FY2025<br>
        <b>Mode:</b> Academic / illustrative<br>
        <b>Market feed:</b> Static demo data
        </div>
        """,
        unsafe_allow_html=True,
    )


company = ALL[sel]
hist = company["historical"]
verified = company["verified2025"]
D = hdf(company)


# ============================================================
# GLOBAL HERO
# ============================================================

icon, _, _ = PAGE_META[page]

st.markdown(
    f"""
    <div class="hero">

        <div class="hero-kicker">
            COMSATS UNIVERSITY ISLAMABAD
            • DEPARTMENT OF MANAGEMENT SCIENCES
        </div>

        <div class="hero-title">
            {icon} PSX Five-Year Financial Analysis Dashboard
        </div>

        <div class="hero-description">
            {sel} — {company["name"]}
        </div>

        <div class="warning">
            <b>Data-quality note:</b>
            submitted historical values and verified FY2025 snapshots
            are intentionally kept separate. Differences can result
            from restatements, consolidation, units or methodology.
            Review <b>Data Integrity</b> before using figures in a report.
        </div>

    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# EXECUTIVE DASHBOARD
# ============================================================

if page == "Executive Dashboard":

    page_header(page)

    st.caption(company["description"])

    sc = scorecard(company)

    health = safe_mean(sc["Score"])

    revenue_2025 = vget(company, "revenue")
    revenue_2024 = clean_number(
        hist["revenue"][-2]
    )

    pat_2025 = vget(company, "netIncome")
    pat_2024 = clean_number(
        hist["netIncome"][-2]
    )

    revenue_growth = pct_change(
        revenue_2025,
        revenue_2024,
    )

    pat_growth = pct_change(
        pat_2025,
        pat_2024,
    )

    k = st.columns(6)

    k[0].metric(
        "Revenue",
        f"{fmt(revenue_2025)}m",
        (
            f"{revenue_growth:+.1f}% YoY"
            if np.isfinite(revenue_growth)
            else "N/A"
        ),
    )

    k[1].metric(
        "PAT",
        f"{fmt(pat_2025)}m",
        (
            f"{pat_growth:+.1f}% YoY"
            if np.isfinite(pat_growth)
            else "N/A"
        ),
    )

    k[2].metric(
        "EPS",
        fmt(vget(company, "eps"), 2),
    )

    k[3].metric(
        "P/E",
        f"{fmt(vget(company, 'pe'), 2)}x",
    )

    k[4].metric(
        "ROE",
        f"{fmt(vget(company, 'roe'), 1)}%",
    )

    k[5].metric(
        "Health",
        (
            f"{fmt(health, 0)}/100"
            if np.isfinite(health)
            else "N/A"
        ),
        light(health),
    )

    st.markdown(
        '<div class="section-divider"></div>',
        unsafe_allow_html=True,
    )

    a, b = st.columns([1.7, 1])

    with a:

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=YEARS,
                y=hist["revenue"],
                name="Revenue",
                marker_color="#1597d1",
            )
        )

        fig.add_trace(
            go.Bar(
                x=YEARS,
                y=hist["netIncome"],
                name="Net income",
                marker_color="#42d392",
            )
        )

        fig.add_trace(
            go.Scatter(
                x=YEARS,
                y=hist["npm"],
                name="NPM %",
                yaxis="y2",
                mode="lines+markers",
                line=dict(
                    color="#ffd166",
                    width=3,
                ),
            )
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

        show(
            fig,
            390,
            "Scale & profitability",
        )

    with b:

        radar = sc.dropna(
            subset=["Score"]
        )

        if len(radar):

            fig = go.Figure(
                go.Scatterpolar(
                    r=(
                        radar["Score"].tolist()
                        + [radar["Score"].iloc[0]]
                    ),
                    theta=(
                        radar["Ratio"].tolist()
                        + [radar["Ratio"].iloc[0]]
                    ),
                    fill="toself",
                    line=dict(
                        color="#5cc8ff",
                        width=2,
                    ),
                    fillcolor="rgba(92,200,255,.18)",
                )
            )

            fig.update_layout(
                polar=dict(
                    bgcolor="rgba(0,0,0,0)",
                    radialaxis=dict(
                        range=[0, 100],
                        gridcolor="rgba(150,180,200,.15)",
                    ),
                )
            )

            show(
                fig,
                390,
                "Ratio health radar",
            )

        else:
            st.info(
                "Insufficient scorecard data."
            )

    section_title(
        "Automated commentary",
        "Descriptive observations generated from the supplied dataset.",
    )

    rev_cagr = cagr(
        hist["revenue"][0],
        hist["revenue"][-1],
    )

    ni_cagr = cagr(
        hist["netIncome"][0],
        hist["netIncome"][-1],
    )

    peak_ni = np.nanmax(
        pd.to_numeric(
            pd.Series(hist["netIncome"]),
            errors="coerce",
        )
    )

    current_ni = clean_number(
        hist["netIncome"][-1]
    )

    drawdown = pct_change(
        current_ni,
        peak_ni,
    )

    current_ratio = vget(
        company,
        "current",
    )

    de = vget(
        company,
        "debtEq",
    )

    interest = vget(
        company,
        "interest",
    )

    receivables_turn = vget(
        company,
        "receivablesTurn",
    )

    notes = []

    if np.isfinite(rev_cagr):
        notes.append(
            f"Revenue CAGR FY21–25 is **{rev_cagr:.1f}%**."
        )

    if np.isfinite(ni_cagr):
        notes.append(
            f"Net income CAGR FY21–25 is **{ni_cagr:.1f}%**."
        )

    if np.isfinite(drawdown):

        if drawdown < -0.1:

            notes.append(
                f"FY2025 net income is approximately "
                f"**{abs(drawdown):.1f}% above the five-year peak comparison "
                f"base**."
            )

        else:

            notes.append(
                "FY2025 net income is at or close to the five-year peak."
            )

    if np.isfinite(current_ratio):

        notes.append(
            f"FY2025 current ratio is **{current_ratio:.2f}x**, "
            "against the educational benchmark of 1.50x."
        )

    if (
        np.isfinite(de)
        and np.isfinite(interest)
    ):

        notes.append(
            f"FY2025 leverage is **{de:.2f}x D/E** and "
            f"interest coverage is **{interest:.1f}x**."
        )

    if (
        np.isfinite(receivables_turn)
        and receivables_turn > 0
    ):

        notes.append(
            f"Approximate receivable days are "
            f"**{365 / receivables_turn:.0f} days**."
        )

    for note in notes:
        st.markdown(
            "• " + note
        )

    section_title(
        "Historical dataset",
        "Submitted historical values for FY2021–FY2025.",
    )

    st.dataframe(
        D.style.format("{:,.2f}"),
        width="stretch",
    )


# ============================================================
# TRENDS
# ============================================================

elif page == "Trends Explorer":

    page_header(page)

    picks = st.multiselect(
        "Metrics",
        list(LBL.values()),
        default=[
            "NPM (%)",
            "ROA (%)",
            "ROE (%)",
        ],
    )

    norm = st.toggle(
        "Index to FY2021 = 100",
        False,
    )

    if not picks:

        st.info(
            "Select at least one metric."
        )

    else:

        X = D[picks].copy()

        if norm:

            base = X.iloc[0].replace(
                0,
                np.nan,
            )

            X = X.divide(base) * 100

        lines(
            X,
            picks,
            (
                "Selected metrics"
                + (
                    " • Indexed"
                    if norm
                    else ""
                )
            ),
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
                    colorscale=[
                        [0, "#b83b5e"],
                        [.5, "#10243a"],
                        [1, "#42d392"],
                    ],
                    text=np.round(
                        cm.values,
                        2,
                    ),
                    texttemplate="%{text}",
                )
            )

            show(
                fig,
                420,
                "Correlation matrix",
            )


# ============================================================
# RATIO SCORECARD
# ============================================================

elif page == "Ratio Scorecard":

    page_header(page)

    sc = scorecard(company)

    if sc.empty:

        st.warning(
            "Insufficient ratio data."
        )

    else:

        st.dataframe(
            style_scorecard(sc),
            width="stretch",
            hide_index=True,
        )

        fig = px.bar(
            sc,
            x="Ratio",
            y="Score",
            color="Score",
            color_continuous_scale=[
                "#d9534f",
                "#ffd166",
                "#42d392",
            ],
            range_color=[0, 100],
        )

        show(
            fig,
            370,
            "Educational ratio score",
        )

    st.caption(
        "Benchmarks are generic teaching thresholds rather than "
        "sector-specific recommendations. Scores are transparent "
        "heuristics and are not investment recommendations."
    )

    t1, t2, t3 = st.tabs(
        [
            "💧 Liquidity",
            "🛡️ Solvency",
            "⚙️ Efficiency",
        ]
    )

    with t1:

        lines(
            D,
            [
                "Current Ratio",
                "Quick Ratio",
            ],
            "Liquidity",
        )

    with t2:

        lines(
            D,
            [
                "Debt/Equity",
                "Interest Coverage",
            ],
            "Solvency",
        )

    with t3:

        lines(
            D,
            [
                "Asset Turnover",
                "Inventory Turnover",
                "Receivables Turnover",
            ],
            "Turnover",
        )

        turnover = vget(
            company,
            "receivablesTurn",
        )

        prev_turnover = clean_number(
            hist["receivablesTurn"][-2]
        )

        if (
            turnover > 0
            and prev_turnover > 0
        ):

            days = 365 / turnover
            prev_days = 365 / prev_turnover

            st.metric(
                "Receivable days",
                f"{days:.0f}",
                f"{days - prev_days:+.0f} vs FY24",
                delta_color="inverse",
            )


# ============================================================
# DUPONT
# ============================================================

elif page == "DuPont Analysis":

    page_header(page)

    st.latex(
        r"ROE = NPM \times Asset\ Turnover \times Equity\ Multiplier"
    )

    rows = []

    for i, year in enumerate(YEARS):

        npm = clean_number(
            hist["npm"][i]
        )

        at = clean_number(
            hist["assetTurn"][i]
        )

        roa = clean_number(
            hist["roa"][i]
        )

        roe = clean_number(
            hist["roe"][i]
        )

        equity_multiplier = safe_div(
            roe,
            roa,
        )

        implied_roa = (
            npm * at
        )

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
            "Equity Multiplier",
            "Implied ROA",
            "Reported ROA",
            "Reported ROE",
        ],
    ).set_index("Year")

    st.dataframe(
        dup.style.format("{:.2f}"),
        width="stretch",
    )

    gap = np.nanmax(
        np.abs(
            dup["Implied ROA"].to_numpy()
            - dup["Reported ROA"].to_numpy()
        )
    )

    if np.isfinite(gap):

        if gap < 1:

            st.success(
                f"Maximum NPM×AT vs reported ROA gap: "
                f"{gap:.2f} percentage points."
            )

        else:

            st.warning(
                f"Maximum gap is {gap:.2f} percentage points. "
                "Check asset-basis and averaging conventions."
            )

    base = dup.iloc[0]
    end = dup.iloc[-1]

    components = {}

    for name, column in [
        ("Margin", "NPM (%)"),
        ("Turnover", "Asset Turnover"),
        ("Leverage", "Equity Multiplier"),
    ]:

        a = clean_number(
            base[column]
        )

        b = clean_number(
            end[column]
        )

        if a > 0 and b > 0:

            components[name] = math.log(
                b / a
            )

    total = sum(
        components.values()
    )

    if (
        components
        and total != 0
    ):

        fig = go.Figure(
            go.Bar(
                x=list(
                    components
                ),
                y=[
                    v / total * 100
                    for v
                    in components.values()
                ],
                marker_color=[
                    "#5cc8ff",
                    "#42d392",
                    "#9b8cff",
                ],
            )
        )

        show(
            fig,
            320,
            "Share of ROE change FY21→FY25",
        )

    lines(
        dup,
        [
            "Reported ROE",
            "NPM (%)",
        ],
        "ROE vs margin",
    )


# ============================================================
# GROWTH
# ============================================================

elif page == "Growth Analysis":

    page_header(page)

    keys = [
        "revenue",
        "netIncome",
        "eps",
        "roe",
        "current",
    ]

    rows = []

    for key in keys:

        start = clean_number(
            hist[key][0]
        )

        end = clean_number(
            hist[key][-1]
        )

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
        width="stretch",
        hide_index=True,
    )

    yoy = pd.DataFrame(
        {
            LBL[key]: [
                pct_change(
                    hist[key][i],
                    hist[key][i - 1],
                )
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
            colorscale=[
                [0, "#d9534f"],
                [.5, "#10243a"],
                [1, "#42d392"],
            ],
            zmid=0,
            text=np.round(
                yoy.values,
                1,
            ),
            texttemplate="%{text}%",
        )
    )

    show(
        fig,
        360,
        "Year-over-year change",
    )


# ============================================================
# VERTICAL ANALYSIS
# ============================================================

elif page == "Vertical Analysis":

    page_header(page)

    vt = company.get(
        "vertical",
        {},
    )

    if not vt:

        st.info(
            "No common-size data supplied."
        )

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

                fig = go.Figure(
                    go.Bar(
                        x=[
                            vt[k]
                            for k in income_keys
                        ],
                        y=income_keys,
                        orientation="h",
                        marker_color="#5cc8ff",
                    )
                )

                show(
                    fig,
                    320,
                    "Income statement composition",
                )

            else:

                st.info(
                    "No income-statement data."
                )

        with b:

            if balance_keys:

                fig = go.Figure(
                    go.Bar(
                        x=[
                            vt[k]
                            for k in balance_keys
                        ],
                        y=balance_keys,
                        orientation="h",
                        marker_color="#42d392",
                    )
                )

                show(
                    fig,
                    320,
                    "Balance-sheet composition",
                )

            else:

                st.info(
                    "No balance-sheet data."
                )


# ============================================================
# PEER COMPARISON
# ============================================================

elif page == "Peer Comparison":

    page_header(page)

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
                cagr(
                    x["historical"]["revenue"][0],
                    x["historical"]["revenue"][-1],
                ),
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
        width="stretch",
    )

    a, b = st.columns(2)

    with a:

        fig = go.Figure()

        for symbol, x in ALL.items():

            base = clean_number(
                x["historical"]["revenue"][0]
            )

            if base > 0:

                fig.add_trace(
                    go.Scatter(
                        x=YEARS,
                        y=(
                            np.array(
                                x["historical"]["revenue"]
                            )
                            / base
                            * 100
                        ),
                        name=symbol,
                        mode="lines+markers",
                    )
                )

        show(
            fig,
            370,
            "Revenue indexed to FY2021 = 100",
        )

    with b:

        cols = [
            "NPM %",
            "ROE %",
            "Current",
            "Rev CAGR %",
        ]

        if len(peer):

            mins = peer[cols].min()

            ranges = (
                peer[cols].max()
                - mins
            ).replace(
                0,
                1,
            )

            normalised = (
                peer[cols]
                - mins
            ) / ranges

            fig = go.Figure()

            for symbol in normalised.index:

                values = normalised.loc[
                    symbol
                ].tolist()

                fig.add_trace(
                    go.Scatterpolar(
                        r=values + [values[0]],
                        theta=cols + [cols[0]],
                        name=symbol,
                        fill="toself",
                        opacity=.45,
                    )
                )

            show(
                fig,
                370,
                "Relative profile",
            )

    st.info(
        "Descriptive comparison only. Accounting basis, "
        "business mix, commodity exposure and capital structure "
        "can differ across companies."
    )


# ============================================================
# PESTEL
# ============================================================

elif page == "Industry / PESTEL":

    page_header(page)

    pestel = [
        (
            "Political / Regulatory",
            "Exploration blocks, permits, fiscal terms, royalties, "
            "taxation and policy consistency can affect project economics.",
        ),
        (
            "Economic",
            "Oil and gas prices, inflation, interest rates, "
            "exchange rates and energy demand influence margins.",
        ),
        (
            "Social",
            "Population, industrial activity and household "
            "energy demand can influence consumption patterns.",
        ),
        (
            "Technological",
            "Seismic imaging, reservoir analytics, automation "
            "and extraction technology can affect recovery and cost.",
        ),
        (
            "Environmental",
            "Emissions requirements, climate policy, water "
            "management and methane management affect operations.",
        ),
        (
            "Legal / Geopolitical",
            "Contracts, security conditions, joint ventures and "
            "regional instability can affect operational continuity.",
        ),
    ]

    cols = st.columns(3)

    for i, (title, text) in enumerate(pestel):

        with cols[i % 3]:

            st.markdown(
                f"""
                <div class="card"
                     style="min-height:150px">

                    <div class="card-title">
                        {title}
                    </div>

                    <div style="
                        color:#b8cbd9;
                        font-size:.82rem;
                        line-height:1.6;
                    ">
                        {text}
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )


# ============================================================
# RISK DASHBOARD
# ============================================================

elif page == "Risk Dashboard":

    page_header(page)

    st.caption(
        "Transparent educational heuristics based on the supplied dataset."
    )

    de = vget(
        company,
        "debtEq",
    )

    cr = vget(
        company,
        "current",
    )

    ic = vget(
        company,
        "interest",
    )

    npm_values = pd.Series(
        pd.to_numeric(
            hist["npm"],
            errors="coerce",
        )
    )

    npm_mean = npm_values.mean()
    npm_std = npm_values.std(
        ddof=0
    )

    volatility = (
        npm_std / npm_mean * 100
        if np.isfinite(npm_mean)
        and npm_mean != 0
        else np.nan
    )

    receivables_turn = vget(
        company,
        "receivablesTurn",
    )

    receivable_days = (
        365 / receivables_turn
        if receivables_turn > 0
        else np.nan
    )

    peak_ni = np.nanmax(
        pd.to_numeric(
            pd.Series(
                hist["netIncome"]
            ),
            errors="coerce",
        )
    )

    current_ni = clean_number(
        hist["netIncome"][-1]
    )

    drawdown = (
        (
            1
            - current_ni / peak_ni
        )
        * 100
        if peak_ni > 0
        and np.isfinite(current_ni)
        else np.nan
    )

    submitted_revenue = clean_number(
        hist["revenue"][-1]
    )

    verified_revenue = vget(
        company,
        "revenue",
    )

    revenue_gap = (
        abs(
            submitted_revenue
            / verified_revenue
            - 1
        )
        * 100
        if verified_revenue > 0
        else np.nan
    )

    risk_rows = [
        [
            "Leverage",
            (
                np.clip(
                    de * 50,
                    0,
                    100,
                )
                if np.isfinite(de)
                else np.nan
            ),
            (
                f"D/E {de:.2f}x"
                if np.isfinite(de)
                else "N/A"
            ),
        ],
        [
            "Liquidity",
            (
                np.clip(
                    100 - cr * 25,
                    0,
                    100,
                )
                if np.isfinite(cr)
                else np.nan
            ),
            (
                f"Current {cr:.2f}x"
                if np.isfinite(cr)
                else "N/A"
            ),
        ],
        [
            "Interest cover",
            (
                np.clip(
                    100 - ic * 8,
                    0,
                    100,
                )
                if np.isfinite(ic)
                else np.nan
            ),
            (
                f"{ic:.1f}x"
                if np.isfinite(ic)
                else "N/A"
            ),
        ],
        [
            "Margin volatility",
            (
                np.clip(
                    volatility * 4,
                    0,
                    100,
                )
                if np.isfinite(volatility)
                else np.nan
            ),
            (
                f"NPM CV {volatility:.1f}%"
                if np.isfinite(volatility)
                else "N/A"
            ),
        ],
        [
            "Receivables",
            (
                np.clip(
                    receivable_days / 2,
                    0,
                    100,
                )
                if np.isfinite(receivable_days)
                else np.nan
            ),
            (
                f"{receivable_days:.0f} days"
                if np.isfinite(receivable_days)
                else "N/A"
            ),
        ],
        [
            "Earnings drawdown",
            (
                np.clip(
                    drawdown * 2,
                    0,
                    100,
                )
                if np.isfinite(drawdown)
                else np.nan
            ),
            (
                f"{drawdown:.1f}%"
                if np.isfinite(drawdown)
                else "N/A"
            ),
        ],
        [
            "Data reliability",
            (
                np.clip(
                    revenue_gap * 3,
                    0,
                    100,
                )
                if np.isfinite(revenue_gap)
                else np.nan
            ),
            (
                f"Revenue gap {revenue_gap:.1f}%"
                if np.isfinite(revenue_gap)
                else "N/A"
            ),
        ],
    ]

    risk_df = pd.DataFrame(
        risk_rows,
        columns=[
            "Risk",
            "Score",
            "Evidence",
        ],
    )

    risk_df["Level"] = pd.cut(
        risk_df["Score"],
        [-1, 33, 66, 101],
        labels=[
            "🟢 Low",
            "🟡 Medium",
            "🔴 High",
        ],
    )

    a, b = st.columns(
        [1, 1.5]
    )

    with a:

        st.dataframe(
            risk_df.style.format(
                {"Score": "{:.0f}"}
            ),
            width="stretch",
            hide_index=True,
        )

    with b:

        chart_df = risk_df.dropna(
            subset=["Score"]
        )

        if len(chart_df):

            fig = px.bar(
                chart_df,
                x="Score",
                y="Risk",
                orientation="h",
                color="Score",
                color_continuous_scale=[
                    "#42d392",
                    "#ffd166",
                    "#ff6b6b",
                ],
                range_color=[0, 100],
            )

            show(
                fig,
                400,
                "Risk indicator scores",
            )

    st.markdown(
        """
        <div class="card">

        <div class="card-title">
            Structural E&P risk themes
        </div>

        <div style="
            color:#b8cbd9;
            line-height:1.65;
            font-size:.83rem;
        ">
        Commodity price and production-volume exposure,
        PKR/USD exposure on imported capital expenditure,
        reserve depletion, receivables/circular-debt collections,
        fiscal-policy changes and operational continuity are
        important structural considerations for E&P companies.
        </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.warning(
        "Risk scores are classroom heuristics, not forecasts "
        "or investment advice."
    )


# ============================================================
# DCF & MONTE CARLO
# ============================================================

elif page == "DCF & Monte Carlo":

    page_header(page)

    st.caption(
        "Illustrative academic valuation model — not investment advice."
    )

    sh = shares(company)

    pe = vget(
        company,
        "pe",
    )

    eps = vget(
        company,
        "eps",
    )

    pe_implied_price = (
        pe * eps
        if np.isfinite(pe)
        and np.isfinite(eps)
        else np.nan
    )

    rev0 = vget(
        company,
        "revenue",
    )

    if (
        not np.isfinite(sh)
        or sh <= 0
    ):

        st.error(
            "DCF requires a positive implied share count. "
            "Check FY2025 PAT and EPS."
        )

        st.stop()

    if (
        not np.isfinite(rev0)
        or rev0 <= 0
    ):

        st.error(
            "DCF requires positive FY2025 revenue."
        )

        st.stop()

    a, b = st.columns(
        [1, 2]
    )

    default_growth = cagr(
        hist["revenue"][0],
        hist["revenue"][-1],
    )

    if not np.isfinite(
        default_growth
    ):
        default_growth = 5.0

    default_margin = (
        clean_number(
            company[
                "vertical"
            ].get(
                "Operating Income",
                35.0,
            )
        )
        if company.get("vertical")
        else 35.0
    )

    with a:

        growth = st.number_input(
            "Revenue growth (%)",
            value=float(
                np.clip(
                    default_growth,
                    0,
                    20,
                )
            ),
            step=.5,
        )

        margin = st.number_input(
            "EBIT margin (%)",
            value=float(
                np.clip(
                    default_margin,
                    1,
                    80,
                )
            ),
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
            f"P/E-implied price = "
            f"PKR {pe_implied_price:,.1f}."
            if np.isfinite(
                pe_implied_price
            )
            else
            f"Implied shares ≈ {sh:,.0f}m."
        )

    if wacc <= terminal_growth:

        st.error(
            "WACC must exceed terminal growth."
        )

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

        st.error(
            f"DCF calculation failed: {exc}"
        )

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

        if (
            np.isfinite(
                pe_implied_price
            )
            and pe_implied_price != 0
        ):

            k[2].metric(
                "Vs P/E implied price",
                (
                    f"{(result['ps'] / "
                    f"pe_implied_price - 1) * 100:+.1f}%"
                ),
            )

        else:

            k[2].metric(
                "Vs P/E implied price",
                "N/A",
            )

        waterfall = go.Figure(
            go.Waterfall(
                x=[
                    "PV explicit FCF",
                    "PV terminal",
                    "Net debt",
                    "Equity",
                ],
                measure=[
                    "relative",
                    "relative",
                    "relative",
                    "total",
                ],
                y=[
                    result["pv"],
                    result["pvtv"],
                    -net_debt,
                    0,
                ],
                connector=dict(
                    line=dict(
                        color="#35556d"
                    )
                ),
                increasing=dict(
                    marker=dict(
                        color="#42d392"
                    )
                ),
                decreasing=dict(
                    marker=dict(
                        color="#ff6b6b"
                    )
                ),
            )
        )

        show(
            waterfall,
            320,
            "Value bridge (PKR m)",
        )

        terminal_share = safe_div(
            result["pvtv"],
            result["ev"],
        ) * 100

        if np.isfinite(
            terminal_share
        ):

            st.caption(
                f"Terminal value contributes "
                f"approximately {terminal_share:.0f}% of EV."
            )

    forecast_df = pd.DataFrame(
        result["rows"],
        columns=[
            "Year",
            "Revenue",
            "EBIT",
            "FCF",
            "Discounted FCF",
        ],
    )

    st.dataframe(
        forecast_df.style.format(
            "{:,.0f}"
        ),
        width="stretch",
        hide_index=True,
    )

    t1, t2 = st.tabs(
        [
            "🎯 Sensitivity",
            "🎲 Monte Carlo",
        ]
    )

    with t1:

        ws = np.arange(
            wacc - 3,
            wacc + 3.1,
            1.0,
        )

        gs = np.arange(
            max(
                -5,
                terminal_growth - 2,
            ),
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

        fig = go.Figure(
            go.Heatmap(
                z=Z,
                x=[
                    f"{w:.1f}%"
                    for w in ws
                ],
                y=[
                    f"{t:.1f}%"
                    for t in gs
                ],
                colorscale=[
                    [0, "#ff6b6b"],
                    [.5, "#ffd166"],
                    [1, "#42d392"],
                ],
                text=np.round(
                    np.array(
                        Z,
                        dtype=float,
                    ),
                    0,
                ),
                texttemplate="%{text}",
            )
        )

        show(
            fig,
            380,
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

        rng = np.random.default_rng(
            42
        )

        outputs = []

        for _ in range(
            simulations
        ):

            w = rng.normal(
                wacc,
                1.5,
            )

            tg_sim = rng.normal(
                terminal_growth,
                .75,
            )

            growth_sim = rng.normal(
                growth,
                3,
            )

            margin_sim = rng.normal(
                margin,
                4,
            )

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

        outputs = np.asarray(
            outputs,
            dtype=float,
        )

        if len(outputs) < 10:

            st.warning(
                "Too few valid simulations. "
                "Adjust WACC or terminal-growth assumptions."
            )

        else:

            p5, median, p95 = np.percentile(
                outputs,
                [5, 50, 95],
            )

            fig = go.Figure(
                go.Histogram(
                    x=outputs,
                    nbinsx=50,
                    marker_color="#5cc8ff",
                    opacity=.85,
                )
            )

            if np.isfinite(
                pe_implied_price
            ):

                fig.add_vline(
                    x=pe_implied_price,
                    line_color="#ffd166",
                    line_width=2,
                    annotation_text="P/E implied price",
                )

            show(
                fig,
                360,
                "Distribution of model value per share",
            )

            probability = (
                np.mean(
                    outputs
                    > pe_implied_price
                )
                * 100
                if np.isfinite(
                    pe_implied_price
                )
                else np.nan
            )

            st.write(
                f"P5 **{p5:,.0f}** | "
                f"Median **{median:,.0f}** | "
                f"P95 **{p95:,.0f}** | "
                + (
                    f"P(value > P/E implied price) = "
                    f"**{probability:.0f}%**"
                    if np.isfinite(
                        probability
                    )
                    else
                    "P/E comparison unavailable."
                )
            )


# ============================================================
# RELATIVE VALUATION
# ============================================================

elif page == "Relative Valuation":

    page_header(page)

    rows = []

    for symbol, x in ALL.items():

        pe = vget(
            x,
            "pe",
        )

        eps = vget(
            x,
            "eps",
        )

        div_yield = vget(
            x,
            "dividendYield",
        )

        roe = vget(
            x,
            "roe",
        )

        implied_price = (
            pe * eps
            if np.isfinite(pe)
            and np.isfinite(eps)
            else np.nan
        )

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
            "P/E implied price",
            "Div yield %",
            "ROE %",
        ],
    ).set_index("Company")

    st.dataframe(
        relative.style.format(
            "{:,.2f}"
        ),
        width="stretch",
    )

    scatter_df = relative.reset_index().dropna(
        subset=[
            "ROE %",
            "P/E",
        ]
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

        fig.update_traces(
            textposition="top center",
            marker=dict(
                color="#5cc8ff",
                line=dict(
                    color="#d8f3ff",
                    width=1,
                ),
            ),
        )

        show(
            fig,
            390,
            "P/E vs ROE",
        )

    else:

        st.info(
            "Insufficient peer data."
        )

    pe_values = pd.to_numeric(
        relative["P/E"],
        errors="coerce",
    ).dropna()

    if len(pe_values):

        median_pe = pe_values.median()

        target_eps = vget(
            company,
            "eps",
        )

        if np.isfinite(
            target_eps
        ):

            st.info(
                f"Peer median P/E = {median_pe:.2f}x. "
                f"Applying that multiple mechanically to "
                f"{sel}'s EPS gives "
                f"PKR {median_pe * target_eps:,.1f} "
                "per share. This is a descriptive multiple "
                "exercise; growth, risk, accounting basis and "
                "business mix also matter."
            )


# ============================================================
# SCENARIO ANALYSIS
# ============================================================

elif page == "Scenario Analysis":

    page_header(page)

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
        value=float(
            clean_number(
                hist["npm"][-1],
                10,
            )
        ),
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

    if (
        not np.isfinite(sh)
        or sh <= 0
    ):

        st.error(
            "Scenario analysis requires a valid positive implied share count."
        )

        st.stop()

    cases = {
        "Bear": (
            base_growth - shock,
            max(
                1,
                base_margin - shock / 2,
            ),
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

    base_revenue = vget(
        company,
        "revenue",
    )

    base_eps = vget(
        company,
        "eps",
    )

    scenario_colors = {
        "Bear": "#ff6b6b",
        "Base": "#5cc8ff",
        "Bull": "#42d392",
    }

    for col, (name, (growth_rate, margin_rate)) in zip(
        cols,
        cases.items(),
    ):

        path = [
            base_revenue
            * (
                1 + growth_rate / 100
            ) ** t
            for t in range(
                horizon + 1
            )
        ]

        profit = (
            path[-1]
            * margin_rate
            / 100
        )

        eps = (
            profit / sh
        )

        fig.add_trace(
            go.Scatter(
                x=[
                    2025 + t
                    for t in range(
                        horizon + 1
                    )
                ],
                y=path,
                name=name,
                mode="lines+markers",
                line=dict(
                    color=scenario_colors[name],
                    width=3,
                ),
            )
        )

        with col:

            st.markdown(
                f"""
                <div class="card">
                    <div class="card-title">
                        {name}
                    </div>

                    <div class="card-note">
                        Growth {growth_rate:.1f}% •
                        Margin {margin_rate:.1f}%
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.metric(
                f"Revenue FY{2025 + horizon}",
                f"{fmt(path[-1])}m",
            )

            st.metric(
                "Profit",
                f"{fmt(profit)}m",
            )

            eps_delta = (
                pct_change(
                    eps,
                    base_eps,
                )
                if np.isfinite(
                    base_eps
                )
                else np.nan
            )

            st.metric(
                "EPS",
                f"PKR {eps:,.2f}",
                (
                    f"{eps_delta:+.1f}% vs FY25"
                    if np.isfinite(
                        eps_delta
                    )
                    else "N/A"
                ),
            )

    show(
        fig,
        360,
        "Revenue scenario paths",
    )


# ============================================================
# DATA INTEGRITY
# ============================================================

elif page == "Data Integrity":

    page_header(page)

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

            if key not in x.get(
                "verified2025",
                {},
            ):
                continue

            submitted = clean_number(
                x["historical"][key][-1]
            )

            verified_value = clean_number(
                x["verified2025"][key]
            )

            variance = (
                (
                    submitted
                    / verified_value
                    - 1
                )
                * 100
                if verified_value != 0
                else np.nan
            )

            if not np.isfinite(
                variance
            ):
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
        width="stretch",
        hide_index=True,
    )

    if len(integrity):

        fig = px.bar(
            integrity,
            x="Metric",
            y="Variance %",
            color="Company",
            barmode="group",
        )

        show(
            fig,
            340,
            "Submitted vs verified variance",
        )

    section_title(
        "Internal consistency",
        "Selected company — reported NPM versus NI / Revenue.",
    )

    consistency = []

    for i, year in enumerate(
        YEARS
    ):

        revenue = clean_number(
            hist["revenue"][i]
        )

        net_income = clean_number(
            hist["netIncome"][i]
        )

        reported_npm = clean_number(
            hist["npm"][i]
        )

        implied_npm = (
            net_income
            / revenue
            * 100
            if revenue != 0
            else np.nan
        )

        consistency.append(
            [
                year,
                reported_npm,
                implied_npm,
                (
                    reported_npm
                    - implied_npm
                    if np.isfinite(
                        reported_npm
                    )
                    and np.isfinite(
                        implied_npm
                    )
                    else np.nan
                ),
            ]
        )

    consistency_df = pd.DataFrame(
        consistency,
        columns=[
            "Year",
            "Reported NPM",
            "NI / Revenue",
            "Gap (pp)",
        ],
    )

    st.dataframe(
        consistency_df.style.format(
            "{:.2f}"
        ),
        width="stretch",
        hide_index=True,
    )

    st.info(
        "Recommended production source priority: audited issuer "
        "annual report → PSX issuer page → licensed data provider. "
        "The demo dataset is not a live market feed."
    )


# ============================================================
# IMPORT & EXPORT
# ============================================================

elif page == "Import & Export":

    page_header(page)

    st.markdown(
        """
        <div class="card">

        <div class="card-title">
            JSON import
        </div>

        <div style="
            color:#b8cbd9;
            font-size:.83rem;
            line-height:1.6;
        ">
        Upload a JSON company record or edit the template below.
        All 15 historical metrics require exactly five values,
        ordered FY2021 through FY2025.
        </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    template = {
        "symbol": "NEWCO",
        "name": "Example Company",
        "years": YEARS,
        **{
            key: [1, 2, 3, 4, 5]
            for key in HK
        },
        "source": "Source / URL",
    }

    template.update(
        revenue=[
            100,
            110,
            120,
            130,
            140,
        ],
        netIncome=[
            10,
            12,
            14,
            15,
            16,
        ],
        npm=[
            10,
            10.91,
            11.67,
            11.54,
            11.43,
        ],
        roa=[
            5,
            5.5,
            6,
            6.2,
            6.5,
        ],
        roe=[
            8,
            9,
            10,
            10.5,
            11,
        ],
        current=[
            2,
            2.1,
            2.2,
            2.3,
            2.4,
        ],
        quick=[
            1.8,
            1.9,
            2,
            2.1,
            2.2,
        ],
        debtEq=[
            .5,
            .48,
            .45,
            .42,
            .4,
        ],
        interest=[
            4,
            4.5,
            5,
            5.2,
            5.5,
        ],
        assetTurn=[
            .5,
            .52,
            .54,
            .56,
            .58,
        ],
        inventoryTurn=[
            5,
            5.2,
            5.4,
            5.6,
            5.8,
        ],
        receivablesTurn=[
            4,
            4.1,
            4.2,
            4.3,
            4.4,
        ],
        pe=[
            10,
            9.5,
            9,
            8.5,
            8,
        ],
        eps=[
            2,
            2.4,
            2.8,
            3,
            3.2,
        ],
        dividendYield=[
            2,
            2.2,
            2.4,
            2.5,
            2.6,
        ],
    )

    uploaded = st.file_uploader(
        "Upload JSON",
        type=["json"],
        key="company_json_upload",
    )

    raw = (
        uploaded.read().decode(
            "utf-8"
        )
        if uploaded is not None
        else st.text_area(
            "Or paste JSON",
            json.dumps(
                template,
                indent=2,
            ),
            height=430,
        )
    )

    if st.button(
        "Validate & Add Company",
        type="primary",
        key="validate_add_company",
    ):

        try:

            payload = json.loads(
                raw
            )

            if not isinstance(
                payload,
                dict,
            ):

                raise ValueError(
                    "Top-level JSON must be an object."
                )

            required = set(
                template.keys()
            )

            missing = sorted(
                required
                - set(payload)
            )

            if missing:

                st.error(
                    "Missing fields: "
                    + ", ".join(missing)
                )

            elif not isinstance(
                payload.get("years"),
                list,
            ):

                st.error(
                    "years must be a list."
                )

            elif payload["years"] != YEARS:

                st.error(
                    f"years must exactly match "
                    f"{YEARS}, from oldest to newest."
                )

            elif any(
                not isinstance(
                    payload.get(key),
                    list,
                )
                or len(
                    payload[key]
                ) != 5
                for key in HK
            ):

                st.error(
                    "Every historical metric "
                    "must contain exactly 5 values."
                )

            elif not str(
                payload.get(
                    "symbol",
                    "",
                )
            ).strip():

                st.error(
                    "symbol cannot be empty."
                )

            elif not str(
                payload.get(
                    "name",
                    "",
                )
            ).strip():

                st.error(
                    "name cannot be empty."
                )

            else:

                numeric_data = {}

                for key in HK:

                    converted = [
                        clean_number(
                            value
                        )
                        for value
                        in payload[key]
                    ]

                    if any(
                        not np.isfinite(
                            value
                        )
                        for value
                        in converted
                    ):

                        raise ValueError(
                            f"{key} contains "
                            "an invalid value."
                        )

                    numeric_data[key] = (
                        converted
                    )

                npm_gaps = []

                for i in range(5):

                    revenue = (
                        numeric_data[
                            "revenue"
                        ][i]
                    )

                    net_income = (
                        numeric_data[
                            "netIncome"
                        ][i]
                    )

                    npm = (
                        numeric_data[
                            "npm"
                        ][i]
                    )

                    if revenue != 0:

                        npm_gaps.append(
                            abs(
                                net_income
                                / revenue
                                * 100
                                - npm
                            )
                        )

                if (
                    npm_gaps
                    and max(npm_gaps) > 2
                ):

                    st.warning(
                        "NPM differs from "
                        "NI/Revenue by more than "
                        "2 percentage points in at "
                        "least one year."
                    )

                symbol = str(
                    payload[
                        "symbol"
                    ]
                ).strip().upper()

                name = str(
                    payload[
                        "name"
                    ]
                ).strip()

                source = str(
                    payload.get(
                        "source",
                        "User supplied",
                    )
                ).strip()

                custom_company = mk(
                    name,
                    "User-imported company.",
                    [
                        numeric_data[key]
                        for key in HK
                    ],
                    {
                        "revenue":
                            numeric_data[
                                "revenue"
                            ][-1],
                        "netIncome":
                            numeric_data[
                                "netIncome"
                            ][-1],
                        "eps":
                            numeric_data[
                                "eps"
                            ][-1],
                        "pe":
                            numeric_data[
                                "pe"
                            ][-1],
                    },
                    None,
                    [
                        (
                            source,
                            (
                                source
                                if source.startswith(
                                    "http"
                                )
                                else ""
                            ),
                        )
                    ],
                )

                ok, reason = (
                    validate_company_structure(
                        custom_company
                    )
                )

                if not ok:

                    st.error(
                        f"Validation failed: {reason}"
                    )

                else:

                    st.session_state.custom[
                        symbol
                    ] = custom_company

                    st.success(
                        f"{symbol} added successfully. "
                        "Use the company selector to load it."
                    )

        except json.JSONDecodeError as exc:

            st.error(
                f"Invalid JSON: {exc}"
            )

        except Exception as exc:

            st.error(
                f"Could not import company: {exc}"
            )

    st.markdown(
        '<div class="section-divider"></div>',
        unsafe_allow_html=True,
    )

    section_title(
        "Export",
        "Download the active company's dataset and analysis outputs.",
    )

    export_a, export_b, export_c = st.columns(3)

    export_a.download_button(
        "⬇ Dataset CSV",
        D.to_csv().encode(
            "utf-8"
        ),
        f"{sel}_dataset.csv",
        "text/csv",
        key="download_dataset",
    )

    export_b.download_button(
        "⬇ Scorecard CSV",
        scorecard(
            company
        ).to_csv(
            index=False
        ).encode(
            "utf-8"
        ),
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
                    key:
                        company[
                            "historical"
                        ][key]
                    for key in HK
                },
                "verified2025":
                    company.get(
                        "verified2025",
                        {},
                    ),
                "vertical":
                    company.get(
                        "vertical",
                        {},
                    ),
                "sources":
                    company.get(
                        "sources",
                        [],
                    ),
            },
            indent=2,
        ).encode(
            "utf-8"
        ),
        f"{sel}_company.json",
        "application/json",
        key="download_company_json",
    )

    section_title(
        "Current imported companies"
    )

    if st.session_state.custom:

        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "Symbol": symbol,
                        "Company": x["name"],
                        "Source": (
                            x["sources"][0][0]
                            if x.get(
                                "sources"
                            )
                            else "N/A"
                        ),
                    }
                    for symbol, x
                    in st.session_state.custom.items()
                ]
            ),
            width="stretch",
            hide_index=True,
        )

    else:

        st.info(
            "No custom companies have been imported in this session."
        )


# ============================================================
# REFERENCES
# ============================================================

elif page == "References":

    page_header(page)

    sources = company.get(
        "sources",
        [],
    )

    if not sources:

        st.info(
            "No references supplied."
        )

    else:

        for title, url in sources:

            safe_url = str(
                url
            ).strip()

            if safe_url.startswith(
                (
                    "http://",
                    "https://",
                )
            ):

                st.markdown(
                    f"""
                    <div class="card">

                        <div class="card-title">
                            {title}
                        </div>

                        <a href="{safe_url}"
                           target="_blank"
                           style="
                           color:#5cc8ff !important;
                           font-size:.82rem;
                           word-break:break-all;
                           ">
                            {safe_url}
                        </a>

                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            else:

                st.markdown(
                    f"""
                    <div class="card">
                        <div class="card-title">
                            {title}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    section_title(
        "Recommended production architecture"
    )

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
        "Never place data-provider credentials, API keys, "
        "passwords or private tokens in frontend code "
        "or a public GitHub repository."
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        <b style="color:#7fa4bc !important">
            COMSATS University Islamabad
        </b>
        • Business Finance
        • Instructor: Miss Sania Khalid
        • Student: Muhammad Abubakar
        <br><br>
        PSX Financial Analysis Lab
        • FY2021–FY2025
        • Academic / illustrative use
    </div>
    """,
    unsafe_allow_html=True,
)



