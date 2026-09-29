import json
from datetime import datetime
import numpy as np, pandas as pd, streamlit as st
import plotly.graph_objects as go, plotly.express as px

st.set_page_config(page_title='PSX Financial Analysis Lab', page_icon='📊', layout='wide')
st.markdown('''<style>
.stApp{background:#07111f;color:#eaf2fb}.block-container{max-width:1500px;padding-top:4.5rem}
[data-testid="stSidebar"]{background:#06101d}
.hero{padding:1.2rem 1.5rem;border:1px solid #20364d;border-radius:16px;background:linear-gradient(135deg,#11243a,#0c1c2e);margin-bottom:1rem}
.warning{border-left:4px solid #ffd166;background:#201c0a;padding:.7rem 1rem;border-radius:10px;color:#f6e6a9;font-size:.9rem}
.card{border:1px solid #20364d;border-radius:12px;padding:1rem;background:#0d1b2e;margin-bottom:.5rem}
div[role="radiogroup"]{gap:.4rem;flex-wrap:wrap}
div[role="radiogroup"]>label{background:#0d1b2e;border:1px solid #20364d;border-radius:999px;padding:.25rem .85rem;margin:0;cursor:pointer}
div[role="radiogroup"]>label:hover{border-color:#5cc8ff}
div[role="radiogroup"]>label>div:first-child{display:none}
div[role="radiogroup"]>label:has(input:checked){background:#5cc8ff;border-color:#5cc8ff}
div[role="radiogroup"]>label:has(input:checked) p{color:#07111f;font-weight:700}
div[role="radiogroup"] p{font-size:.85rem;margin:0}
[data-testid="stMetric"]{background:#0d1b2e;border:1px solid #20364d;border-radius:12px;padding:.6rem .9rem}
</style>''', unsafe_allow_html=True)

YEARS = [2021, 2022, 2023, 2024, 2025]
HK = ['revenue','netIncome','npm','roa','roe','current','quick','debtEq','interest','assetTurn','inventoryTurn','receivablesTurn','pe','eps','dividendYield']
LBL = dict(zip(HK, ['Revenue (PKR m)','Net Income (PKR m)','NPM (%)','ROA (%)','ROE (%)','Current Ratio','Quick Ratio','Debt/Equity','Interest Coverage','Asset Turnover','Inventory Turnover','Receivables Turnover','P/E','EPS','Dividend Yield (%)']))

def mk(name, desc, rows, ver, vert, src):
    return dict(name=name, description=desc, historical=dict(zip(HK, rows)), verified2025=ver, vertical=vert, sources=src)

DEMO = {
'OGDC': mk('Oil & Gas Development Company Limited','Large Pakistani upstream exploration and production company.',
 [[239774,279816,324282,378423,401178],[91534,133430,224617,208976,169903],[38.28,39.88,54.31,45.07,42.35],[9.57,11.84,15.77,13.03,10.27],[11.89,15.28,20.74,16.71,12.60],[6.40,5.60,5.96,5.86,8.97],[6.21,5.45,5.81,5.73,8.72],[0]*5,[5.92,9.75,6.17,3.74,3.54],[.25,.30,.29,.29,.24],[5.08,5.78,6.15,7.38,5.53],[.63,.69,.67,.68,.61],[9.40,7.07,4.79,4.73,4.56],[21.28,31.11,52.23,48.59,39.50],[3.45,3.30,3.42,4.40,2.81]],
 {'revenue':401178,'netIncome':169904,'eps':39.50,'pe':5.58},
 {'Cost of Revenue':42.28,'Gross Profit':57.72,'Operating Income':46.40,'Net Income':42.35,'Current Assets':42.47,'Net PPE':57.53,'Total Liabilities':25.06,'Total Equity':74.94},
 [('PSX company page','https://dps.psx.com.pk/company/OGDC'),('OGDCL Financial Reports','https://ogdcl.com/investors/financial-reports?language=en'),('OGDCL Financial Highlights','https://ogdcl.com/investors/financial-highlights')]),
'PPL': mk('Pakistan Petroleum Limited','Major Pakistani exploration and production company.',
 [[149279,203811,288053,291241,244977],[52283,54356,97937,114309,89949],[35.02,26.67,33.75,39.65,36.72],[9.73,8.65,12.24,12.65,9.68],[13.44,12.50,17.98,18.02,12.76],[4.37,3.52,3.32,3.55,4.78],[4.31,3.48,3.28,3.52,4.72],[0]*5,[17.25,13.42,12.89,8.85,6.55],[.28,.32,.36,.32,.26],[13.79,12.99,16.23,14.78,10.49],[.53,.56,.56,.50,.41],[6.25,6.51,4.48,4.24,4.54],[19.21,19.98,35.73,42.44,33.06],[2.92,1.92,3.75,4.17,3.33]],
 {'revenue':242516,'netIncome':92027,'eps':33.82,'pe':5.03,'current':4.81,'roe':13.0},
 {'Cost of Revenue':37.72,'Gross Profit':62.28,'Operating Income':46.40,'Net Income':36.72,'Current Assets':75.53,'Net PPE':15.54,'Total Liabilities':24.14,'Total Equity':75.86},
 [('PSX company page','https://dps.psx.com.pk/company/PPL'),('PPL Annual Report 2025','https://www.ppl.com.pk/content/annual-report-2025'),('PPL Financial Highlights','https://www.ppl.com.pk/content/financial-highlights')]),
'MARI': mk('Mari Energies Limited','Pakistani E&P company formerly Mari Petroleum Company Limited.',
 [[63703,83135,128221,159731,141486],[31445,33064,56129,77288,65369],[49.36,39.77,43.77,48.39,46.20],[20.91,17.86,22.05,22.30,15.36],[27.22,25.27,33.33,34.36,23.87],[3.61,2.26,1.98,2.79,2.97],[3.49,2.17,1.86,2.66,2.78],[0,.01,.01,0,.04],[10.27,19.77,17.21,10.50,7.86],[.42,.45,.50,.46,.33],[5.12,4.93,3.76,4.04,3.17],[2.27,2.57,2.08,1.97,1.63],[13.36,13.80,9.63,8.54,9.18],[26.19,27.54,46.75,64.37,54.45],[4.48,3.63,3.63,4.69,4.34]],
 {'revenue':177097,'netIncome':65136,'eps':54.25,'pe':11.56,'current':2.81,'quick':2.59,'roe':26.23,'assetTurn':.46,'dividendYield':7.20},
 {'Cost of Revenue':28.37,'Gross Profit':71.63,'Operating Income':55.03,'Net Income':36.78,'Current Assets':47.90,'Net PPE':47.33,'Total Liabilities':35.62,'Total Equity':64.38},
 [('PSX company page','https://dps.psx.com.pk/company/MARI'),('MariEnergies Annual Reports','https://www.marienergies.com.pk/investors-relations/financial-reports'),('MariEnergies Financial Highlights','https://www.marienergies.com.pk/investors-relations/financial-highlights')]),
}
st.session_state.setdefault('custom', {})
ALL = {**DEMO, **st.session_state.custom}

# ---------- helpers ----------
def fmt(x, d=0):
    return 'N/A' if x is None or (isinstance(x, float) and np.isnan(x)) else f'{float(x):,.{d}f}'
def cagr(a, b, n=4):
    return ((b / a) ** (1 / n) - 1) * 100 if a and a > 0 and b > 0 else np.nan
def vget(c, k):
    v, h = c['verified2025'], c['historical']
    return v.get(k, v.get('epsRestated') if k == 'eps' and 'eps' not in v else h[k][-1])
def hdf(c):
    return pd.DataFrame({'Year': YEARS, **{LBL[k]: c['historical'][k] for k in HK}}).set_index('Year')
def shares(c):
    return vget(c, 'netIncome') / vget(c, 'eps')
def style(fig, h=380, title=None):
    fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=h,
                      margin=dict(l=10, r=10, t=45, b=10), legend=dict(orientation='h', y=1.12), title=title)
    return fig
def show(fig, h=380, title=None):
    st.plotly_chart(style(fig, h, title), use_container_width=True)
def lines(df, cols, title, h=380, bar=False):
    fig = go.Figure([(go.Bar if bar else go.Scatter)(x=df.index, y=df[k], name=k, **({} if bar else dict(mode='lines+markers'))) for k in cols])
    show(fig, h, title)

RULES = {'current':(1.5,'hi'),'quick':(1.0,'hi'),'debtEq':(1.0,'lo'),'interest':(3,'hi'),'npm':(10,'hi'),'roa':(5,'hi'),'roe':(12,'hi'),'assetTurn':(.3,'hi'),'receivablesTurn':(4,'hi')}
def score(k, val):
    thr, d = RULES[k]
    if d == 'hi': return float(np.clip(70 * val / thr, 0, 100))
    return 100.0 if val <= thr else float(np.clip(100 * thr / val, 0, 100))
def light(s): return '🟢 Strong' if s >= 70 else '🟡 Watch' if s >= 45 else '🔴 Weak'
def scorecard(c):
    h = c['historical']; rows = []
    for k in RULES:
        cur, prev = h[k][-1], h[k][-2]; s = score(k, cur)
        rows.append([LBL[k], cur, prev, cur - prev, RULES[k][0], '≥' if RULES[k][1] == 'hi' else '≤', round(s), light(s)])
    return pd.DataFrame(rows, columns=['Ratio','FY2025','FY2024','Δ YoY','Benchmark','Rule','Score','Status'])

def dcf(rev0, g, m, tax, capex, wc, wacc, tg, nd, sh, n=5):
    rev, pv, rows = rev0, 0, []
    for t in range(1, n + 1):
        rev *= 1 + g / 100; ebit = rev * m / 100
        fcf = ebit * (1 - tax / 100) - rev * (capex + wc) / 100
        d = fcf / (1 + wacc / 100) ** t; pv += d; rows.append([t, rev, ebit, fcf, d])
    tv = rows[-1][3] * (1 + tg / 100) / ((wacc - tg) / 100); pvtv = tv / (1 + wacc / 100) ** n
    ev = pv + pvtv
    return dict(rows=rows, pv=pv, tv=tv, pvtv=pvtv, ev=ev, eq=ev - nd, ps=(ev - nd) / sh)

# ---------- sidebar ----------
st.sidebar.title('📊 PSX Financial Lab')
st.sidebar.caption('Five-Year Academic Analysis Engine v2')
sel = st.sidebar.selectbox('Company', list(ALL), format_func=lambda x: f'{x} – {ALL[x]["name"]}')
PAGES = ['Executive Dashboard','Trends Explorer','Ratio Scorecard','DuPont Analysis','Growth Analysis','Vertical Analysis','Peer Comparison','Industry / PESTEL','Risk Dashboard','DCF & Monte Carlo','Relative Valuation','Scenario Analysis','Data Integrity','Import & Export','References']
st.sidebar.markdown('---'); st.sidebar.caption('Pick a company here; navigate pages from the top bar.')
c = ALL[sel]; h = c['historical']; v = c['verified2025']; D = hdf(c)

page = st.radio('Navigate', PAGES, horizontal=True, label_visibility='collapsed', key='nav')
st.markdown('<hr style="margin:.2rem 0 .8rem;border-color:#20364d">', unsafe_allow_html=True)

st.markdown('<div class="hero"><b style="color:#5cc8ff">COMSATS UNIVERSITY ISLAMABAD • DEPARTMENT OF MANAGEMENT SCIENCES</b><h2 style="margin:.3rem 0">PSX Five-Year Financial Analysis Dashboard</h2><div class="warning"><b>Data-quality note:</b> submitted history and verified snapshots are kept separate; differences may come from restatements, consolidation, units or methodology. See <i>Data Integrity</i>.</div></div>', unsafe_allow_html=True)

# ---------- pages ----------
if page == 'Executive Dashboard':
    st.header(f'{sel} — {c["name"]}'); st.caption(c['description'])
    sc = scorecard(c); comp = sc['Score'].mean()
    k = st.columns(6)
    k[0].metric('Revenue', f'{fmt(vget(c,"revenue"))}m', f'{(h["revenue"][-1]/h["revenue"][-2]-1)*100:+.1f}% YoY')
    k[1].metric('PAT', f'{fmt(vget(c,"netIncome"))}m', f'{(h["netIncome"][-1]/h["netIncome"][-2]-1)*100:+.1f}% YoY')
    k[2].metric('EPS', fmt(vget(c,'eps'), 2)); k[3].metric('P/E', f'{vget(c,"pe"):.2f}x')
    k[4].metric('ROE', f'{vget(c,"roe"):.1f}%'); k[5].metric('Health score', f'{comp:.0f}/100', light(comp).split()[1])
    a, b = st.columns([3, 2])
    with a:
        fig = go.Figure([go.Bar(x=YEARS, y=h['revenue'], name='Revenue'), go.Bar(x=YEARS, y=h['netIncome'], name='Net income'),
                         go.Scatter(x=YEARS, y=h['npm'], name='NPM %', yaxis='y2', mode='lines+markers', line=dict(color='#ffd166'))])
        fig.update_layout(barmode='group', yaxis2=dict(overlaying='y', side='right', showgrid=False)); show(fig, 380, 'Scale & margin')
    with b:
        fig = go.Figure(go.Scatterpolar(r=sc['Score'].tolist() + [sc['Score'][0]], theta=sc['Ratio'].tolist() + [sc['Ratio'][0]], fill='toself', line=dict(color='#5cc8ff')))
        fig.update_layout(polar=dict(radialaxis=dict(range=[0, 100]))); show(fig, 380, 'Ratio health radar')
    st.subheader('Automated commentary')
    rc, nc = cagr(h['revenue'][0], h['revenue'][-1]), cagr(h['netIncome'][0], h['netIncome'][-1])
    peak = max(h['netIncome']); dd = (h['netIncome'][-1] / peak - 1) * 100
    notes = [f'Revenue CAGR FY21–25 is **{rc:.1f}%**; net income CAGR is **{nc:.1f}%**' + (' — profit growth lags sales, signalling margin pressure.' if nc < rc else '.'),
             f'Net income is **{abs(dd):.1f}% {"below" if dd < 0 else "at"}** its five-year peak.' if dd < 0 else 'Net income is at its five-year peak.',
             f'Liquidity: current ratio **{h["current"][-1]:.2f}x** ' + ('(comfortable).' if h['current'][-1] >= 1.5 else '(tight).'),
             f'Leverage: debt/equity **{h["debtEq"][-1]:.2f}x**; interest cover **{h["interest"][-1]:.1f}x**' + (' but falling for several years.' if h['interest'][-1] < h['interest'][0] else '.'),
             f'Receivable days ≈ **{365/h["receivablesTurn"][-1]:.0f}** (circular-debt sensitivity).']
    for n in notes: st.markdown('• ' + n)
    st.subheader('Historical dataset'); st.dataframe(D.style.format('{:,.2f}'), use_container_width=True)

elif page == 'Trends Explorer':
    st.header('Trends Explorer')
    picks = st.multiselect('Metrics', list(LBL.values()), default=['NPM (%)', 'ROA (%)', 'ROE (%)'])
    norm = st.toggle('Index to FY2021 = 100', False)
    X = D[picks]; X = X / X.iloc[0] * 100 if norm else X
    if picks:
        lines(X, picks, 'Selected metrics' + (' (indexed)' if norm else ''), 420)
        if len(picks) > 1:
            cm = D[picks].corr()
            show(go.Figure(go.Heatmap(z=cm.values, x=cm.columns, y=cm.index, zmin=-1, zmax=1, colorscale='RdBu', text=cm.round(2).values, texttemplate='%{text}')), 420, 'Correlation (5 obs – indicative only)')

elif page == 'Ratio Scorecard':
    st.header('Ratio Scorecard'); sc = scorecard(c)
    st.dataframe(sc.style.format({'FY2025':'{:.2f}','FY2024':'{:.2f}','Δ YoY':'{:+.2f}'}).background_gradient(subset=['Score'], cmap='RdYlGn', vmin=0, vmax=100), use_container_width=True, hide_index=True)
    show(px.bar(sc, x='Ratio', y='Score', color='Score', color_continuous_scale='RdYlGn', range_color=[0, 100]), 360, 'Score by ratio')
    st.caption('Benchmarks are generic teaching thresholds, not sector norms. Score = 70 at benchmark, capped at 100.')
    t1, t2, t3 = st.tabs(['Liquidity', 'Solvency', 'Efficiency'])
    with t1: lines(D, ['Current Ratio', 'Quick Ratio'], 'Liquidity')
    with t2: lines(D, ['Debt/Equity', 'Interest Coverage'], 'Solvency')
    with t3:
        lines(D, ['Asset Turnover', 'Inventory Turnover', 'Receivables Turnover'], 'Turnover')
        st.metric('Receivable days (365/turnover)', f'{365/h["receivablesTurn"][-1]:.0f}', f'{365/h["receivablesTurn"][-1]-365/h["receivablesTurn"][-2]:+.0f} vs FY24', delta_color='inverse')

elif page == 'DuPont Analysis':
    st.header('DuPont Analysis'); st.latex(r'ROE = NPM \times Asset\ Turnover \times Equity\ Multiplier')
    rows = []
    for i, y in enumerate(YEARS):
        npm, at, roe, roa = h['npm'][i], h['assetTurn'][i], h['roe'][i], h['roa'][i]
        rows.append([y, npm, at, roa / 100 * 0 + (roe / roa if roa else np.nan), npm * at / 100 * 100, roa, roe])
    d = pd.DataFrame(rows, columns=['Year','NPM (%)','Asset Turnover','Equity Multiplier (ROE/ROA)','Implied ROA (NPM×AT)','Reported ROA','Reported ROE']).set_index('Year')
    st.dataframe(d.style.format('{:.2f}'), use_container_width=True)
    gap = (d['Implied ROA (NPM×AT)'] - d['Reported ROA']).abs().max()
    (st.success if gap < 1 else st.warning)(f'Max gap between NPM×AT and reported ROA: {gap:.2f} pp' + ('' if gap < 1 else ' — check asset basis / averaging.'))
    a = d.iloc[[0, -1]]; base, end = a.iloc[0], a.iloc[1]
    ch = {n: np.log(end[k] / base[k]) for n, k in [('Margin','NPM (%)'),('Turnover','Asset Turnover'),('Leverage','Equity Multiplier (ROE/ROA)')] if base[k] > 0 and end[k] > 0}
    tot = sum(ch.values()) or 1
    show(go.Figure(go.Bar(x=list(ch), y=[x / tot * 100 for x in ch.values()], marker_color='#5cc8ff')), 320, 'Share of ROE change FY21→FY25 (log decomposition, %)')
    lines(d, ['Reported ROE', 'NPM (%)'], 'ROE vs margin')

elif page == 'Growth Analysis':
    st.header('Growth Analysis'); keys = ['revenue','netIncome','eps','roe','current']
    rows = [[LBL[k], h[k][0], h[k][-1], (h[k][-1] / h[k][0] - 1) * 100 if h[k][0] else np.nan, cagr(h[k][0], h[k][-1])] for k in keys]
    st.dataframe(pd.DataFrame(rows, columns=['Metric','FY2021','FY2025','Total change (%)','CAGR (%)']).style.format({'FY2021':'{:,.2f}','FY2025':'{:,.2f}','Total change (%)':'{:+.1f}','CAGR (%)':'{:+.1f}'}), use_container_width=True, hide_index=True)
    yoy = pd.DataFrame({LBL[k]: np.array(h[k][1:]) / np.array(h[k][:-1]) * 100 - 100 for k in keys}, index=YEARS[1:]).T
    show(go.Figure(go.Heatmap(z=yoy.values, x=yoy.columns, y=yoy.index, colorscale='RdYlGn', zmid=0, text=yoy.round(1).values, texttemplate='%{text}%')), 340, 'Year-on-year change heatmap')

elif page == 'Vertical Analysis':
    st.header('Vertical / Common-Size Analysis')
    if not c['vertical']: st.info('No common-size data supplied for this company.')
    else:
        vt = c['vertical']; a, b = st.columns(2)
        for col, ks, ttl in [(a, list(vt)[:4], 'Income statement (% revenue)'), (b, list(vt)[4:], 'Balance sheet (% assets)')]:
            with col: show(go.Figure(go.Bar(x=[vt[k] for k in ks], y=ks, orientation='h', marker_color='#5cc8ff')), 300, ttl)

elif page == 'Peer Comparison':
    st.header('Peer Comparison'); rows = []
    for s, x in ALL.items():
        rows.append([s, vget(x,'revenue'), vget(x,'netIncome'), vget(x,'eps'), vget(x,'pe'), x['historical']['current'][-1], x['historical']['npm'][-1], vget(x,'roe'), x['historical']['debtEq'][-1], cagr(x['historical']['revenue'][0], x['historical']['revenue'][-1])])
    P = pd.DataFrame(rows, columns=['Company','Revenue','PAT','EPS','P/E','Current','NPM %','ROE %','D/E','Rev CAGR %']).set_index('Company')
    st.dataframe(P.style.format('{:,.2f}').background_gradient(cmap='Blues'), use_container_width=True)
    a, b = st.columns(2)
    with a:
        fig = go.Figure([go.Scatter(x=YEARS, y=np.array(x['historical']['revenue']) / x['historical']['revenue'][0] * 100, name=s, mode='lines+markers') for s, x in ALL.items()])
        show(fig, 360, 'Revenue indexed (FY2021 = 100)')
    with b:
        cols = ['NPM %', 'ROE %', 'Current', 'Rev CAGR %']; N = (P[cols] - P[cols].min()) / (P[cols].max() - P[cols].min()).replace(0, 1)
        fig = go.Figure([go.Scatterpolar(r=N.loc[s].tolist() + [N.loc[s].iloc[0]], theta=cols + [cols[0]], name=s, fill='toself', opacity=.5) for s in N.index])
        show(fig, 360, 'Relative profile (min–max normalised)')
    st.info('Descriptive only: accounting basis, business mix, commodity exposure and capital structure differ.')

elif page == 'Industry / PESTEL':
    st.header('Industry / PESTEL')
    P_ = [('Political / Regulatory','Exploration blocks, permits, fiscal terms, royalties, taxation and policy consistency affect project economics.'),('Economic','Oil/gas prices, inflation, interest and exchange rates, energy demand drive margins and capex.'),('Social','Population, industrial activity and household energy demand influence consumption.'),('Technological','Seismic imaging, reservoir analytics, automation and advanced extraction affect recovery and cost.'),('Environmental','Emissions rules, climate policy, water and methane management affect operations.'),('Legal / Geopolitical','Contracts, security, joint-venture rules and regional instability affect continuity.')]
    cols = st.columns(3)
    for i, (t, x) in enumerate(P_):
        with cols[i % 3]: st.markdown(f'<div class="card"><b>{t}</b><br>{x}</div>', unsafe_allow_html=True)

elif page == 'Risk Dashboard':
    st.header('Risk Dashboard (data-driven)')
    de, cr, ic = h['debtEq'][-1], h['current'][-1], h['interest'][-1]
    vol = np.std(h['npm']) / np.mean(h['npm']) * 100; rd = 365 / h['receivablesTurn'][-1]
    dd = (1 - h['netIncome'][-1] / max(h['netIncome'])) * 100
    gaps = abs(h['revenue'][-1] / vget(c, 'revenue') - 1) * 100
    R = [['Leverage', np.clip(de * 50, 0, 100), f'D/E {de:.2f}x'], ['Liquidity', np.clip(100 - cr * 25, 0, 100), f'Current {cr:.2f}x'],
         ['Interest cover', np.clip(100 - ic * 8, 0, 100), f'{ic:.1f}x'], ['Margin volatility', np.clip(vol * 4, 0, 100), f'CV of NPM {vol:.1f}%'],
         ['Receivables / circular debt', np.clip(rd / 2, 0, 100), f'{rd:.0f} days'], ['Earnings drawdown', np.clip(dd * 2, 0, 100), f'{dd:.1f}% below peak'],
         ['Data reliability', np.clip(gaps * 3, 0, 100), f'Revenue gap vs verified {gaps:.1f}%']]
    R = pd.DataFrame(R, columns=['Risk','Score','Evidence']); R['Level'] = pd.cut(R['Score'], [-1, 33, 66, 101], labels=['🟢 Low','🟡 Medium','🔴 High'])
    a, b = st.columns([2, 3])
    with a: st.dataframe(R.style.format({'Score':'{:.0f}'}), use_container_width=True, hide_index=True)
    with b: show(px.bar(R, x='Score', y='Risk', orientation='h', color='Score', color_continuous_scale='RdYlGn_r', range_color=[0, 100]), 380)
    st.markdown('**Structural E&P risks:** commodity price/volume, PKR/USD on imported capex, reserve depletion, circular-debt collections, fiscal-policy change.')
    st.warning('Scores are transparent heuristics for teaching, not forecasts.')

elif page == 'DCF & Monte Carlo':
    st.header('DCF Valuation'); st.caption('Illustrative model estimate — not investment advice.')
    sh = shares(c); px_mkt = vget(c, 'pe') * vget(c, 'eps'); rev0 = float(vget(c, 'revenue'))
    a, b = st.columns([1, 2])
    with a:
        g = st.number_input('Revenue growth (%)', value=min(8.0, max(0.0, round(cagr(h['revenue'][0], h['revenue'][-1]), 1))), step=.5)
        m = st.number_input('EBIT margin (%)', value=float(v and c['vertical'].get('Operating Income', 35.0) if c['vertical'] else 35.0), step=.5)
        tax = st.number_input('Tax rate (%)', value=39.0, step=1.0); capex = st.number_input('Capex (% rev)', value=8.0, step=.5)
        wc = st.number_input('WC drag (% rev)', value=2.0, step=.5); wacc = st.number_input('WACC (%)', value=14.0, step=.5)
        tg = st.number_input('Terminal growth (%)', value=3.0, step=.25); nd = st.number_input('Net debt (PKR m)', value=0.0, step=1000.0)
        st.caption(f'Implied shares ≈ {sh:,.0f}m (PAT ÷ EPS). Market price proxy = P/E × EPS = PKR {px_mkt:,.1f}.')
    if wacc <= tg: st.error('WACC must exceed terminal growth.'); st.stop()
    r = dcf(rev0, g, m, tax, capex, wc, wacc, tg, nd, sh)
    with b:
        k = st.columns(3); k[0].metric('Enterprise value', f'{fmt(r["ev"])}m'); k[1].metric('Model value / share', f'PKR {r["ps"]:,.1f}')
        k[2].metric('vs market proxy', f'{(r["ps"]/px_mkt-1)*100:+.1f}%')
        show(go.Figure(go.Waterfall(x=['PV explicit FCF','PV terminal','Net debt','Equity'], measure=['relative','relative','relative','total'], y=[r['pv'], r['pvtv'], -nd, 0])), 300, 'Value bridge (PKR m)')
        st.caption(f'Terminal value is {r["pvtv"]/r["ev"]*100:.0f}% of EV.')
    st.dataframe(pd.DataFrame(r['rows'], columns=['Year','Revenue','EBIT','FCF','Discounted FCF']).style.format('{:,.0f}'), use_container_width=True, hide_index=True)
    t1, t2 = st.tabs(['Sensitivity (WACC × terminal g)', 'Monte Carlo'])
    with t1:
        ws = np.arange(wacc - 3, wacc + 3.1, 1.0); gs = np.arange(max(0, tg - 2), tg + 2.1, 1.0)
        Z = [[dcf(rev0, g, m, tax, capex, wc, w, t, nd, sh)['ps'] if w > t else np.nan for w in ws] for t in gs]
        show(go.Figure(go.Heatmap(z=Z, x=[f'{w:.1f}%' for w in ws], y=[f'{t:.1f}%' for t in gs], colorscale='RdYlGn', text=np.round(Z, 0), texttemplate='%{text}')), 360, 'Value per share (PKR)')
    with t2:
        n = st.slider('Simulations', 500, 5000, 2000, 500); rng = np.random.default_rng(42); out = []
        for _ in range(n):
            w = rng.normal(wacc, 1.5); t = rng.normal(tg, .75)
            if w - t > 2: out.append(dcf(rev0, rng.normal(g, 3), rng.normal(m, 4), tax, capex, wc, w, t, nd, sh)['ps'])
        out = np.array(out); p = np.percentile(out, [5, 50, 95])
        fig = go.Figure(go.Histogram(x=out, nbinsx=50, marker_color='#5cc8ff')); fig.add_vline(x=px_mkt, line_color='#ffd166', annotation_text='Market proxy')
        show(fig, 340, 'Distribution of value per share (PKR)')
        st.write(f'P5 **{p[0]:,.0f}** | Median **{p[1]:,.0f}** | P95 **{p[2]:,.0f}** | P(value > market) = **{(out>px_mkt).mean()*100:.0f}%**')

elif page == 'Relative Valuation':
    st.header('Relative Valuation'); rows = [[s, vget(x,'pe'), vget(x,'eps'), vget(x,'pe') * vget(x,'eps'), vget(x,'dividendYield'), vget(x,'roe')] for s, x in ALL.items()]
    R = pd.DataFrame(rows, columns=['Company','P/E','EPS','Implied price','Div yield %','ROE %']).set_index('Company')
    st.dataframe(R.style.format('{:,.2f}'), use_container_width=True)
    fig = px.scatter(R.reset_index(), x='ROE %', y='P/E', size='Div yield %', text='Company', size_max=40); fig.update_traces(textposition='top center'); show(fig, 380, 'P/E vs ROE (bubble = dividend yield)')
    med = R['P/E'].median(); st.info(f'Peer median P/E = {med:.2f}x → peer-implied price for {sel}: PKR {med*vget(c,"eps"):,.1f}. Multiples must be read with growth, risk and accounting basis.')

elif page == 'Scenario Analysis':
    st.header('Bear / Base / Bull Scenarios'); a, b, d, e = st.columns(4)
    g = a.number_input('Base growth (%)', value=6.0, step=.5); m = b.number_input('Base net margin (%)', value=float(h['npm'][-1]), step=.5)
    shock = d.number_input('Shock (%)', value=10.0, step=.5); yrs = e.slider('Horizon (yrs)', 1, 5, 3)
    sh = shares(c); cases = {'Bear': (g - shock, max(1, m - shock / 2)), 'Base': (g, m), 'Bull': (g + shock, m + shock / 2)}
    fig = go.Figure(); cols = st.columns(3)
    for col, (nme, (gg, mm)) in zip(cols, cases.items()):
        path = [vget(c, 'revenue') * (1 + gg / 100) ** t for t in range(yrs + 1)]; eps = path[-1] * mm / 100 / sh
        fig.add_trace(go.Scatter(x=[2025 + t for t in range(yrs + 1)], y=path, name=nme, mode='lines+markers'))
        col.subheader(nme); col.metric(f'Revenue FY{2025+yrs}', f'{fmt(path[-1])}m'); col.metric('Profit', f'{fmt(path[-1]*mm/100)}m'); col.metric('EPS', f'PKR {eps:,.2f}', f'{(eps/vget(c,"eps")-1)*100:+.1f}% vs FY25')
    show(fig, 340, 'Revenue paths')

elif page == 'Data Integrity':
    st.header('Data Integrity & Reconciliation'); rows = []
    for s, x in DEMO.items():
        for k, lab in [('revenue','Revenue'),('netIncome','PAT'),('eps','EPS'),('pe','P/E'),('current','Current ratio'),('roe','ROE')]:
            if k in x['verified2025'] or k in ('eps',):
                sub, ver = x['historical'][k][-1], x['verified2025'][k]; var = (sub / ver - 1) * 100 if ver else np.nan
                rows.append([s, lab, sub, ver, var, '✅ Verified' if abs(var) < .5 else '🟡 Minor' if abs(var) < 5 else '🔴 Major'])
    R = pd.DataFrame(rows, columns=['Company','Metric','Submitted','Verified','Variance %','Status'])
    st.dataframe(R.style.format({'Submitted':'{:,.2f}','Verified':'{:,.2f}','Variance %':'{:+.2f}'}), use_container_width=True, hide_index=True)
    show(px.bar(R, x='Metric', y='Variance %', color='Company', barmode='group'), 320, 'Submitted vs verified variance')
    st.subheader('Internal consistency (selected company)'); ch = []
    for i, y in enumerate(YEARS):
        implied = h['netIncome'][i] / h['revenue'][i] * 100; ch.append([y, h['npm'][i], implied, h['npm'][i] - implied, h['npm'][i] * h['assetTurn'][i] / 100 - h['roa'][i] / 100 * 100 * 0])
    C = pd.DataFrame(ch, columns=['Year','Reported NPM','NI/Revenue','Gap (pp)','NPM×AT']).drop(columns='NPM×AT')
    st.dataframe(C.style.format('{:.2f}', subset=C.columns[1:]), use_container_width=True, hide_index=True)
    st.info('Source priority: audited issuer annual report → PSX issuer page → licensed data provider.')

elif page == 'Import & Export':
    st.header('Import Company'); tpl = {'symbol':'NEWCO','name':'Example Company','years':YEARS,**{k: [1, 2, 3, 4, 5] for k in HK},'source':'Source / URL'}
    tpl.update(revenue=[100,110,120,130,140], netIncome=[10,12,14,15,16], npm=[10,10.91,11.67,11.54,11.43], roa=[5,5.5,6,6.2,6.5], roe=[8,9,10,10.5,11], current=[2,2.1,2.2,2.3,2.4], quick=[1.8,1.9,2,2.1,2.2], debtEq=[.5,.48,.45,.42,.4], interest=[4,4.5,5,5.2,5.5], assetTurn=[.5,.52,.54,.56,.58], inventoryTurn=[5,5.2,5.4,5.6,5.8], receivablesTurn=[4,4.1,4.2,4.3,4.4], pe=[10,9.5,9,8.5,8], eps=[2,2.4,2.8,3,3.2], dividendYield=[2,2.2,2.4,2.5,2.6])
    up = st.file_uploader('Upload JSON', type='json'); raw = up.read().decode() if up else st.text_area('…or paste JSON', json.dumps(tpl, indent=1), height=380)
    if st.button('Validate & add company', type='primary'):
        try:
            x = json.loads(raw); miss = [k for k in tpl if k not in x]
            if miss: st.error('Missing: ' + ', '.join(miss))
            elif any(len(x[k]) != 5 for k in HK + ['years']): st.error('Every series needs exactly 5 values.')
            elif x['years'] != sorted(x['years']): st.error('Years must be oldest → newest.')
            elif any(x['revenue'][i] and abs(x['netIncome'][i] / x['revenue'][i] * 100 - x['npm'][i]) > 2 for i in range(5)): st.warning('NPM inconsistent with NI/Revenue (>2pp). Fix data before adding.')
            else:
                st.session_state.custom[x['symbol']] = mk(x['name'], 'User-imported company.', [x[k] for k in HK],
                    {'revenue': x['revenue'][-1], 'netIncome': x['netIncome'][-1], 'eps': x['eps'][-1], 'pe': x['pe'][-1]}, None, [(x['source'], '')])
                st.success(f'{x["symbol"]} added — select it in the sidebar (rerun to refresh).')
        except Exception as e: st.error(f'Invalid input: {e}')
    st.header('Export'); a, b = st.columns(2)
    a.download_button('⬇ Dataset (CSV)', D.to_csv().encode(), f'{sel}_dataset.csv', 'text/csv')
    b.download_button('⬇ Scorecard (CSV)', scorecard(c).to_csv(index=False).encode(), f'{sel}_scorecard.csv', 'text/csv')

elif page == 'References':
    st.header('References')
    for t, u in c['sources']: st.markdown(f'<div class="card"><b>{t}</b><br><a href="{u}" target="_blank">{u}</a></div>', unsafe_allow_html=True)
    st.code('Streamlit UI → authorized backend/data adapter → (PSX feed | annual-report parser | cached dataset) → normalization + source metadata → ratio engine → charts / valuation / scenarios')
    st.warning('Never place data-provider credentials in frontend code.')

st.divider()
st.caption('COMSATS University Islamabad • Business Finance • Instructor: Miss Sania Khalid • Student: Muhammad Abubakar')
st.caption(f'Generated {datetime.now():%Y-%m-%d %H:%M} | FY2021–FY2025 | requires: streamlit pandas numpy plotly')