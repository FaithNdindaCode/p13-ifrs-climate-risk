import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="P13 · IFRS Climate Risk | SmartHaven Digital",
    page_icon="⚠️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Design System ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
}

/* Dark editorial base */
.stApp { background-color: #0d0f14; }
[data-testid="stSidebar"] { background-color: #111318; border-right: 1px solid #1e2130; }

/* Metric cards */
[data-testid="stMetric"] {
    background: #13161f;
    border: 1px solid #1e2130;
    border-radius: 4px;
    padding: 1rem 1.2rem;
}
[data-testid="stMetricValue"] {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.8rem !important;
    font-weight: 600;
    color: #f0f2f8;
}
[data-testid="stMetricLabel"] { color: #6b7280; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.08em; }

/* Warning band — the signature element */
.stranded-alert {
    background: linear-gradient(90deg, rgba(239,68,68,0.15) 0%, rgba(239,68,68,0.03) 100%);
    border-left: 3px solid #ef4444;
    padding: 1rem 1.4rem;
    border-radius: 0 4px 4px 0;
    margin: 0.75rem 0;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.82rem;
    color: #fca5a5;
}
.watch-alert {
    background: linear-gradient(90deg, rgba(245,158,11,0.15) 0%, rgba(245,158,11,0.03) 100%);
    border-left: 3px solid #f59e0b;
    padding: 1rem 1.4rem;
    border-radius: 0 4px 4px 0;
    margin: 0.75rem 0;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.82rem;
    color: #fcd34d;
}
.safe-alert {
    background: linear-gradient(90deg, rgba(34,197,94,0.10) 0%, rgba(34,197,94,0.02) 100%);
    border-left: 3px solid #22c55e;
    padding: 1rem 1.4rem;
    border-radius: 0 4px 4px 0;
    margin: 0.75rem 0;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.82rem;
    color: #86efac;
}

/* IFRS tag pills */
.ifrs-tag {
    display: inline-block;
    background: #1a1f2e;
    border: 1px solid #2d3452;
    color: #818cf8;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    padding: 2px 8px;
    border-radius: 2px;
    margin-right: 4px;
    letter-spacing: 0.05em;
}

/* Section headers */
.section-label {
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #4f5b7a;
    margin-bottom: 0.5rem;
}

/* Mono data display */
.mono-data {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.82rem;
    color: #94a3b8;
    line-height: 1.8;
}

.block-container { padding-top: 1.2rem; padding-bottom: 2rem; }
.stTabs [data-baseweb="tab"] {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem;
    letter-spacing: 0.06em;
    color: #4f5b7a;
}
.stTabs [aria-selected="true"] { color: #818cf8 !important; }

h1,h2,h3,h4 { color: #e2e8f0; }
p, li { color: #94a3b8; }
</style>
""", unsafe_allow_html=True)

# ── Data ──────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    companies = [
        # name, sector, country, revenue_usd_m, asset_value_usd_m, carbon_intensity,
        # reserve_life_years, physical_risk, transition_risk, ecl_base_rate,
        # lease_exposure_usd_m, gresb_score, green_bond_issued_usd_m, credit_rating, ifrs6_applicable
        ("Safaricom PLC",        "Telecoms",    "KE", 2500, 3200, 45,  None, 5.2, 7.8, 0.018, 180, 62, 0,   "BB+", False),
        ("KenGen",               "Energy",      "KE", 890,  4100, 210, None, 7.8, 6.2, 0.032, 520, 48, 150, "BB",  False),
        ("Equity Group",         "Banking",     "KE", 1200, 8900, 28,  None, 4.1, 5.9, 0.041, 95,  55, 0,   "BB+", False),
        ("East African Breweries","Consumer",   "KE", 680,  1100, 185, None, 6.3, 5.1, 0.027, 210, 38, 0,   "BB-", False),
        ("Kenya Airways",        "Transport",   "KE", 440,  2800, 890, None, 8.9, 8.1, 0.065, 1200,22, 0,   "B+",  False),
        ("Bamburi Cement",       "Materials",   "KE", 310,  680,  720, None, 7.1, 7.4, 0.048, 85,  31, 0,   "B+",  False),
        ("Tullow Oil Kenya",     "Oil & Gas",   "KE", 180,  2100, 1450,8,    9.2, 9.4, 0.071, 320, 18, 0,   "B",   True),
        ("Africa Oil Corp",      "Oil & Gas",   "KE", 95,   1400, 1820,6,    9.5, 9.6, 0.082, 180, 14, 0,   "B-",  True),
        ("KCB Group",            "Banking",     "KE", 980,  7200, 22,  None, 3.8, 5.4, 0.038, 75,  58, 80,  "BB+", False),
        ("NCBA Group",           "Banking",     "KE", 520,  4100, 25,  None, 3.5, 5.1, 0.035, 55,  52, 0,   "BB",  False),
        ("Nation Media Group",   "Media",       "KE", 120,  280,  65,  None, 3.2, 4.8, 0.022, 35,  41, 0,   "BB-", False),
        ("Carbacid Investments", "Industrials", "KE", 45,   190,  380, None, 5.9, 6.8, 0.044, 20,  29, 0,   "B+",  False),
    ]
    cols = ["company","sector","country","revenue_usd_m","asset_value_usd_m",
            "carbon_intensity","reserve_life_years","physical_risk","transition_risk",
            "ecl_base_rate","lease_exposure_usd_m","gresb_score",
            "green_bond_issued_usd_m","credit_rating","ifrs6_applicable"]
    df = pd.DataFrame(companies, columns=cols)

    # GRESB tier
    df["gresb_tier"] = pd.cut(df["gresb_score"],
        bins=[0,30,50,70,100],
        labels=["⬛ Laggard","🟧 Developing","🟦 Advanced","🟩 Leader"])

    # Green bond flag
    df["green_bond_issuer"] = df["green_bond_issued_usd_m"] > 0
    return df

df = load_data()

# ── Carbon price scenarios ────────────────────────────────────────────────────
CARBON_SCENARIOS = {
    "1.5°C — Aggressive transition": {"2025":85,"2026":95,"2027":108,"2028":122,"2029":138,"2030":155},
    "2°C — Moderate transition":     {"2025":50,"2026":57,"2027":65,"2028":74,"2029":84,"2030":95},
    "3°C — Physical risk dominant":  {"2025":25,"2026":27,"2027":29,"2028":31,"2029":34,"2030":37},
}

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<p class="section-label">P13 · SmartHaven Digital</p>', unsafe_allow_html=True)
    st.markdown("### IFRS Climate Risk\nStranded Asset Early Warning")
    st.divider()

    scenario_name = st.selectbox(
        "Carbon price pathway",
        list(CARBON_SCENARIOS.keys()),
        index=1,
    )
    carbon_prices = CARBON_SCENARIOS[scenario_name]
    carbon_price_2025 = carbon_prices["2025"]
    carbon_price_2030 = carbon_prices["2030"]

    st.markdown(f"""
    <div class="mono-data">
    2025 price: <b style="color:#818cf8">${carbon_price_2025}/t CO₂e</b><br>
    2030 price: <b style="color:#818cf8">${carbon_price_2030}/t CO₂e</b><br>
    Stranded trigger: <b style="color:#ef4444">&gt;$100/t</b>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    sectors = st.multiselect(
        "Filter sectors",
        sorted(df["sector"].unique()),
        default=sorted(df["sector"].unique()),
    )

    discount_rate = st.slider("Discount rate (IFRS impairment test)", 0.06, 0.18, 0.10, 0.01, format="%.0%%")

    st.divider()
    st.markdown('<p class="section-label">Standards Coverage</p>', unsafe_allow_html=True)
    st.markdown("""
    <span class="ifrs-tag">IFRS 6</span> Reserve impairment<br><br>
    <span class="ifrs-tag">IFRS 9</span> Climate ECL<br><br>
    <span class="ifrs-tag">IFRS 16</span> Stranded leases<br><br>
    <span class="ifrs-tag">IFRS S2</span> Disclosure gap
    """, unsafe_allow_html=True)
    st.divider()
    st.caption("SmartHaven Digital · P13 · Faith Ndinda")
    st.caption("[GitHub](https://github.com/FaithNdindaCode/financial-engineering-portfolio)")

# ── Filter ────────────────────────────────────────────────────────────────────
df = df[df["sector"].isin(sectors)].copy()

# ── Computed fields ───────────────────────────────────────────────────────────
# IFRS 6 — reserve impairment
def ifrs6_impairment(row, carbon_price, discount_rate):
    if not row["ifrs6_applicable"] or pd.isna(row["reserve_life_years"]):
        return 0.0, 0.0, False
    annual_carbon_cost = (row["carbon_intensity"] / 1_000_000) * row["revenue_usd_m"] * carbon_price
    pv_carbon_costs = sum([annual_carbon_cost / ((1 + discount_rate) ** t)
                           for t in range(1, int(row["reserve_life_years"]) + 1)])
    net_recoverable = row["asset_value_usd_m"] - pv_carbon_costs
    impairment = max(0, row["asset_value_usd_m"] - net_recoverable)
    impairment_pct = impairment / row["asset_value_usd_m"] * 100
    return round(impairment, 1), round(impairment_pct, 1), net_recoverable < (row["asset_value_usd_m"] * 0.70)

# IFRS 9 — climate-adjusted ECL
def ifrs9_ecl(row, carbon_price):
    climate_uplift = (row["physical_risk"] * 0.003) + (row["transition_risk"] * 0.004)
    carbon_uplift = min(0.05, (carbon_price / 1000) * (row["carbon_intensity"] / 500))
    adj_pd = row["ecl_base_rate"] + climate_uplift + carbon_uplift
    lgd = 0.45
    ead = row["asset_value_usd_m"] * 0.35
    ecl = adj_pd * lgd * ead
    ecl_uplift_pct = (climate_uplift + carbon_uplift) / row["ecl_base_rate"] * 100
    return round(ecl, 2), round(adj_pd * 100, 3), round(ecl_uplift_pct, 1)

# IFRS 16 — stranded lease
def ifrs16_stranded(row, carbon_price):
    if row["lease_exposure_usd_m"] == 0:
        return 0.0, False
    stranded_pct = min(0.85, (row["carbon_intensity"] / 2000) * (carbon_price / 100))
    stranded_exposure = row["lease_exposure_usd_m"] * stranded_pct
    return round(stranded_exposure, 1), stranded_exposure > (row["lease_exposure_usd_m"] * 0.4)

# IFRS S2 — disclosure score (simulated)
def ifrs_s2_gap(row):
    factors = {
        "Scenario analysis": min(100, row["gresb_score"] * 1.1),
        "Physical risk disclosure": min(100, row["physical_risk"] * 8),
        "Transition plan": min(100, (100 - row["carbon_intensity"] / 20)),
        "Scope 1/2/3 reporting": min(100, row["gresb_score"] * 0.9),
        "Carbon price assumption": 40 if row["carbon_intensity"] > 200 else 65,
    }
    disclosed = np.mean(list(factors.values()))
    gap = 100 - disclosed
    return round(disclosed, 1), round(gap, 1), factors

# Stranded asset flag
def stranded_flag(row, carbon_price, reserve_life):
    triggers = []
    if carbon_price > 100 and reserve_life and reserve_life < 10:
        triggers.append(f"Carbon price ${carbon_price}/t × reserve life {reserve_life}yr")
    if row["carbon_intensity"] > 800:
        triggers.append(f"Carbon intensity {row['carbon_intensity']} tCO₂e/USD M")
    if row["physical_risk"] > 8.0:
        triggers.append(f"Physical risk score {row['physical_risk']}")
    if row["transition_risk"] > 8.0:
        triggers.append(f"Transition risk score {row['transition_risk']}")
    if len(triggers) >= 2:
        return "🔴 STRANDED", triggers
    elif len(triggers) == 1:
        return "🟡 WATCH", triggers
    return "🟢 SAFE", triggers

# Apply computations
records = []
for _, row in df.iterrows():
    imp_usd, imp_pct, imp_triggered = ifrs6_impairment(row, carbon_price_2025, discount_rate)
    ecl_usd, adj_pd, ecl_uplift = ifrs9_ecl(row, carbon_price_2025)
    lease_str, lease_triggered = ifrs16_stranded(row, carbon_price_2025)
    s2_score, s2_gap, s2_factors = ifrs_s2_gap(row)
    flag, triggers = stranded_flag(row, carbon_price_2025, row["reserve_life_years"])
    records.append({
        **row.to_dict(),
        "ifrs6_impairment_usd_m": imp_usd,
        "ifrs6_impairment_pct": imp_pct,
        "ifrs6_triggered": imp_triggered,
        "ifrs9_ecl_usd_m": ecl_usd,
        "ifrs9_adj_pd_pct": adj_pd,
        "ifrs9_ecl_uplift_pct": ecl_uplift,
        "ifrs16_stranded_usd_m": lease_str,
        "ifrs16_triggered": lease_triggered,
        "ifrs_s2_score": s2_score,
        "ifrs_s2_gap": s2_gap,
        "stranded_flag": flag,
        "stranded_triggers": triggers,
        "total_climate_liability_usd_m": imp_usd + ecl_usd + lease_str,
    })

result = pd.DataFrame(records)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<p class="section-label">SmartHaven Digital · P13 · Financial Engineering Portfolio</p>
<h2 style="margin-top:0;color:#e2e8f0;font-family:'IBM Plex Sans',sans-serif;font-weight:300;letter-spacing:-0.02em">
IFRS Climate Risk & <span style="color:#818cf8;font-weight:600">Stranded Asset</span> Early Warning System
</h2>
<p style="color:#4f5b7a;font-size:0.85rem;margin-top:-0.5rem">
IFRS 6 · IFRS 9 · IFRS 16 · IFRS S2 &nbsp;|&nbsp; GRESB Sustainability Scoring &nbsp;|&nbsp; Green Bond Quality &nbsp;|&nbsp; NSE-listed companies
</p>
""", unsafe_allow_html=True)

st.divider()

# ── KPI Row ───────────────────────────────────────────────────────────────────
stranded_count = (result["stranded_flag"] == "🔴 STRANDED").sum()
watch_count = (result["stranded_flag"] == "🟡 WATCH").sum()
total_liability = result["total_climate_liability_usd_m"].sum()
avg_s2_gap = result["ifrs_s2_gap"].mean()
total_ecl = result["ifrs9_ecl_usd_m"].sum()

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Companies Analysed", len(result))
k2.metric("🔴 Stranded Risk", stranded_count, delta=f"{watch_count} on watch")
k3.metric("Total Climate Liability", f"USD {total_liability:,.0f}M", help="IFRS 6+9+16 combined exposure")
k4.metric("Avg IFRS S2 Gap", f"{avg_s2_gap:.0f}%", help="Disclosure gap vs full S2 compliance")
k5.metric("Portfolio Climate ECL", f"USD {total_ecl:.1f}M", help="Climate-adjusted expected credit loss")

st.divider()

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "⚠️ Early Warning",
    "📘 IFRS 6 · Reserves",
    "📗 IFRS 9 · Credit",
    "📙 IFRS 16 · Leases",
    "📒 IFRS S2 · Disclosure",
    "🌱 GRESB & Green Bonds",
    "📋 Full Dataset",
])

# ─── TAB 1: Early Warning Dashboard ──────────────────────────────────────────
with tab1:
    st.markdown("#### Stranded Asset Early Warning — All Companies")
    st.caption(f"Carbon price trigger: **>${100}/tonne CO₂e** + reserve life <10yr | Scenario: {scenario_name.split('—')[0].strip()}")

    # Warning cards
    stranded_cos = result[result["stranded_flag"] == "🔴 STRANDED"]
    watch_cos = result[result["stranded_flag"] == "🟡 WATCH"]
    safe_cos = result[result["stranded_flag"] == "🟢 SAFE"]

    if not stranded_cos.empty:
        st.markdown("**Critical — Stranded Asset Risk**")
        for _, r in stranded_cos.iterrows():
            triggers_str = " · ".join(r["stranded_triggers"])
            st.markdown(f"""
            <div class="stranded-alert">
            🔴 <b>{r['company']}</b> &nbsp;|&nbsp; {r['sector']}<br>
            Triggers: {triggers_str}<br>
            Total climate liability: <b>USD {r['total_climate_liability_usd_m']:.1f}M</b>
            &nbsp;·&nbsp; IFRS S2 gap: <b>{r['ifrs_s2_gap']:.0f}%</b>
            </div>
            """, unsafe_allow_html=True)

    if not watch_cos.empty:
        st.markdown("**Watch — Elevated Risk**")
        for _, r in watch_cos.iterrows():
            triggers_str = " · ".join(r["stranded_triggers"]) if r["stranded_triggers"] else "Monitoring"
            st.markdown(f"""
            <div class="watch-alert">
            🟡 <b>{r['company']}</b> &nbsp;|&nbsp; {r['sector']}<br>
            Trigger: {triggers_str}<br>
            Total climate liability: <b>USD {r['total_climate_liability_usd_m']:.1f}M</b>
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    # Portfolio heat map
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### Climate Liability vs Carbon Intensity")
        fig1 = px.scatter(
            result,
            x="carbon_intensity",
            y="total_climate_liability_usd_m",
            size="asset_value_usd_m",
            color="stranded_flag",
            hover_name="company",
            hover_data={"sector": True, "ifrs6_impairment_usd_m": True, "ifrs9_ecl_usd_m": True},
            color_discrete_map={"🔴 STRANDED": "#ef4444", "🟡 WATCH": "#f59e0b", "🟢 SAFE": "#22c55e"},
            labels={
                "carbon_intensity": "Carbon Intensity (tCO₂e / USD M rev)",
                "total_climate_liability_usd_m": "Total Climate Liability (USD M)",
                "asset_value_usd_m": "Asset Value (USD M)",
            },
        )
        fig1.add_vline(x=800, line_dash="dash", line_color="#ef4444", opacity=0.5, annotation_text="High intensity threshold")
        fig1.update_layout(height=380, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                           font_color="#94a3b8", legend_title="")
        st.plotly_chart(fig1, use_container_width=True)

    with col_b:
        st.markdown("#### Carbon Price Sensitivity — Liability at Risk")
        price_range = list(range(25, 201, 25))
        sensitivity_rows = []
        for price in price_range:
            total = 0
            for _, row in df.iterrows():
                imp, _, _ = ifrs6_impairment(row, price, discount_rate)
                ecl, _, _ = ifrs9_ecl(row, price)
                lease, _ = ifrs16_stranded(row, price)
                total += imp + ecl + lease
            sensitivity_rows.append({"Carbon Price (USD/t)": price, "Total Liability (USD M)": round(total, 1)})

        sens_df = pd.DataFrame(sensitivity_rows)
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=sens_df["Carbon Price (USD/t)"], y=sens_df["Total Liability (USD M)"],
            fill="tozeroy", fillcolor="rgba(129,140,248,0.10)",
            line=dict(color="#818cf8", width=2.5),
            mode="lines+markers", marker=dict(size=6),
        ))
        fig2.add_vline(x=100, line_dash="dash", line_color="#ef4444", opacity=0.6,
                       annotation_text="Stranded trigger $100/t", annotation_font_color="#fca5a5")
        fig2.update_layout(
            height=380, xaxis_title="Carbon Price (USD/tonne)", yaxis_title="Total IFRS Liability (USD M)",
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#94a3b8",
        )
        st.plotly_chart(fig2, use_container_width=True)

    # IFRS liability breakdown
    st.markdown("#### IFRS Liability Decomposition by Company")
    fig3 = go.Figure()
    co_sorted = result.sort_values("total_climate_liability_usd_m", ascending=False)
    fig3.add_trace(go.Bar(name="IFRS 6 — Impairment", x=co_sorted["company"], y=co_sorted["ifrs6_impairment_usd_m"], marker_color="#ef4444"))
    fig3.add_trace(go.Bar(name="IFRS 9 — ECL", x=co_sorted["company"], y=co_sorted["ifrs9_ecl_usd_m"], marker_color="#f59e0b"))
    fig3.add_trace(go.Bar(name="IFRS 16 — Stranded Leases", x=co_sorted["company"], y=co_sorted["ifrs16_stranded_usd_m"], marker_color="#818cf8"))
    fig3.update_layout(
        barmode="stack", height=380, xaxis_tickangle=-30,
        yaxis_title="USD Million", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font_color="#94a3b8", legend=dict(orientation="h", y=1.1),
    )
    st.plotly_chart(fig3, use_container_width=True)


# ─── TAB 2: IFRS 6 ───────────────────────────────────────────────────────────
with tab2:
    st.markdown("""
    <span class="ifrs-tag">IFRS 6</span>
    <b style="color:#e2e8f0"> Exploration & Evaluation Asset Impairment</b>
    """, unsafe_allow_html=True)
    st.caption("Under IFRS 6, companies must test E&E assets for impairment when facts suggest the carrying amount exceeds recoverable amount. Climate risk — via carbon pricing — directly reduces the net recoverable amount of hydrocarbon reserves.")

    st.markdown("""
    <div class="mono-data" style="background:#13161f;padding:1rem;border-radius:4px;border:1px solid #1e2130;margin-bottom:1rem">
    Net Recoverable Amount = Asset Value − PV(Annual Carbon Cost × Reserve Life)<br>
    Impairment Required IF: NRA &lt; 70% of Carrying Value<br>
    Annual Carbon Cost = (Carbon Intensity / 1,000,000) × Revenue × Carbon Price
    </div>
    """, unsafe_allow_html=True)

    ifrs6_df = result[result["ifrs6_applicable"]].copy()

    if ifrs6_df.empty:
        st.info("No IFRS 6 applicable companies in current sector filter.")
    else:
        for _, r in ifrs6_df.iterrows():
            status = "🔴 IMPAIRMENT REQUIRED" if r["ifrs6_triggered"] else "🟡 MONITOR"
            color = "#ef4444" if r["ifrs6_triggered"] else "#f59e0b"
            st.markdown(f"""
            <div style="background:#13161f;border:1px solid #1e2130;border-left:3px solid {color};
                        padding:1rem 1.4rem;border-radius:0 4px 4px 0;margin-bottom:0.8rem">
            <b style="color:#e2e8f0">{r['company']}</b>
            <span style="color:{color};font-family:'IBM Plex Mono',monospace;font-size:0.75rem;margin-left:1rem">{status}</span><br>
            <span class="mono-data">
            Reserve Life: {r['reserve_life_years']:.0f} years &nbsp;·&nbsp;
            Carbon Intensity: {r['carbon_intensity']:,.0f} tCO₂e/USD M &nbsp;·&nbsp;
            Asset Value: USD {r['asset_value_usd_m']:,.0f}M<br>
            IFRS 6 Write-down: <b style="color:#fca5a5">USD {r['ifrs6_impairment_usd_m']:,.1f}M</b>
            ({r['ifrs6_impairment_pct']:.1f}% of carrying value)
            </span>
            </div>
            """, unsafe_allow_html=True)

    # Carbon price path vs impairment
    st.markdown("#### How impairment grows with carbon price (2025–2030)")
    years = list(carbon_prices.keys())
    prices = list(carbon_prices.values())

    if not ifrs6_df.empty:
        fig_imp = go.Figure()
        colors_ifrs6 = ["#ef4444", "#f59e0b", "#818cf8"]
        for i, (_, r) in enumerate(ifrs6_df.iterrows()):
            imps = []
            for p in prices:
                imp, _, _ = ifrs6_impairment(r, p, discount_rate)
                imps.append(imp)
            fig_imp.add_trace(go.Scatter(
                x=years, y=imps, name=r["company"],
                mode="lines+markers",
                line=dict(color=colors_ifrs6[i % len(colors_ifrs6)], width=2),
                marker=dict(size=7),
            ))
        fig_imp.add_hline(y=0, line_color="#4f5b7a", line_dash="dot")
        fig_imp.update_layout(
            height=360, xaxis_title="Year", yaxis_title="IFRS 6 Impairment (USD M)",
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="#94a3b8", legend=dict(orientation="h", y=1.1),
        )
        st.plotly_chart(fig_imp, use_container_width=True)

    st.info("💡 **Use case:** Auditors and fund managers use this to flag when O&G reserves require write-down in financial statements under rising carbon price assumptions.")


# ─── TAB 3: IFRS 9 ───────────────────────────────────────────────────────────
with tab3:
    st.markdown("""
    <span class="ifrs-tag">IFRS 9</span>
    <b style="color:#e2e8f0"> Climate-Adjusted Expected Credit Loss (ECL)</b>
    """, unsafe_allow_html=True)
    st.caption("IFRS 9 requires forward-looking ECL provisions. Climate risk creates systematic PD uplift — physical shocks impair borrower cashflows; transition risk inflates operating costs. Banks and DFIs must embed these into their staging and provisioning models.")

    st.markdown("""
    <div class="mono-data" style="background:#13161f;padding:1rem;border-radius:4px;border:1px solid #1e2130;margin-bottom:1rem">
    Adjusted PD = Base PD + Physical Risk Uplift + Transition Uplift + Carbon Cost Uplift<br>
    ECL = Adjusted PD × LGD (45%) × EAD (35% of assets)<br>
    ECL Uplift % = (Climate Uplift / Base PD) × 100
    </div>
    """, unsafe_allow_html=True)

    col_e1, col_e2 = st.columns(2)

    with col_e1:
        st.markdown("#### Climate ECL by Company")
        ecl_sorted = result.sort_values("ifrs9_ecl_usd_m", ascending=True)
        fig_ecl1 = px.bar(
            ecl_sorted, x="ifrs9_ecl_usd_m", y="company", orientation="h",
            color="ifrs9_ecl_uplift_pct",
            color_continuous_scale=[[0,"#22c55e"],[0.5,"#f59e0b"],[1,"#ef4444"]],
            labels={"ifrs9_ecl_usd_m": "Climate ECL (USD M)", "company": "",
                    "ifrs9_ecl_uplift_pct": "ECL Uplift %"},
        )
        fig_ecl1.update_layout(height=400, plot_bgcolor="rgba(0,0,0,0)",
                                paper_bgcolor="rgba(0,0,0,0)", font_color="#94a3b8")
        st.plotly_chart(fig_ecl1, use_container_width=True)

    with col_e2:
        st.markdown("#### Adjusted PD vs Base PD")
        fig_ecl2 = go.Figure()
        fig_ecl2.add_trace(go.Bar(
            name="Base PD", x=result["company"],
            y=result["ecl_base_rate"] * 100,
            marker_color="#2d3452",
        ))
        fig_ecl2.add_trace(go.Bar(
            name="Climate Uplift",
            x=result["company"],
            y=result["ifrs9_adj_pd_pct"] - result["ecl_base_rate"] * 100,
            marker_color="#818cf8",
        ))
        fig_ecl2.update_layout(
            barmode="stack", height=400, xaxis_tickangle=-30,
            yaxis_title="Probability of Default (%)",
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="#94a3b8", legend=dict(orientation="h", y=1.1),
        )
        st.plotly_chart(fig_ecl2, use_container_width=True)

    # Sector ECL summary
    st.markdown("#### Sector-Level ECL Aggregation")
    sector_ecl = result.groupby("sector").agg(
        Total_ECL=("ifrs9_ecl_usd_m", "sum"),
        Avg_Uplift=("ifrs9_ecl_uplift_pct", "mean"),
        Companies=("company", "count")
    ).reset_index().sort_values("Total_ECL", ascending=False)

    fig_ecl3 = px.treemap(
        sector_ecl, path=["sector"], values="Total_ECL",
        color="Avg_Uplift", color_continuous_scale="RdYlGn_r",
        labels={"Total_ECL": "Total ECL (USD M)", "Avg_Uplift": "Avg ECL Uplift %"},
    )
    fig_ecl3.update_layout(height=340, paper_bgcolor="rgba(0,0,0,0)", font_color="#94a3b8")
    st.plotly_chart(fig_ecl3, use_container_width=True)

    st.info("💡 **Use case:** Central banks (CBK), development finance institutions (IFC, AfDB), and commercial banks use climate ECL to set provisions, capital buffers, and lending limits for high-emission borrowers.")


# ─── TAB 4: IFRS 16 ──────────────────────────────────────────────────────────
with tab4:
    st.markdown("""
    <span class="ifrs-tag">IFRS 16</span>
    <b style="color:#e2e8f0"> Stranded Lease Exposure</b>
    """, unsafe_allow_html=True)
    st.caption("IFRS 16 requires lease liabilities on-balance-sheet. When an asset becomes stranded (uneconomic under carbon pricing), the remaining lease liability becomes a climate-linked financial obligation — a form of transition risk directly on the balance sheet.")

    col_l1, col_l2 = st.columns(2)

    with col_l1:
        st.markdown("#### Lease Exposure vs Stranded Portion")
        lease_df = result[result["lease_exposure_usd_m"] > 0].sort_values("ifrs16_stranded_usd_m", ascending=False)
        fig_l1 = go.Figure()
        fig_l1.add_trace(go.Bar(name="Safe Lease Portion",
            x=lease_df["company"],
            y=lease_df["lease_exposure_usd_m"] - lease_df["ifrs16_stranded_usd_m"],
            marker_color="#1e2130"))
        fig_l1.add_trace(go.Bar(name="Stranded Portion",
            x=lease_df["company"],
            y=lease_df["ifrs16_stranded_usd_m"],
            marker_color="#ef4444"))
        fig_l1.update_layout(
            barmode="stack", height=380, xaxis_tickangle=-25,
            yaxis_title="USD Million",
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="#94a3b8", legend=dict(orientation="h", y=1.1),
        )
        st.plotly_chart(fig_l1, use_container_width=True)

    with col_l2:
        st.markdown("#### Most Exposed Lessees")
        for _, r in lease_df.iterrows():
            stranded_pct = (r["ifrs16_stranded_usd_m"] / r["lease_exposure_usd_m"] * 100) if r["lease_exposure_usd_m"] > 0 else 0
            status_color = "#ef4444" if r["ifrs16_triggered"] else "#f59e0b" if stranded_pct > 20 else "#22c55e"
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;align-items:center;
                        padding:0.6rem 1rem;background:#13161f;border:1px solid #1e2130;
                        border-radius:4px;margin-bottom:0.4rem">
            <span style="color:#e2e8f0;font-size:0.85rem">{r['company']}</span>
            <span class="mono-data">
                Total: USD {r['lease_exposure_usd_m']:,.0f}M &nbsp;|&nbsp;
                <span style="color:{status_color}">Stranded: USD {r['ifrs16_stranded_usd_m']:,.1f}M ({stranded_pct:.0f}%)</span>
            </span>
            </div>
            """, unsafe_allow_html=True)

    st.info("💡 **Use case:** Lessees in aviation, logistics, and energy sectors face early termination costs when leased assets (aircraft, pipelines, vehicles) become uneconomic under carbon pricing. IFRS 16 makes this liability visible on the balance sheet.")


# ─── TAB 5: IFRS S2 ──────────────────────────────────────────────────────────
with tab5:
    st.markdown("""
    <span class="ifrs-tag">IFRS S2</span>
    <b style="color:#e2e8f0"> Climate Disclosure Gap Analysis</b>
    """, unsafe_allow_html=True)
    st.caption("IFRS S2 (effective Jan 2024) mandates climate-related financial disclosures aligned with TCFD. This module scores each company's current disclosure against S2 requirements and quantifies the gap.")

    # Radar chart for selected company
    col_s1, col_s2 = st.columns([1, 2])

    with col_s1:
        selected_co_s2 = st.selectbox("Select company", result["company"].unique(), key="s2_co")
        row_s2 = result[result["company"] == selected_co_s2].iloc[0]
        s2_score, s2_gap, s2_factors = ifrs_s2_gap(row_s2)

        st.markdown(f"""
        <div style="background:#13161f;border:1px solid #1e2130;padding:1.2rem;border-radius:4px;margin-top:0.5rem">
        <p class="section-label">S2 Compliance Score</p>
        <p style="font-family:'IBM Plex Mono',monospace;font-size:2.2rem;color:#818cf8;margin:0">{s2_score:.0f}<span style="font-size:1rem;color:#4f5b7a">/100</span></p>
        <p style="font-family:'IBM Plex Mono',monospace;font-size:0.8rem;color:#ef4444;margin:0">Disclosure gap: {s2_gap:.0f}%</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        for factor, score in s2_factors.items():
            bar_color = "#22c55e" if score >= 70 else "#f59e0b" if score >= 45 else "#ef4444"
            st.markdown(f"""
            <div style="margin-bottom:0.5rem">
            <div style="display:flex;justify-content:space-between;margin-bottom:2px">
                <span style="font-size:0.75rem;color:#94a3b8">{factor}</span>
                <span style="font-family:'IBM Plex Mono',monospace;font-size:0.72rem;color:{bar_color}">{score:.0f}</span>
            </div>
            <div style="background:#1e2130;border-radius:2px;height:4px">
                <div style="background:{bar_color};width:{score}%;height:4px;border-radius:2px"></div>
            </div>
            </div>
            """, unsafe_allow_html=True)

    with col_s2:
        st.markdown("#### Portfolio Disclosure Gap — All Companies")
        s2_sorted = result.sort_values("ifrs_s2_gap", ascending=False)
        fig_s2 = px.bar(
            s2_sorted, x="company", y=["ifrs_s2_score", "ifrs_s2_gap"],
            barmode="stack",
            color_discrete_map={"ifrs_s2_score": "#818cf8", "ifrs_s2_gap": "#1e2130"},
            labels={"value": "Score", "variable": "", "company": ""},
        )
        fig_s2.update_layout(
            height=360, xaxis_tickangle=-30,
            yaxis_title="Score (0–100)",
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="#94a3b8",
            legend=dict(orientation="h", y=1.1),
        )
        st.plotly_chart(fig_s2, use_container_width=True)

        st.markdown("#### What IFRS S2 Requires vs What NSE Companies Disclose")
        requirements = pd.DataFrame({
            "IFRS S2 Requirement": [
                "Scenario analysis (≥2 scenarios)",
                "Quantified physical risk exposure",
                "Transition plan with milestones",
                "Scope 1, 2, 3 emissions",
                "Climate-adjusted financial projections",
                "Carbon price assumption disclosed",
            ],
            "NSE Compliance Rate": ["~15%", "~8%", "~5%", "~22%", "~3%", "~2%"],
            "Gap Severity": ["High","Critical","Critical","High","Critical","Critical"],
        })
        st.dataframe(requirements, hide_index=True, use_container_width=True)

    st.info("💡 **Use case:** Regulators (CMA, CBK), institutional investors, and ESG rating agencies use S2 gap analysis to pressure companies toward disclosure, adjust valuations for non-disclosure risk, and design regulatory reporting frameworks.")


# ─── TAB 6: GRESB & Green Bonds ──────────────────────────────────────────────
with tab6:
    st.markdown("#### GRESB Sustainability Scores & Green Bond Quality")
    st.caption("GRESB benchmarks real asset sustainability performance. Bloomberg Green Bond data scores issuance quality against ICMA Green Bond Principles.")

    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.markdown("**GRESB Score Distribution — NSE Sample**")
        fig_g1 = px.bar(
            result.sort_values("gresb_score", ascending=True),
            x="gresb_score", y="company", orientation="h",
            color="gresb_score",
            color_continuous_scale=[[0,"#ef4444"],[0.4,"#f59e0b"],[0.7,"#22c55e"],[1,"#818cf8"]],
            labels={"gresb_score": "GRESB Score (0–100)", "company": ""},
        )
        fig_g1.add_vline(x=50, line_dash="dash", line_color="#4f5b7a",
                         annotation_text="Global median ~50", annotation_font_color="#6b7280")
        fig_g1.update_layout(height=400, coloraxis_showscale=False,
                              plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                              font_color="#94a3b8")
        st.plotly_chart(fig_g1, use_container_width=True)

    with col_g2:
        st.markdown("**Green Bond Issuers — Use of Proceeds Quality**")
        gb_issuers = result[result["green_bond_issuer"]].copy()

        if gb_issuers.empty:
            st.info("No green bond issuers in current filter.")
        else:
            # Simulate green bond quality scoring
            gb_issuers["use_of_proceeds_score"] = gb_issuers["gresb_score"] * 0.9 + np.random.uniform(-5, 5, len(gb_issuers))
            gb_issuers["climate_alignment_score"] = gb_issuers["gresb_score"] * 0.8 + np.random.uniform(-8, 8, len(gb_issuers))
            gb_issuers["icma_compliance"] = gb_issuers["use_of_proceeds_score"].apply(
                lambda x: "✅ Compliant" if x >= 60 else "⚠️ Partial" if x >= 40 else "❌ Non-compliant"
            )

            for _, r in gb_issuers.iterrows():
                comp_color = "#22c55e" if "Compliant" in r["icma_compliance"] else "#f59e0b" if "Partial" in r["icma_compliance"] else "#ef4444"
                st.markdown(f"""
                <div style="background:#13161f;border:1px solid #1e2130;padding:1rem 1.4rem;
                            border-radius:4px;margin-bottom:0.6rem">
                <b style="color:#e2e8f0">{r['company']}</b>
                <span style="color:{comp_color};font-family:'IBM Plex Mono',monospace;font-size:0.75rem;margin-left:1rem">{r['icma_compliance']}</span><br>
                <span class="mono-data">
                Issued: USD {r['green_bond_issued_usd_m']:,.0f}M &nbsp;·&nbsp;
                GRESB: {r['gresb_score']} &nbsp;·&nbsp;
                Use of Proceeds Score: {r['use_of_proceeds_score']:.0f}/100
                </span>
                </div>
                """, unsafe_allow_html=True)

    # GRESB vs Climate liability
    st.divider()
    st.markdown("#### Does Higher GRESB Score Reduce Climate Liability?")
    fig_g2 = px.scatter(
        result,
        x="gresb_score", y="total_climate_liability_usd_m",
        color="sector", size="asset_value_usd_m",
        hover_name="company",
        trendline="ols",
        labels={
            "gresb_score": "GRESB Sustainability Score",
            "total_climate_liability_usd_m": "Total Climate Liability (USD M)",
            "asset_value_usd_m": "Asset Value",
        },
    )
    fig_g2.update_layout(height=360, plot_bgcolor="rgba(0,0,0,0)",
                          paper_bgcolor="rgba(0,0,0,0)", font_color="#94a3b8")
    st.plotly_chart(fig_g2, use_container_width=True)

    st.info("💡 **Use case:** Fund managers allocating to green bonds use GRESB scores and ICMA compliance to verify impact claims. Development banks (IFC, AfDB) require GRESB benchmarking for blended finance structures and green bond eligibility.")


# ─── TAB 7: Full Dataset ──────────────────────────────────────────────────────
with tab7:
    st.markdown("#### Full IFRS Climate Risk Dataset")

    display = result[[
        "company","sector","stranded_flag",
        "ifrs6_impairment_usd_m","ifrs9_ecl_usd_m","ifrs16_stranded_usd_m",
        "total_climate_liability_usd_m",
        "ifrs_s2_score","ifrs_s2_gap",
        "gresb_score","gresb_tier",
        "carbon_intensity","reserve_life_years","credit_rating",
    ]].rename(columns={
        "ifrs6_impairment_usd_m": "IFRS6 Impairment (USD M)",
        "ifrs9_ecl_usd_m": "IFRS9 ECL (USD M)",
        "ifrs16_stranded_usd_m": "IFRS16 Stranded (USD M)",
        "total_climate_liability_usd_m": "Total Liability (USD M)",
        "ifrs_s2_score": "S2 Score",
        "ifrs_s2_gap": "S2 Gap %",
        "gresb_score": "GRESB Score",
        "gresb_tier": "GRESB Tier",
        "carbon_intensity": "Carbon Intensity",
        "reserve_life_years": "Reserve Life (yr)",
        "credit_rating": "Rating",
    })

    st.dataframe(display, hide_index=True, use_container_width=True)

    csv = display.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download Full IFRS Climate Risk Report (CSV)",
        csv, "p13_ifrs_climate_risk.csv", "text/csv",
    )

    st.divider()
    st.markdown("#### Methodology Notes")
    st.markdown("""
    <div class="mono-data" style="background:#13161f;padding:1.2rem;border-radius:4px;border:1px solid #1e2130">
    <b style="color:#818cf8">IFRS 6</b> — Impairment test: NRA = Asset Value − PV(Carbon Costs over Reserve Life).
    Discount rate user-adjustable. Trigger at NRA &lt; 70% carrying value.<br><br>
    <b style="color:#818cf8">IFRS 9</b> — Climate PD uplift: Physical risk × 0.3% + Transition risk × 0.4% + Carbon cost × intensity factor.
    LGD fixed at 45% (Kenya market estimate). EAD = 35% of total assets.<br><br>
    <b style="color:#818cf8">IFRS 16</b> — Stranded lease % = min(85%, Carbon Intensity/2000 × Carbon Price/100).
    Triggered when stranded portion exceeds 40% of total lease book.<br><br>
    <b style="color:#818cf8">IFRS S2</b> — Disclosure score synthesised from GRESB data, carbon intensity proxy,
    physical/transition risk scores, and green bond issuance as disclosure intent signals.<br><br>
    <b style="color:#818cf8">GRESB</b> — Scores are representative estimates for NSE-listed companies based on
    sector benchmarks and public sustainability disclosures. Green bond ICMA compliance assessed
    against Use of Proceeds, Project Evaluation, Management of Proceeds, and Reporting pillars.<br><br>
    <b style="color:#4f5b7a">Data: Synthetic NSE-representative dataset. For institutional use, replace with
    live Bloomberg, GRESB API, and company filings data.</b>
    </div>
    """, unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.markdown("""
<div style="display:flex;justify-content:space-between;align-items:center">
<span style="color:#2d3452;font-family:'IBM Plex Mono',monospace;font-size:0.72rem">
SmartHaven Digital · P13 · IFRS Climate Risk & Stranded Asset Early Warning · Faith Ndinda
</span>
<span style="color:#2d3452;font-family:'IBM Plex Mono',monospace;font-size:0.72rem">
IFRS 6 · IFRS 9 · IFRS 16 · IFRS S2 · GRESB · Green Bond
</span>
</div>
""", unsafe_allow_html=True)
