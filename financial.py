from pathlib import Path
from textwrap import dedent


# ============================================================
# PSX FIVE-YEAR FINANCIAL ANALYSIS DASHBOARD
# Generates a standalone HTML dashboard.
# ============================================================

html = dedent(r'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>PSX Five-Year Financial Analysis Dashboard</title>
  <meta
    name="description"
    content="Academic five-year financial analysis dashboard for PSX-listed companies."
  />

  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>

  <style>
    :root{
      --bg:#07111f;
      --panel:#0d1b2e;
      --panel2:#11243a;
      --text:#eaf2fb;
      --muted:#9fb0c2;
      --line:#20364d;
      --accent:#5cc8ff;
      --accent2:#73e0b4;
      --warn:#ffd166;
      --danger:#ff7d7d;
      --shadow:0 12px 30px rgba(0,0,0,.22);
      --radius:16px;
    }

    *{
      box-sizing:border-box;
    }

    html{
      scroll-behavior:smooth;
    }

    body{
      margin:0;
      background:linear-gradient(
        180deg,
        #06101d,
        #091626 45%,
        #07111f
      );
      color:var(--text);
      font-family:
        Inter,
        system-ui,
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        Roboto,
        Arial,
        sans-serif;
    }

    a{
      color:var(--accent);
      text-decoration:none;
    }

    a:hover{
      text-decoration:underline;
    }

    .app{
      display:grid;
      grid-template-columns:260px 1fr;
      min-height:100vh;
    }

    aside{
      position:sticky;
      top:0;
      height:100vh;
      border-right:1px solid var(--line);
      background:rgba(6,16,29,.94);
      padding:22px 16px;
      overflow:auto;
    }

    .brand{
      font-weight:800;
      font-size:18px;
      line-height:1.15;
      margin-bottom:4px;
    }

    .brand small{
      display:block;
      font-size:11px;
      color:var(--muted);
      font-weight:600;
      margin-top:5px;
    }

    nav{
      margin-top:20px;
    }

    nav a{
      display:block;
      padding:10px 12px;
      border-radius:10px;
      color:#c7d6e6;
      margin:3px 0;
      font-size:13px;
    }

    nav a:hover{
      background:#102239;
      text-decoration:none;
      color:#fff;
    }

    main{
      min-width:0;
    }

    .topbar{
      position:sticky;
      top:0;
      z-index:20;
      display:flex;
      gap:12px;
      align-items:center;
      justify-content:space-between;
      padding:14px 22px;
      border-bottom:1px solid var(--line);
      background:rgba(7,17,31,.88);
      backdrop-filter:blur(16px);
    }

    .controls{
      display:flex;
      gap:8px;
      flex-wrap:wrap;
      align-items:center;
    }

    select,
    input,
    button,
    textarea{
      font:inherit;
    }

    select,
    input{
      background:#0b192b;
      border:1px solid var(--line);
      color:var(--text);
      padding:9px 11px;
      border-radius:10px;
      outline:none;
    }

    button{
      border:1px solid var(--line);
      background:#10243a;
      color:#eaf2fb;
      padding:9px 12px;
      border-radius:10px;
      cursor:pointer;
    }

    button:hover{
      background:#17334f;
    }

    .primary{
      background:#124665;
      border-color:#276887;
    }

    .primary:hover{
      background:#175873;
    }

    .content{
      padding:26px;
      max-width:1500px;
      margin:0 auto;
    }

    .hero{
      display:grid;
      grid-template-columns:1.3fr .7fr;
      gap:18px;
      margin-bottom:18px;
    }

    .heroCard,
    .card{
      background:
        linear-gradient(
          180deg,
          rgba(17,36,58,.94),
          rgba(12,28,46,.94)
        );
      border:1px solid var(--line);
      border-radius:var(--radius);
      box-shadow:var(--shadow);
    }

    .heroCard{
      padding:24px;
    }

    h1,
    h2,
    h3{
      margin:0 0 10px;
    }

    h1{
      font-size:30px;
      letter-spacing:-.6px;
    }

    h2{
      font-size:20px;
    }

    h3{
      font-size:14px;
    }

    p{
      color:#c4d1df;
      line-height:1.55;
    }

    .eyebrow{
      text-transform:uppercase;
      letter-spacing:1.2px;
      color:var(--accent);
      font-weight:800;
      font-size:11px;
    }

    .warning{
      border-left:4px solid var(--warn);
      background:#201c0a;
      padding:14px 16px;
      border-radius:12px;
      margin-top:14px;
      color:#f6e6a9;
    }

    .grid{
      display:grid;
      gap:14px;
    }

    .grid.kpis{
      grid-template-columns:repeat(6,minmax(0,1fr));
      margin:16px 0;
    }

    .kpi{
      padding:15px;
    }

    .kpi .label{
      font-size:11px;
      color:var(--muted);
      text-transform:uppercase;
      letter-spacing:.7px;
    }

    .kpi .value{
      font-size:23px;
      font-weight:800;
      margin-top:6px;
    }

    .grid.two{
      grid-template-columns:repeat(2,minmax(0,1fr));
    }

    .grid.three{
      grid-template-columns:repeat(3,minmax(0,1fr));
    }

    .card{
      padding:18px;
    }

    .card .sub{
      color:var(--muted);
      font-size:12px;
    }

    section{
      scroll-margin-top:82px;
      margin:22px 0;
    }

    .section-head{
      display:flex;
      justify-content:space-between;
      align-items:end;
      gap:14px;
      margin-bottom:12px;
    }

    .chartWrap{
      height:340px;
    }

    .tableWrap{
      overflow:auto;
    }

    table{
      width:100%;
      border-collapse:collapse;
      font-size:13px;
    }

    th,
    td{
      padding:10px 9px;
      border-bottom:1px solid var(--line);
      text-align:right;
      white-space:nowrap;
    }

    th:first-child,
    td:first-child{
      text-align:left;
    }

    th{
      color:#b7c8da;
      font-size:11px;
      text-transform:uppercase;
      letter-spacing:.55px;
    }

    .status{
      display:inline-flex;
      align-items:center;
      padding:4px 8px;
      border-radius:99px;
      font-size:11px;
      font-weight:800;
    }

    .ok{
      background:#113728;
      color:#8ff0bf;
    }

    .warn{
      background:#3a2d0b;
      color:#ffe28b;
    }

    .info{
      background:#102b40;
      color:#8ddcff;
    }

    .muted{
      color:var(--muted);
    }

    .formula{
      font-family:
        ui-monospace,
        SFMono-Regular,
        Menlo,
        Monaco,
        Consolas,
        monospace;
      background:#071421;
      border:1px solid var(--line);
      padding:11px;
      border-radius:10px;
      color:#cde7ff;
      font-size:12px;
      overflow:auto;
      white-space:pre-wrap;
    }

    .metricList{
      display:grid;
      grid-template-columns:1fr auto;
      gap:7px;
      font-size:13px;
    }

    .metricList div{
      padding:7px 0;
      border-bottom:1px solid #1a3046;
    }

    .pillRow{
      display:flex;
      gap:7px;
      flex-wrap:wrap;
    }

    .pill{
      padding:6px 9px;
      background:#0a1b2e;
      border:1px solid var(--line);
      border-radius:999px;
      font-size:11px;
      color:#cfe0f1;
    }

    .risk{
      display:grid;
      grid-template-columns:1fr 100px 1.5fr;
      gap:1px;
      background:var(--line);
      border:1px solid var(--line);
      border-radius:12px;
      overflow:hidden;
    }

    .risk div{
      background:#0d1b2e;
      padding:10px;
      font-size:12px;
    }

    .scenarioGrid{
      display:grid;
      grid-template-columns:repeat(3,minmax(0,1fr));
      gap:12px;
    }

    .scenario{
      padding:15px;
      border:1px solid var(--line);
      border-radius:14px;
      background:#0a192b;
    }

    .scenario h3{
      margin-bottom:8px;
    }

    .scenario .big{
      font-size:20px;
      font-weight:800;
    }

    .sourceBox{
      font-size:12px;
      line-height:1.55;
    }

    .small{
      font-size:11px;
    }

    textarea{
      width:100%;
      min-height:300px;
      background:#071421;
      color:#dcecff;
      border:1px solid var(--line);
      padding:12px;
      border-radius:12px;
      resize:vertical;
      font-family:
        ui-monospace,
        SFMono-Regular,
        Menlo,
        Monaco,
        Consolas,
        monospace;
      font-size:12px;
    }

    footer{
      padding:30px 0 60px;
      color:var(--muted);
      font-size:12px;
    }

    .empty{
      color:var(--muted);
      padding:20px;
      text-align:center;
    }

    @media(max-width:1100px){
      .app{
        grid-template-columns:1fr;
      }

      aside{
        position:static;
        height:auto;
        border-right:0;
        border-bottom:1px solid var(--line);
      }

      nav{
        display:flex;
        flex-wrap:wrap;
        gap:3px;
      }

      nav a{
        padding:7px 9px;
      }

      .grid.kpis{
        grid-template-columns:repeat(3,minmax(0,1fr));
      }

      .hero{
        grid-template-columns:1fr;
      }
    }

    @media(max-width:720px){
      .content{
        padding:16px;
      }

      .topbar{
        position:static;
        align-items:flex-start;
        flex-direction:column;
      }

      .grid.two,
      .grid.three,
      .scenarioGrid{
        grid-template-columns:1fr;
      }

      .grid.kpis{
        grid-template-columns:repeat(2,minmax(0,1fr));
      }

      .chartWrap{
        height:280px;
      }

      h1{
        font-size:25px;
      }

      .risk{
        grid-template-columns:1fr;
      }
    }

    @media print{
      aside,
      .topbar,
      button,
      textarea{
        display:none !important;
      }

      .app{
        display:block;
      }

      body{
        background:white;
        color:black;
      }

      .card,
      .heroCard{
        box-shadow:none;
        break-inside:avoid;
      }
    }
  </style>
</head>

<body>

<div class="app">

  <aside>
    <div class="brand">
      PSX Financial Lab
      <small>Five-Year Academic Analysis Engine</small>
    </div>

    <nav>
      <a href="#dashboard">Executive Dashboard</a>
      <a href="#financials">Financial Performance</a>
      <a href="#liquidity">Liquidity</a>
      <a href="#profitability">Profitability</a>
      <a href="#solvency">Solvency</a>
      <a href="#efficiency">Efficiency</a>
      <a href="#market">Market Ratios</a>
      <a href="#dupont">DuPont</a>
      <a href="#horizontal">Horizontal Analysis</a>
      <a href="#vertical">Vertical Analysis</a>
      <a href="#benchmark">Cross-Company Comparison</a>
      <a href="#industry">Industry / PESTEL</a>
      <a href="#risk">Risk Dashboard</a>
      <a href="#dcf">DCF Valuation</a>
      <a href="#relative">Relative Valuation</a>
      <a href="#scenarios">Scenario Analysis</a>
      <a href="#integrity">Data Integrity</a>
      <a href="#import">Import Data</a>
      <a href="#references">References</a>
    </nav>
  </aside>


  <main>

    <div class="topbar">

      <div class="controls">

        <label class="small muted">
          Demo company
        </label>

        <select id="companySelect"></select>

        <input
          id="symbolInput"
          value="OGDC"
          maxlength="12"
          placeholder="PSX symbol"
        />

        <button
          class="primary"
          id="loadSymbol"
        >
          Load company
        </button>

      </div>


      <div class="controls">

        <span
          class="status info"
          id="dataModeBadge"
        >
          Submitted + FY2025 verified snapshot
        </span>

        <button id="printBtn">
          Print / PDF
        </button>

      </div>

    </div>


    <div class="content">


      <!-- ================================================= -->
      <!-- DASHBOARD -->
      <!-- ================================================= -->

      <section id="dashboard">

        <div class="hero">

          <div class="heroCard">

            <div class="eyebrow">
              COMSATS University Islamabad • Department of Management Sciences
            </div>

            <h1>
              General PSX Five-Year Financial Analysis Dashboard
            </h1>

            <p>
              Academic analysis of scale, liquidity, profitability,
              solvency, efficiency, market ratios, valuation and scenario
              assumptions. The dashboard is designed to work with any
              PSX-listed company once a permitted data adapter supplies
              the annual financial statements.
            </p>

            <div class="pillRow">
              <span class="pill">FY2021–FY2025 historical layer</span>
              <span class="pill">Verified-source snapshot</span>
              <span class="pill">Scenario ranges</span>
              <span class="pill">DCF + relative valuation</span>
              <span class="pill">Data-integrity controls</span>
            </div>

            <div class="warning">
              <b>Data-quality warning:</b>
              accounting datasets can differ across reports,
              restatements, consolidated/unconsolidated statements
              and standardized data vendors. The dashboard does not
              silently merge conflicting values.
            </div>

          </div>


          <div class="card">

            <h3>
              Selected company
            </h3>

            <div id="companySummary"></div>

          </div>

        </div>


        <div
          class="grid kpis"
          id="kpis"
        ></div>

      </section>



      <!-- ================================================= -->
      <!-- FINANCIAL PERFORMANCE -->
      <!-- ================================================= -->

      <section id="financials">

        <div class="section-head">

          <div>
            <h2>Financial Performance</h2>

            <div class="sub">
              Five-year historical trend from the active demo dataset
            </div>
          </div>

        </div>


        <div class="grid two">

          <div class="card">
            <h3>Revenue Trend</h3>
            <div class="chartWrap">
              <canvas id="revenueChart"></canvas>
            </div>
          </div>


          <div class="card">
            <h3>Profitability Trend</h3>
            <div class="chartWrap">
              <canvas id="profitChart"></canvas>
            </div>
          </div>

        </div>

      </section>



      <!-- ================================================= -->
      <!-- LIQUIDITY -->
      <!-- ================================================= -->

      <section id="liquidity">

        <div class="section-head">
          <h2>Liquidity Analysis</h2>
        </div>

        <div class="grid two">

          <div class="card">

            <h3>
              Current / Quick Ratio
            </h3>

            <div class="chartWrap">
              <canvas id="liquidityChart"></canvas>
            </div>

          </div>


          <div class="card">

            <h3>
              Interpretation
            </h3>

            <p id="liquidityText"></p>

          </div>

        </div>

      </section>



      <!-- ================================================= -->
      <!-- PROFITABILITY -->
      <!-- ================================================= -->

      <section id="profitability">

        <div class="section-head">
          <h2>Profitability Analysis</h2>
        </div>

        <div class="grid two">

          <div class="card">

            <h3>
              NPM / ROA / ROE
            </h3>

            <div class="chartWrap">
              <canvas id="profitRatiosChart"></canvas>
            </div>

          </div>


          <div class="card">

            <h3>
              Latest profitability snapshot
            </h3>

            <div id="profitMetrics"></div>

          </div>

        </div>

      </section>



      <!-- ================================================= -->
      <!-- SOLVENCY -->
      <!-- ================================================= -->

      <section id="solvency">

        <div class="section-head">
          <h2>Solvency & Coverage</h2>
        </div>

        <div class="grid two">

          <div class="card">

            <h3>
              Debt-to-Equity / Interest Coverage
            </h3>

            <div class="chartWrap">
              <canvas id="solvencyChart"></canvas>
            </div>

          </div>


          <div class="card">

            <h3>
              Interpretation
            </h3>

            <p id="solvencyText"></p>

          </div>

        </div>

      </section>



      <!-- ================================================= -->
      <!-- EFFICIENCY -->
      <!-- ================================================= -->

      <section id="efficiency">

        <div class="section-head">
          <h2>Efficiency Analysis</h2>
        </div>

        <div class="grid two">

          <div class="card">

            <h3>
              Asset / Inventory / Receivables Turnover
            </h3>

            <div class="chartWrap">
              <canvas id="efficiencyChart"></canvas>
            </div>

          </div>


          <div class="card">

            <h3>
              Collection indicator
            </h3>

            <p id="efficiencyText"></p>

          </div>

        </div>

      </section>



      <!-- ================================================= -->
      <!-- MARKET -->
      <!-- ================================================= -->

      <section id="market">

        <div class="section-head">
          <h2>Market Ratios</h2>
        </div>

        <div class="grid two">

          <div class="card">

            <h3>
              P/E Trend
            </h3>

            <div class="chartWrap">
              <canvas id="peChart"></canvas>
            </div>

          </div>


          <div class="card">

            <h3>
              Market snapshot
            </h3>

            <div id="marketMetrics"></div>

          </div>

        </div>

      </section>



      <!-- ================================================= -->
      <!-- DUPONT -->
      <!-- ================================================= -->

      <section id="dupont">

        <div class="section-head">
          <h2>DuPont Analysis</h2>
        </div>

        <div class="card">

          <div class="formula">
ROE = Net Profit Margin × Asset Turnover × Equity Multiplier
          </div>

          <div
            class="tableWrap"
            style="margin-top:12px"
          >
            <table id="dupontTable"></table>
          </div>

          <p class="small muted">
            For a production version, calculate these components directly
            from audited statement inputs rather than accepting a manually
            entered ROE.
          </p>

        </div>

      </section>



      <!-- ================================================= -->
      <!-- HORIZONTAL -->
      <!-- ================================================= -->

      <section id="horizontal">

        <div class="section-head">

          <h2>
            Horizontal Analysis
          </h2>

          <div class="sub">
            2021 base → 2025
          </div>

        </div>

        <div class="card">

          <div class="tableWrap">
            <table id="horizontalTable"></table>
          </div>

        </div>

      </section>



      <!-- ================================================= -->
      <!-- VERTICAL -->
      <!-- ================================================= -->

      <section id="vertical">

        <div class="section-head">
          <h2>Vertical / Common-Size Analysis</h2>
        </div>

        <div class="grid two">

          <div class="card">

            <h3>
              Income statement structure
            </h3>

            <div class="tableWrap">
              <table id="verticalIncome"></table>
            </div>

          </div>


          <div class="card">

            <h3>
              Balance sheet structure
            </h3>

            <div class="tableWrap">
              <table id="verticalBalance"></table>
            </div>

          </div>

        </div>

      </section>



      <!-- ================================================= -->
      <!-- BENCHMARK -->
      <!-- ================================================= -->

      <section id="benchmark">

        <div class="section-head">

          <h2>
            Cross-Company Comparison
          </h2>

          <div class="sub">
            Snapshot comparison without a hard-coded winner label
          </div>

        </div>

        <div class="card">

          <div class="tableWrap">
            <table id="benchmarkTable"></table>
          </div>

        </div>

      </section>



      <!-- ================================================= -->
      <!-- INDUSTRY -->
      <!-- ================================================= -->

      <section id="industry">

        <div class="section-head">
          <h2>Industry & PESTEL</h2>
        </div>

        <div
          class="grid three"
          id="pestelGrid"
        ></div>

      </section>



      <!-- ================================================= -->
      <!-- RISK -->
      <!-- ================================================= -->

      <section id="risk">

        <div class="section-head">
          <h2>Risk Dashboard</h2>
        </div>

        <div class="risk">

          <div><b>Risk area</b></div>
          <div><b>Level</b></div>
          <div><b>Evidence / monitoring factor</b></div>

          <div>Leverage</div>
          <div>
            <span class="status ok">Low</span>
          </div>
          <div>
            Review debt, lease liabilities and interest coverage;
            do not infer zero risk from a low debt-to-equity ratio.
          </div>

          <div>Liquidity</div>
          <div>
            <span class="status info">Monitor</span>
          </div>
          <div>
            Track current assets, current liabilities, cash,
            short-term investments and receivable concentration.
          </div>

          <div>Commodity exposure</div>
          <div>
            <span class="status warn">High</span>
          </div>
          <div>
            Oil/gas prices and production volumes can materially
            affect revenue and margins.
          </div>

          <div>Receivables / circular debt</div>
          <div>
            <span class="status warn">High</span>
          </div>
          <div>
            Monitor debtor days, collections, trade debt and
            operating cash flow.
          </div>

          <div>FX / imported capex</div>
          <div>
            <span class="status warn">Medium</span>
          </div>
          <div>
            PKR/USD movements can raise the local cost of imported
            equipment and development inputs.
          </div>

          <div>Reserve depletion</div>
          <div>
            <span class="status warn">Medium</span>
          </div>
          <div>
            Monitor reserve replacement, discovery success,
            mature-field decline and development activity.
          </div>

        </div>

      </section>



      <!-- ================================================= -->
      <!-- DCF -->
      <!-- ================================================= -->

      <section id="dcf">

        <div class="section-head">

          <h2>
            DCF Valuation Framework
          </h2>

          <div class="sub">
            Model-generated estimate, not a guaranteed future outcome
          </div>

        </div>

        <div class="grid two">

          <div class="card">

            <h3>
              Interactive assumptions
            </h3>

            <div class="metricList">

              <div>Revenue growth</div>
              <div>
                <input
                  id="dcfGrowth"
                  type="number"
                  step="0.1"
                  value="6"
                />
              </div>

              <div>EBIT / operating margin</div>
              <div>
                <input
                  id="dcfMargin"
                  type="number"
                  step="0.1"
                  value="30"
                />
              </div>

              <div>WACC</div>
              <div>
                <input
                  id="dcfWacc"
                  type="number"
                  step="0.1"
                  value="14"
                />
              </div>

              <div>Terminal growth</div>
              <div>
                <input
                  id="dcfTg"
                  type="number"
                  step="0.1"
                  value="3"
                />
              </div>

              <div>Capex (% revenue)</div>
              <div>
                <input
                  id="dcfCapex"
                  type="number"
                  step="0.1"
                  value="8"
                />
              </div>

              <div>
                Working-capital drag (% revenue)
              </div>
              <div>
                <input
                  id="dcfWc"
                  type="number"
                  step="0.1"
                  value="2"
                />
              </div>

              <div>
                Current net debt (PKR m)
              </div>
              <div>
                <input
                  id="dcfNetDebt"
                  type="number"
                  step="1000"
                  value="0"
                />
              </div>

              <div>
                Diluted shares (m)
              </div>
              <div>
                <input
                  id="dcfShares"
                  type="number"
                  step="1"
                  value="4301"
                />
              </div>

            </div>

            <div style="margin-top:12px">

              <button
                class="primary"
                id="runDcf"
              >
                Recalculate DCF
              </button>

            </div>

          </div>


          <div class="card">

            <h3>
              Valuation output
            </h3>

            <div id="dcfOutput"></div>

            <div
              class="formula"
              style="margin-top:12px"
            >
FCF = Operating Cash Flow − Capex
PV(FCF) = FCF / (1 + WACC)^t
TV = FCFₙ × (1 + g) / (WACC − g)
EV = PV(FCF) + PV(TV)
Equity Value = EV + Cash − Debt
            </div>

          </div>

        </div>

      </section>



      <!-- ================================================= -->
      <!-- RELATIVE VALUATION -->
      <!-- ================================================= -->

      <section id="relative">

        <div class="section-head">
          <h2>Relative Valuation</h2>
        </div>

        <div class="card">

          <p>
            Relative valuation is descriptive. A lower P/E or P/B does
            not automatically prove that a security is undervalued;
            interpret the multiple alongside growth, profitability,
            capital intensity, risk and accounting basis.
          </p>

          <div class="tableWrap">
            <table id="relativeTable"></table>
          </div>

        </div>

      </section>



      <!-- ================================================= -->
      <!-- SCENARIOS -->
      <!-- ================================================= -->

      <section id="scenarios">

        <div class="section-head">
          <h2>Base / Bull / Bear Scenario Engine</h2>
        </div>

        <div class="card">

          <div class="grid three">

            <div>

              <label class="small muted">
                Scenario growth range (%)
              </label>

              <input
                id="scBase"
                type="number"
                value="6"
                style="width:100%"
              />

            </div>


            <div>

              <label class="small muted">
                Base margin (%)
              </label>

              <input
                id="scMargin"
                type="number"
                value="35"
                style="width:100%"
              />

            </div>


            <div>

              <label class="small muted">
                Commodity shock (%)
              </label>

              <input
                id="scShock"
                type="number"
                value="10"
                style="width:100%"
              />

            </div>

          </div>


          <div
            class="scenarioGrid"
            style="margin-top:14px"
            id="scenarioCards"
          ></div>

        </div>

      </section>



      <!-- ================================================= -->
      <!-- INTEGRITY -->
      <!-- ================================================= -->

      <section id="integrity">

        <div class="section-head">
          <h2>Data Integrity & Source Reconciliation</h2>
        </div>

        <div class="card">

          <div
            class="pillRow"
            style="margin-bottom:12px"
          >

            <span class="status ok">
              Verified
            </span>

            <span class="status info">
              Submitted
            </span>

            <span class="status warn">
              Reconciliation Required
            </span>

          </div>


          <div class="tableWrap">
            <table id="integrityTable"></table>
          </div>


          <p class="small muted">
            Source priority in production: audited issuer annual report /
            financial highlights → PSX issuer page → permitted standardized
            data provider. Keep source basis, period, currency/unit and
            consolidation status attached to each value.
          </p>

        </div>

      </section>



      <!-- ================================================= -->
      <!-- IMPORT -->
      <!-- ================================================= -->

      <section id="import">

        <div class="section-head">

          <h2>
            General Company Import
          </h2>

          <div class="sub">
            Use this instead of rebuilding the UI for every company
          </div>

        </div>


        <div class="grid two">

          <div class="card">

            <h3>
              JSON schema
            </h3>

            <p class="small">
              Paste a company object using the structure shown below.
              For five-year data, years should be ordered oldest → newest.
            </p>

            <textarea id="jsonInput"></textarea>

            <div style="margin-top:10px">

              <button
                class="primary"
                id="importJson"
              >
                Import JSON into dashboard
              </button>

            </div>

          </div>


          <div class="card">

            <h3>
              Production connector design
            </h3>

            <div class="formula">
Frontend
  ↓
GET /api/company/:symbol?from=2021&to=2025
  ↓
Data adapter
  ├─ authorized PSX / licensed market feed
  ├─ issuer annual-report parser
  └─ cached normalized financial dataset
  ↓
Normalization + source metadata
  ↓
Ratio engine
  ↓
Charts / benchmarking / scenarios / DCF
            </div>

            <p class="small">
              Do not put credentials in browser JavaScript.
              Keep market-data licensing, access control, caching
              and source attribution on the server.
            </p>

          </div>

        </div>

      </section>



      <!-- ================================================= -->
      <!-- REFERENCES -->
      <!-- ================================================= -->

      <section id="references">

        <div class="section-head">
          <h2>References & Official Validation</h2>
        </div>

        <div
          class="grid three"
          id="referencesGrid"
        ></div>

      </section>



      <footer>

        <b>Academic context:</b>
        COMSATS University Islamabad • Business Finance •
        Instructor: Miss Sania Khalid • Student: Muhammad Abubakar.

        <br/>

        Historical period:
        FY2021–FY2025.

        FY2026 information is treated separately as a latest-update
        context and is not silently inserted into the formal five-year
        historical series.

      </footer>

    </div>

  </main>

</div>



<script>

const years = [2021, 2022, 2023, 2024, 2025];


const demo = {

  OGDC: {

    name:
      "Oil & Gas Development Company Limited",

    short:
      "OGDC",

    description:
      "Large Pakistani upstream E&P company. Demo historical layer follows the submitted assignment dataset; FY2025 verified snapshot is kept separately.",

    historical: {

      revenue:
        [239774,279816,324282,378423,401178],

      netIncome:
        [91534,133430,224617,208976,169903],

      npm:
        [38.28,39.88,54.31,45.07,42.35],

      roa:
        [9.57,11.84,15.77,13.03,10.27],

      roe:
        [11.89,15.28,20.74,16.71,12.60],

      current:
        [6.40,5.60,5.96,5.86,8.97],

      quick:
        [6.21,5.45,5.81,5.73,8.72],

      debtEq:
        [0,0,0,0,0],

      interest:
        [5.92,9.75,6.17,3.74,3.54],

      assetTurn:
        [.25,.30,.29,.29,.24],

      inventoryTurn:
        [5.08,5.78,6.15,7.38,5.53],

      receivablesTurn:
        [.63,.69,.67,.68,.61],

      pe:
        [9.40,7.07,4.79,4.73,4.56],

      eps:
        [21.28,31.11,52.23,48.59,39.50],

      dividendYield:
        [3.45,3.30,3.42,4.40,2.81]
    },

    verified2025: {

      revenue:401178,
      netIncome:169904,
      eps:39.50,
      pe:5.58,
      marketCap:948610,

      sourceLabel:
        "OGDCL FY2025"
    },

    vertical: {

      costRevenue:42.28,
      grossMargin:57.72,
      operatingMargin:46.40,
      netMargin:42.35,

      currentAssets:42.47,
      netPpe:57.53,

      totalLiabilities:25.06,
      totalEquity:74.94
    },

    sources: [

      [
        "PSX company page",
        "https://dps.psx.com.pk/company/OGDC"
      ],

      [
        "OGDCL Financial Reports",
        "https://ogdcl.com/investors/financial-reports?language=en"
      ],

      [
        "OGDCL Financial Highlights",
        "https://ogdcl.com/investors/financial-highlights"
      ]

    ]
  },


  PPL: {

    name:
      "Pakistan Petroleum Limited",

    short:
      "PPL",

    description:
      "Major Pakistani E&P company. Demo historical layer follows the submitted assignment dataset; FY2025 verified snapshot uses the issuer financial highlights.",

    historical: {

      revenue:
        [149279,203811,288053,291241,244977],

      netIncome:
        [52283,54356,97937,114309,89949],

      npm:
        [35.02,26.67,33.75,39.65,36.72],

      roa:
        [9.73,8.65,12.24,12.65,9.68],

      roe:
        [13.44,12.50,17.98,18.02,12.76],

      current:
        [4.37,3.52,3.32,3.55,4.78],

      quick:
        [4.31,3.48,3.28,3.52,4.72],

      debtEq:
        [0,0,0,0,0],

      interest:
        [17.25,13.42,12.89,8.85,6.55],

      assetTurn:
        [.28,.32,.36,.32,.26],

      inventoryTurn:
        [13.79,12.99,16.23,14.78,10.49],

      receivablesTurn:
        [.53,.56,.56,.50,.41],

      pe:
        [6.25,6.51,4.48,4.24,4.54],

      eps:
        [19.21,19.98,35.73,42.44,33.06],

      dividendYield:
        [2.92,1.92,3.75,4.17,3.33]
    },

    verified2025: {

      revenue:242516,
      netIncome:92027,
      eps:33.82,
      pe:5.03,
      current:4.81,
      roe:13,
      tradeDebts:592404,

      sourceLabel:
        "PPL FY2024–25"
    },

    vertical: {

      costRevenue:37.72,
      grossMargin:62.28,
      operatingMargin:46.40,
      netMargin:36.72,

      currentAssets:75.53,
      netPpe:15.54,

      totalLiabilities:24.14,
      totalEquity:75.86
    },

    sources: [

      [
        "PSX company page",
        "https://dps.psx.com.pk/company/PPL"
      ],

      [
        "PPL Annual Report 2025",
        "https://www.ppl.com.pk/content/annual-report-2025"
      ],

      [
        "PPL Financial Highlights",
        "https://www.ppl.com.pk/content/financial-highlights"
      ]

    ]
  },


  MARI: {

    name:
      "Mari Energies Limited",

    short:
      "MARI",

    description:
      "Pakistani E&P company formerly known as Mari Petroleum Company Limited. Demo historical layer follows the submitted assignment dataset; official FY2025 figures are shown as a separate verified snapshot.",

    historical: {

      revenue:
        [63703,83135,128221,159731,141486],

      netIncome:
        [31445,33064,56129,77288,65369],

      npm:
        [49.36,39.77,43.77,48.39,46.20],

      roa:
        [20.91,17.86,22.05,22.30,15.36],

      roe:
        [27.22,25.27,33.33,34.36,23.87],

      current:
        [3.61,2.26,1.98,2.79,2.97],

      quick:
        [3.49,2.17,1.86,2.66,2.78],

      debtEq:
        [0,.01,.01,0,.04],

      interest:
        [10.27,19.77,17.21,10.50,7.86],

      assetTurn:
        [.42,.45,.50,.46,.33],

      inventoryTurn:
        [5.12,4.93,3.76,4.04,3.17],

      receivablesTurn:
        [2.27,2.57,2.08,1.97,1.63],

      pe:
        [13.36,13.80,9.63,8.54,9.18],

      eps:
        [26.19,27.54,46.75,64.37,54.45],

      dividendYield:
        [4.48,3.63,3.63,4.69,4.34]
    },

    verified2025: {

      revenue:177097,
      netIncome:65136,

      epsRestated:54.25,
      epsConsolidated:54.45,

      pe:11.56,
      current:2.81,
      quick:2.59,
      roe:26.23,
      assetTurn:.46,
      dividendYield:7.20,

      sourceLabel:
        "MariEnergies FY2024–25"
    },

    vertical: {

      costRevenue:28.37,
      grossMargin:71.63,
      operatingMargin:55.03,
      netMargin:36.78,

      currentAssets:47.90,
      netPpe:47.33,

      totalLiabilities:35.62,
      totalEquity:64.38
    },

    latest2026: {

      revenue:191663,
      netIncome:87069,
      eps:72.52,
      roe:29.31
    },

    sources: [

      [
        "PSX company page",
        "https://dps.psx.com.pk/company/MARI"
      ],

      [
        "MariEnergies Annual Reports",
        "https://www.marienergies.com.pk/investors-relations/financial-reports"
      ],

      [
        "MariEnergies Financial Highlights",
        "https://www.marienergies.com.pk/investors-relations/financial-highlights"
      ]

    ]
  }

};



const peer =
  Object.fromEntries(
    Object.entries(demo).map(
      ([key,value]) => [key,value.verified2025]
    )
  );


let active = "OGDC";

const charts = {};



function fmt(number, decimals=0){

  if(
    number === null ||
    number === undefined ||
    Number.isNaN(Number(number))
  ){
    return "—";
  }

  return Number(number).toLocaleString(
    undefined,
    {
      maximumFractionDigits:decimals,
      minimumFractionDigits:decimals
    }
  );

}



function pct(number){

  if(
    number === null ||
    number === undefined ||
    Number.isNaN(Number(number))
  ){
    return "—";
  }

  return `${fmt(number,2)}%`;

}



function destroy(id){

  if(charts[id]){
    charts[id].destroy();
    delete charts[id];
  }

}



function makeChart(id, config){

  destroy(id);

  const element =
    document.getElementById(id);

  if(!element){
    return;
  }

  charts[id] =
    new Chart(element,config);

}



function setHtml(id, html){

  const element =
    document.getElementById(id);

  if(element){
    element.innerHTML = html;
  }

}



function commonChartOptions(){

  return {

    responsive:true,

    maintainAspectRatio:false,

    plugins:{
      legend:{
        labels:{
          color:"#c8d8e8"
        }
      }
    },

    scales:{

      x:{
        ticks:{
          color:"#9fb0c2"
        },
        grid:{
          color:"#193047"
        }
      },

      y:{
        ticks:{
          color:"#9fb0c2"
        },
        grid:{
          color:"#193047"
        }
      }

    }

  };

}



function render(){

  const company =
    demo[active];

  if(!company){
    return;
  }

  const h =
    company.historical;

  const v =
    company.verified2025;


  document.getElementById(
    "companySummary"
  ).innerHTML = `

    <div
      style="
        font-size:26px;
        font-weight:900;
      "
    >
      ${company.short}
    </div>

    <div
      class="muted"
      style="
        margin:2px 0 10px;
      "
    >
      ${company.name}
    </div>

    <p class="small">
      ${company.description}
    </p>

    <div class="pillRow">

      <span class="pill">
        FY2025 submitted:
        PKR ${fmt(h.revenue[4])}m
      </span>

      <span class="pill">
        FY2025 verified:
        PKR ${fmt(v.revenue)}m
      </span>

    </div>

  `;


  document.getElementById(
    "kpis"
  ).innerHTML = [

    [
      "FY2025 verified sales",
      `PKR ${fmt(v.revenue)}m`
    ],

    [
      "FY2025 verified PAT",
      `PKR ${fmt(v.netIncome)}m`
    ],

    [
      "EPS",
      active === "MARI"
        ? `${fmt(v.epsRestated,2)} / ${fmt(v.epsConsolidated,2)}`
        : `${fmt(v.eps,2)}`
    ],

    [
      "Current ratio",
      `${fmt(
        v.current ?? h.current[4],
        2
      )}x`
    ],

    [
      "ROE",
      `${fmt(
        v.roe ?? h.roe[4],
        2
      )}%`
    ],

    [
      "P/E",
      `${fmt(v.pe,2)}x`
    ]

  ]
  .map(
    ([label,value]) => `

      <div class="card kpi">

        <div class="label">
          ${label}
        </div>

        <div class="value">
          ${value}
        </div>

      </div>

    `
  )
  .join("");


  const chartOptions =
    commonChartOptions();


  makeChart(
    "revenueChart",
    {
      type:"line",

      data:{
        labels:years,

        datasets:[

          {
            label:"Revenue (PKR m)",
            data:h.revenue,
            tension:.25,
            borderWidth:2,
            pointRadius:3
          }

        ]
      },

      options:chartOptions
    }
  );


  makeChart(
    "profitChart",
    {
      type:"line",

      data:{
        labels:years,

        datasets:[

          {
            label:"Net profit margin %",
            data:h.npm,
            tension:.25,
            borderWidth:2,
            pointRadius:3
          },

          {
            label:"ROA %",
            data:h.roa,
            tension:.25,
            borderWidth:2,
            pointRadius:3
          },

          {
            label:"ROE %",
            data:h.roe,
            tension:.25,
            borderWidth:2,
            pointRadius:3
          }

        ]
      },

      options:chartOptions
    }
  );


  makeChart(
    "liquidityChart",
    {
      type:"line",

      data:{
        labels:years,

        datasets:[

          {
            label:"Current ratio",
            data:h.current,
            tension:.25,
            borderWidth:2,
            pointRadius:3
          },

          {
            label:"Quick ratio",
            data:h.quick,
            tension:.25,
            borderWidth:2,
            pointRadius:3
          }

        ]
      },

      options:chartOptions
    }
  );


  makeChart(
    "profitRatiosChart",
    {
      type:"bar",

      data:{
        labels:years,

        datasets:[

          {
            label:"NPM %",
            data:h.npm
          },

          {
            label:"ROA %",
            data:h.roa
          },

          {
            label:"ROE %",
            data:h.roe
          }

        ]
      },

      options:chartOptions
    }
  );


  makeChart(
    "solvencyChart",
    {
      type:"line",

      data:{
        labels:years,

        datasets:[

          {
            label:"Debt / Equity",
            data:h.debtEq,
            tension:.2,
            borderWidth:2,
            pointRadius:3
          },

          {
            label:"Interest coverage",
            data:h.interest,
            tension:.2,
            borderWidth:2,
            pointRadius:3
          }

        ]
      },

      options:chartOptions
    }
  );


  makeChart(
    "efficiencyChart",
    {
      type:"line",

      data:{
        labels:years,

        datasets:[

          {
            label:"Asset turnover",
            data:h.assetTurn,
            tension:.2,
            borderWidth:2,
            pointRadius:3
          },

          {
            label:"Inventory turnover",
            data:h.inventoryTurn,
            tension:.2,
            borderWidth:3,
            pointRadius:3
          },

          {
            label:"Receivables turnover",
            data:h.receivablesTurn,
            tension:.2,
            borderWidth:2,
            pointRadius:3
          }

        ]
      },

      options:chartOptions
    }
  );


  makeChart(
    "peChart",
    {
      type:"line",

      data:{
        labels:years,

        datasets:[

          {
            label:"P/E",
            data:h.pe,
            tension:.2,
            borderWidth:2,
            pointRadius:3
          }

        ]
      },

      options:chartOptions
    }
  );


  const current =
    h.current[4];

  const quick =
    h.quick[4];

  const interest =
    h.interest[4];


  setHtml(
    "liquidityText",

    `
      The selected company has a FY2025 submitted
      current ratio of
      <b>${fmt(current,2)}x</b>
      and quick ratio of
      <b>${fmt(quick,2)}x</b>.
      Liquidity should be interpreted together with
      the composition of current assets, particularly
      receivables and cash, rather than as a standalone
      strength score.
    `
  );


  setHtml(
    "solvencyText",

    `
      Debt-to-equity is
      <b>${fmt(h.debtEq[4],2)}x</b>
      in the submitted FY2025 series and interest
      coverage is
      <b>${fmt(interest,2)}x</b>.
      Low leverage reduces financing exposure, but
      the coverage ratio can still move with operating
      profit and should not be treated as a guarantee.
    `
  );


  const receivableDays =
    h.receivablesTurn[4] > 0
      ? 365 / h.receivablesTurn[4]
      : null;


  setHtml(
    "efficiencyText",

    `
      FY2025 submitted asset turnover is
      <b>${fmt(h.assetTurn[4],2)}x</b>.
      Receivables turnover is
      <b>${fmt(h.receivablesTurn[4],2)}x</b>,
      equivalent to roughly
      <b>${fmt(receivableDays,0)} days</b>
      of receivables on a simple 365-day approximation.
    `
  );


  setHtml(
    "profitMetrics",

    `

      <div class="metricList">

        <div>Net profit margin</div>
        <div><b>${pct(h.npm[4])}</b></div>

        <div>ROA</div>
        <div><b>${pct(h.roa[4])}</b></div>

        <div>ROE</div>
        <div><b>${pct(h.roe[4])}</b></div>

        <div>EPS (submitted)</div>
        <div><b>${fmt(h.eps[4],2)} PKR</b></div>

        <div>Verified PAT</div>
        <div>
          <b>PKR ${fmt(v.netIncome)}m</b>
        </div>

      </div>

    `
  );


  setHtml(
    "marketMetrics",

    `

      <div class="metricList">

        <div>P/E (submitted)</div>
        <div><b>${fmt(h.pe[4],2)}x</b></div>

        <div>P/E (verified snapshot)</div>
        <div><b>${fmt(v.pe,2)}x</b></div>

        <div>Dividend yield (submitted)</div>
        <div><b>${pct(h.dividendYield[4])}</b></div>

        <div>EPS (submitted)</div>
        <div><b>${fmt(h.eps[4],2)}</b></div>

        <div>
          ${active === "MARI"
            ? "Verified restated EPS"
            : "Verified EPS"}
        </div>

        <div>
          <b>
            ${
              active === "MARI"
                ? fmt(v.epsRestated,2)
                : fmt(v.eps,2)
            }
          </b>
        </div>

        ${
          active === "MARI"
            ? `
              <div>
                Verified consolidated EPS
              </div>

              <div>
                <b>${fmt(v.epsConsolidated,2)}</b>
              </div>
            `
            : ""
        }

      </div>

    `
  );


  setHtml(
    "dupontTable",

    `

      <thead>

        <tr>
          <th>Year</th>
          <th>NPM</th>
          <th>Asset Turnover</th>
          <th>Equity Multiplier</th>
          <th>Calculated ROE</th>
        </tr>

      </thead>

      <tbody>

        ${
          years.map(
            (year,index) => {

              const npm =
                h.npm[index];

              const assetTurn =
                h.assetTurn[index];

              const roe =
                h.roe[index];

              const equityMultiplier =
                npm > 0 && assetTurn > 0
                  ? roe / npm / assetTurn
                  : 0;

              const calculatedRoe =
                npm *
                assetTurn *
                equityMultiplier;

              return `

                <tr>

                  <td>${year}</td>

                  <td>
                    ${pct(npm)}
                  </td>

                  <td>
                    ${fmt(assetTurn,2)}x
                  </td>

                  <td>
                    ${fmt(equityMultiplier,2)}x
                  </td>

                  <td>
                    ${pct(calculatedRoe)}
                  </td>

                </tr>

              `;

            }
          ).join("")
        }

      </tbody>

    `
  );


  const horizontalMetrics = [

    [
      "Revenue",
      h.revenue[0],
      h.revenue[4]
    ],

    [
      "Net income",
      h.netIncome[0],
      h.netIncome[4]
    ],

    [
      "Current ratio",
      h.current[0],
      h.current[4]
    ],

    [
      "ROE",
      h.roe[0],
      h.roe[4]
    ],

    [
      "EPS",
      h.eps[0],
      h.eps[4]
    ]

  ];


  setHtml(
    "horizontalTable",

    `

      <thead>

        <tr>
          <th>Metric</th>
          <th>2021</th>
          <th>2025</th>
          <th>Change</th>
        </tr>

      </thead>

      <tbody>

        ${
          horizontalMetrics.map(
            ([metric,start,end]) => {

              const change =
                start !== 0
                  ? (end / start - 1) * 100
                  : null;

              return `

                <tr>

                  <td>${metric}</td>

                  <td>
                    ${fmt(start,2)}
                  </td>

                  <td>
                    ${fmt(end,2)}
                  </td>

                  <td>
                    ${pct(change)}
                  </td>

                </tr>

              `;

            }
          ).join("")
        }

      </tbody>

    `
  );


  setHtml(
    "verticalIncome",

    `

      <thead>

        <tr>
          <th>Metric</th>
          <th>% of Revenue</th>
        </tr>

      </thead>

      <tbody>

        ${
          [
            [
              "Cost of Revenue",
              company.vertical.costRevenue
            ],

            [
              "Gross Profit",
              company.vertical.grossMargin
            ],

            [
              "Operating Income",
              company.vertical.operatingMargin
            ],

            [
              "Net Income",
              company.vertical.netMargin
            ]

          ].map(
            ([metric,value]) => `

              <tr>

                <td>${metric}</td>

                <td>${pct(value)}</td>

              </tr>

            `
          ).join("")
        }

      </tbody>

    `
  );


  setHtml(
    "verticalBalance",

    `

      <thead>

        <tr>
          <th>Metric</th>
          <th>% of Assets</th>
        </tr>

      </thead>

      <tbody>

        ${
          [
            [
              "Current Assets",
              company.vertical.currentAssets
            ],

            [
              "Net PPE",
              company.vertical.netPpe
            ],

            [
              "Total Liabilities",
              company.vertical.totalLiabilities
            ],

            [
              "Total Equity",
              company.vertical.totalEquity
            ]

          ].map(
            ([metric,value]) => `

              <tr>

                <td>${metric}</td>

                <td>${pct(value)}</td>

              </tr>

            `
          ).join("")
        }

      </tbody>

    `
  );


  const peerOrder =
    ["OGDC","PPL","MARI"];


  setHtml(
    "benchmarkTable",

    `

      <thead>

        <tr>

          <th>Metric</th>

          ${
            peerOrder.map(
              symbol => `<th>${symbol}</th>`
            ).join("")
          }

        </tr>

      </thead>

      <tbody>

        ${

          [

            [
              "Revenue (PKR m)",
              ...peerOrder.map(
                symbol => peer[symbol].revenue
              )
            ],

            [
              "PAT (PKR m)",
              ...peerOrder.map(
                symbol => peer[symbol].netIncome
              )
            ],

            [
              "EPS",
              ...peerOrder.map(
                symbol =>
                  peer[symbol].eps ??
                  peer[symbol].epsRestated
              )
            ],

            [
              "P/E",
              ...peerOrder.map(
                symbol => peer[symbol].pe
              )
            ],

            [
              "Current ratio",
              ...peerOrder.map(
                symbol =>
                  peer[symbol].current ?? null
              )
            ],

            [
              "ROE",
              ...peerOrder.map(
                symbol =>
                  peer[symbol].roe ?? null
              )
            ]

          ].map(
            row => `

              <tr>

                <td>${row[0]}</td>

                ${
                  row.slice(1).map(
                    value => `

                      <td>
                        ${
                          typeof value === "number"
                            ? fmt(value,2)
                            : "—"
                        }
                      </td>

                    `
                  ).join("")
                }

              </tr>

            `
          ).join("")

        }

      </tbody>

    `
  );


  const pestel = [

    [
      "Political / Regulatory",
      "Exploration blocks, permits, fiscal terms, royalties, taxation and policy consistency affect project economics."
    ],

    [
      "Economic",
      "Oil/gas prices, inflation, interest rates, exchange rates and domestic energy demand influence margins and capital spending."
    ],

    [
      "Social",
      "Population, industrial activity and household energy demand support consumption, while energy-transition preferences affect long-term demand."
    ],

    [
      "Technological",
      "Seismic imaging, reservoir analytics, automation and unconventional/offshore technologies can change recovery rates and unit costs."
    ],

    [
      "Environmental",
      "Emissions requirements, climate policy, water management, methane control and environmental approvals affect operating practices and costs."
    ],

    [
      "Legal / Geopolitical",
      "Contract terms, security, joint-venture rules, trade conditions and regional instability can affect exploration and production continuity."
    ]

  ];


  setHtml(
    "pestelGrid",

    pestel.map(
      ([title,text]) => `

        <div class="card">

          <h3>${title}</h3>

          <p class="small">
            ${text}
          </p>

        </div>

      `
    ).join("")
  );


  setHtml(
    "relativeTable",

    `

      <thead>

        <tr>

          <th>Metric</th>
          <th>OGDC</th>
          <th>PPL</th>
          <th>MARI</th>
          <th>Interpretive note</th>

        </tr>

      </thead>

      <tbody>

        <tr>

          <td>P/E</td>

          <td>
            ${fmt(peer.OGDC.pe,2)}
          </td>

          <td>
            ${fmt(peer.PPL.pe,2)}
          </td>

          <td>
            ${fmt(peer.MARI.pe,2)}
          </td>

          <td>
            Compare with growth, risk and earnings quality.
          </td>

        </tr>


        <tr>

          <td>EPS</td>

          <td>
            ${fmt(peer.OGDC.eps,2)}
          </td>

          <td>
            ${fmt(peer.PPL.eps,2)}
          </td>

          <td>
            ${fmt(peer.MARI.epsRestated,2)}
          </td>

          <td>
            MARI uses restated EPS here; consolidated EPS is shown separately.
          </td>

        </tr>


        <tr>

          <td>Dividend yield</td>

          <td>
            ${pct(demo.OGDC.historical.dividendYield[4])}
          </td>

          <td>
            ${pct(demo.PPL.historical.dividendYield[4])}
          </td>

          <td>
            ${pct(peer.MARI.dividendYield)}
          </td>

          <td>
            Yield depends on the price date and dividend basis.
          </td>

        </tr>


        <tr>

          <td>ROE</td>

          <td>
            ${pct(demo.OGDC.historical.roe[4])}
          </td>

          <td>
            ${pct(peer.PPL.roe)}
          </td>

          <td>
            ${pct(peer.MARI.roe)}
          </td>

          <td>
            ROE should be linked to margins, asset turnover and capital structure.
          </td>

        </tr>

      </tbody>

    `
  );


  let integrityHtml = `

    <thead>

      <tr>

        <th>Company</th>
        <th>Metric</th>
        <th>Submitted</th>
        <th>Official / Verified</th>
        <th>Status</th>

      </tr>

    </thead>

    <tbody>

  `;


  if(active === "OGDC"){

    integrityHtml += `

      <tr>

        <td>OGDC</td>

        <td>
          FY2025 Revenue (PKR m)
        </td>

        <td>
          401,178
        </td>

        <td>
          401,178
        </td>

        <td>
          <span class="status ok">
            Verified
          </span>
        </td>

      </tr>


      <tr>

        <td>OGDC</td>

        <td>
          FY2025 PAT (PKR m)
        </td>

        <td>
          169,903
        </td>

        <td>
          169,904
        </td>

        <td>
          <span class="status warn">
            Minor rounding
          </span>
        </td>

      </tr>


      <tr>

        <td>OGDC</td>

        <td>
          EPS
        </td>

        <td>
          39.50
        </td>

        <td>
          39.50
        </td>

        <td>
          <span class="status ok">
            Verified
          </span>
        </td>

      </tr>

    `;

  }


  if(active === "PPL"){

    integrityHtml += `

      <tr>

        <td>PPL</td>

        <td>
          FY2025 Net sales (PKR m)
        </td>

        <td>
          244,977
        </td>

        <td>
          242,516
        </td>

        <td>
          <span class="status warn">
            Reconcile
          </span>
        </td>

      </tr>


      <tr>

        <td>PPL</td>

        <td>
          FY2025 PAT (PKR m)
        </td>

        <td>
          89,949
        </td>

        <td>
          92,027
        </td>

        <td>
          <span class="status warn">
            Reconcile
          </span>
        </td>

      </tr>


      <tr>

        <td>PPL</td>

        <td>
          Current ratio
        </td>

        <td>
          4.78
        </td>

        <td>
          4.81
        </td>

        <td>
          <span class="status warn">
            Reconcile
          </span>
        </td>

      </tr>

    `;

  }


  if(active === "MARI"){

    integrityHtml += `

      <tr>

        <td>MARI</td>

        <td>
          FY2025 Net sales (PKR m)
        </td>

        <td>
          141,486
        </td>

        <td>
          177,097
        </td>

        <td>
          <span class="status warn">
            Major discrepancy
          </span>
        </td>

      </tr>


      <tr>

        <td>MARI</td>

        <td>
          FY2025 PAT (PKR m)
        </td>

        <td>
          65,369
        </td>

        <td>
          65,136
        </td>

        <td>
          <span class="status warn">
            Minor discrepancy
          </span>
        </td>

      </tr>


      <tr>

        <td>MARI</td>

        <td>
          FY2025 EPS
        </td>

        <td>
          54.45
        </td>

        <td>
          54.25 restated / 54.45 consolidated
        </td>

        <td>
          <span class="status info">
            Basis matters
          </span>
        </td>

      </tr>

    `;

  }


  integrityHtml += `

    </tbody>

  `;


  setHtml(
    "integrityTable",
    integrityHtml
  );


  setHtml(
    "referencesGrid",

    company.sources.map(
      ([label,url]) => `

        <div class="card sourceBox">

          <h3>
            ${label}
          </h3>

          <a
            href="${url}"
            target="_blank"
            rel="noopener noreferrer"
          >
            ${url}
          </a>

        </div>

      `
    ).join("")
  );


  document.getElementById(
    "jsonInput"
  ).value =
    JSON.stringify(

      {

        symbol:company.short,

        name:company.name,

        years:years,

        revenue:h.revenue,

        netIncome:h.netIncome,

        npm:h.npm,

        roa:h.roa,

        roe:h.roe,

        current:h.current,

        quick:h.quick,

        debtEq:h.debtEq,

        interest:h.interest,

        assetTurn:h.assetTurn,

        inventoryTurn:h.inventoryTurn,

        receivablesTurn:h.receivablesTurn,

        pe:h.pe,

        eps:h.eps,

        dividendYield:h.dividendYield,

        source:
          "Submitted demo dataset; attach audited-source metadata in production."

      },

      null,

      2

    );


  renderScenarios();

  runDCF();

}



function renderScenarios(){

  const company =
    demo[active];

  if(!company){
    return;
  }

  const h =
    company.historical;


  const growth =
    Number(
      document.getElementById("scBase").value || 6
    );


  const margin =
    Number(
      document.getElementById("scMargin").value || 35
    );


  const shock =
    Number(
      document.getElementById("scShock").value || 10
    );


  const baseRevenue =
    h.revenue[4] *
    (1 + growth / 100);


  const cases = [

    [
      "Bear",
      growth - shock,
      Math.max(
        1,
        margin - shock / 2
      ),
      "Lower production / commodity pressure / slower collections"
    ],

    [
      "Base",
      growth,
      margin,
      "Historical growth with stable operating conditions"
    ],

    [
      "Bull",
      growth + shock,
      margin + shock / 2,
      "Higher production / favorable prices / stronger execution"
    ]

  ];


  setHtml(
    "scenarioCards",

    cases.map(
      ([name,caseGrowth,caseMargin,note]) => {

        const revenue =
          h.revenue[4] *
          (1 + caseGrowth / 100);


        const profit =
          revenue *
          caseMargin /
          100;


        const eps =
          h.netIncome[4] !== 0
            ? (
                profit /
                h.netIncome[4]
              ) *
              h.eps[4]
            : 0;


        return `

          <div class="scenario">

            <h3>
              ${name} Case
            </h3>

            <div class="big">
              Revenue PKR ${fmt(revenue)}m
            </div>

            <div style="margin-top:5px">
              Net profit ≈
              PKR ${fmt(profit)}m
            </div>

            <div>
              EPS ≈
              PKR ${fmt(eps,2)}
            </div>

            <p class="small">
              ${note}
            </p>

            <span class="status info">
              Model-generated scenario
            </span>

          </div>

        `;

      }
    ).join("")
  );

}



function runDCF(){

  const company =
    demo[active];

  if(!company){
    return;
  }

  const h =
    company.historical;


  const growth =
    Number(
      document.getElementById("dcfGrowth").value
    ) / 100;


  const margin =
    Number(
      document.getElementById("dcfMargin").value
    ) / 100;


  const wacc =
    Number(
      document.getElementById("dcfWacc").value
    ) / 100;


  const terminalGrowth =
    Number(
      document.getElementById("dcfTg").value
    ) / 100;


  const capex =
    Number(
      document.getElementById("dcfCapex").value
    ) / 100;


  const workingCapital =
    Number(
      document.getElementById("dcfWc").value
    ) / 100;


  const netDebt =
    Number(
      document.getElementById("dcfNetDebt").value || 0
    );


  const shares =
    Number(
      document.getElementById("dcfShares").value || 1
    );


  if(
    !Number.isFinite(growth) ||
    !Number.isFinite(margin) ||
    !Number.isFinite(wacc) ||
    !Number.isFinite(terminalGrowth) ||
    !Number.isFinite(capex) ||
    !Number.isFinite(workingCapital)
  ){

    setHtml(
      "dcfOutput",
      `
        <div class="status warn">
          Please enter valid numerical DCF assumptions.
        </div>
      `
    );

    return;
  }


  if(wacc <= terminalGrowth){

    setHtml(
      "dcfOutput",

      `
        <div class="status warn">
          WACC must be greater than terminal growth.
        </div>
      `
    );

    return;
  }


  if(shares <= 0){

    setHtml(
      "dcfOutput",

      `
        <div class="status warn">
          Diluted shares must be greater than zero.
        </div>
      `
    );

    return;
  }


  let revenue =
    h.revenue[4];

  let presentValue =
    0;

  const rows = [];


  for(
    let period = 1;
    period <= 5;
    period++
  ){

    revenue *=
      1 + growth;


    const operatingProfit =
      revenue *
      margin;


    const fcf =
      operatingProfit -
      revenue * capex -
      revenue * workingCapital;


    const discounted =
      fcf /
      Math.pow(
        1 + wacc,
        period
      );


    presentValue +=
      discounted;


    rows.push(
      [
        period,
        revenue,
        fcf,
        discounted
      ]
    );

  }


  const terminalFcf =
    rows[rows.length - 1][2];


  const terminalValue =
    terminalFcf *
    (1 + terminalGrowth) /
    (wacc - terminalGrowth);


  const presentValueTerminal =
    terminalValue /
    Math.pow(
      1 + wacc,
      5
    );


  const enterpriseValue =
    presentValue +
    presentValueTerminal;


  const equityValue =
    enterpriseValue -
    netDebt;


  const valuePerShare =
    equityValue /
    shares;


  setHtml(

    "dcfOutput",

    `

      <div class="metricList">

        <div>
          PV of explicit FCF
        </div>

        <div>
          <b>
            PKR ${fmt(presentValue)}m
          </b>
        </div>


        <div>
          Terminal value
        </div>

        <div>
          <b>
            PKR ${fmt(terminalValue)}m
          </b>
        </div>


        <div>
          PV of terminal value
        </div>

        <div>
          <b>
            PKR ${fmt(presentValueTerminal)}m
          </b>
        </div>


        <div>
          Enterprise value
        </div>

        <div>
          <b>
            PKR ${fmt(enterpriseValue)}m
          </b>
        </div>


        <div>
          Equity value
        </div>

        <div>
          <b>
            PKR ${fmt(equityValue)}m
          </b>
        </div>


        <div>
          Model value / share
        </div>

        <div>
          <b>
            PKR ${fmt(valuePerShare,2)}
          </b>
        </div>

      </div>


      <p
        class="small muted"
        style="margin-top:10px"
      >
        Illustrative only. A real DCF should use cash-flow statement
        inputs, tax effects, depreciation, working capital, capex plans
        and a defensible WACC.
      </p>

    `

  );

}



function importJson(){

  try{

    const input =
      document.getElementById(
        "jsonInput"
      ).value;


    const data =
      JSON.parse(input);


    if(
      !data.symbol ||
      !Array.isArray(data.years) ||
      data.years.length !== 5
    ){

      throw new Error(
        "symbol and exactly five years are required"
      );

    }


    const requiredArrays = [

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
      "dividendYield"

    ];


    requiredArrays.forEach(
      field => {

        if(
          !Array.isArray(data[field]) ||
          data[field].length !== 5
        ){

          throw new Error(
            `${field} must contain exactly five values`
          );

        }

      }
    );


    const historical = {

      revenue:data.revenue,

      netIncome:data.netIncome,

      npm:data.npm,

      roa:data.roa,

      roe:data.roe,

      current:data.current,

      quick:data.quick,

      debtEq:data.debtEq,

      interest:data.interest,

      assetTurn:data.assetTurn,

      inventoryTurn:data.inventoryTurn,

      receivablesTurn:data.receivablesTurn,

      pe:data.pe,

      eps:data.eps,

      dividendYield:data.dividendYield

    };


    demo[data.symbol] = {

      name:
        data.name || data.symbol,

      short:
        data.symbol,

      description:
        "Imported five-year dataset.",

      historical:historical,

      verified2025:{

        revenue:data.revenue[4],

        netIncome:data.netIncome[4],

        eps:data.eps[4],

        pe:data.pe[4],

        current:data.current[4],

        roe:data.roe[4],

        sourceLabel:
          data.source ||
          "Imported dataset"

      },

      vertical:{

        costRevenue:
          100 - data.npm[4],

        grossMargin:
          100 - data.npm[4],

        operatingMargin:
          null,

        netMargin:
          data.npm[4],

        currentAssets:
          null,

        netPpe:
          null,

        totalLiabilities:
          null,

        totalEquity:
          null

      },

      sources:[

        [
          data.source ||
            "Imported source",
          "#"
        ]

      ]

    };


    active =
      data.symbol;


    populateSelector();


    document.getElementById(
      "companySelect"
    ).value =
      active;


    document.getElementById(
      "symbolInput"
    ).value =
      active;


    render();


    alert(
      "Imported successfully."
    );

  }

  catch(error){

    alert(
      "Import error: " +
      error.message
    );

  }

}



function populateSelector(){

  const selector =
    document.getElementById(
      "companySelect"
    );


  selector.innerHTML =

    Object.keys(demo)

      .map(
        symbol => `

          <option value="${symbol}">
            ${symbol} — ${demo[symbol].name}
          </option>

        `
      )

      .join("");

}



document
  .getElementById("companySelect")
  .addEventListener(
    "change",
    event => {

      active =
        event.target.value;


      document.getElementById(
        "symbolInput"
      ).value =
        active;


      render();

    }
  );



document
  .getElementById("loadSymbol")
  .addEventListener(
    "click",
    () => {

      const symbol =
        document
          .getElementById("symbolInput")
          .value
          .trim()
          .toUpperCase();


      if(demo[symbol]){

        active =
          symbol;


        document.getElementById(
          "companySelect"
        ).value =
          symbol;


        render();

      }

      else{

        alert(
          "This standalone demo does not scrape PSX. " +
          "Use Import Data or connect /api/company/:symbol " +
          "on your own authorized backend."
        );

      }

    }
  );



[
  "scBase",
  "scMargin",
  "scShock"
]
.forEach(
  id => {

    document
      .getElementById(id)
      .addEventListener(
        "input",
        renderScenarios
      );

  }
);



document
  .getElementById("runDcf")
  .addEventListener(
    "click",
    runDCF
  );



document
  .getElementById("importJson")
  .addEventListener(
    "click",
    importJson
  );



document
  .getElementById("printBtn")
  .addEventListener(
    "click",
    () => window.print()
  );



populateSelector();


document.getElementById(
  "companySelect"
).value =
  active;


document.getElementById(
  "symbolInput"
).value =
  active;


render();

</script>

</body>
</html>
''')

# ============================================================
# OUTPUT FILE
# ============================================================

output_path = Path(__file__).parent / "psx_financial_analysis_dashboard.html"

output_path.write_text(
    html,
    encoding="utf-8"
)

print(f"Dashboard created: {output_path}")

# ============================================================
# README
# ============================================================

readme = dedent('''\
# PSX Five-Year Financial Analysis Dashboard

## What this demo contains

- FY2021-FY2025 historical charts
- OGDC, PPL and MARI demo datasets
- Liquidity analysis
- Profitability analysis
- Solvency and coverage analysis
- Efficiency analysis
- Market-ratio analysis
- DuPont analysis
- Horizontal analysis
- Vertical/common-size analysis
- Cross-company comparison
- Industry and PESTEL analysis
- Risk dashboard
- Base/Bull/Bear scenario engine
- Interactive DCF assumptions
- Relative valuation
- Data-integrity reconciliation
- JSON import for any five-year company dataset
- Official-source links
- Print / PDF support
- Responsive desktop/tablet/mobile layout

## Important architecture note

The standalone HTML deliberately does NOT scrape PSX market data
directly from browser JavaScript.

For a production/generalized version, use:

Frontend
    ->
/api/company/:symbol
    ->
Authorized/licensed data adapter
    ->
Normalized financial dataset
    ->
Ratio engine
    ->
Charts / benchmarking / scenarios / DCF

Keep all data-provider credentials on the server.

## Recommended source metadata

Every financial value should retain:

- source URL or document
- reporting period
- consolidated vs unconsolidated status
- currency
- unit
- as-reported vs standardized basis
- retrieval date
- verification status

## Suggested normalized API response

```json
{
  "symbol": "OGDC",
  "companyName": "Oil & Gas Development Company Limited",
  "currency": "PKR",
  "unit": "million",
  "years": [2021, 2022, 2023, 2024, 2025],

  "income": {
    "revenue": [
      239774,
      279816,
      324282,
      378423,
      401178
    ],

    "netIncome": [
      91534,
      133430,
      224617,
      208976,
      169903
    ]
  },

  "balance": {
    "currentAssets": [],
    "currentLiabilities": [],
    "totalAssets": [],
    "totalLiabilities": [],
    "equity": []
  },

  "cashFlow": {
    "operatingCashFlow": [],
    "capex": []
  },

  "market": {
    "eps": [],
    "pe": [],
    "price": [],
    "shares": []
  },

  "sources": [
    {
      "type": "annual_report",
      "period": 2025,
      "url": "https://...",
      "status": "verified"
    }
  ]
} ''')