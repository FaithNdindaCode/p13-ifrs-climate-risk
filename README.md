# P13 · IFRS Climate Risk & Stranded Asset Early Warning System
**SmartHaven Digital · Financial Engineering Portfolio**

## What This Does
Translates climate risk into **balance sheet impact** under four IFRS standards, with a real-time stranded asset early warning system and sustainability scoring.

## Standards Coverage
| Module | Standard | What It Models |
|---|---|---|
| Reserve Impairment | IFRS 6 | Carbon-price-triggered write-downs on E&E assets |
| Climate ECL | IFRS 9 | PD uplift from physical & transition risk |
| Stranded Leases | IFRS 16 | Lease liabilities exposed to carbon pricing |
| Disclosure Gap | IFRS S2 | Distance from full TCFD-aligned disclosure |
| Sustainability | GRESB | Benchmark scores for NSE-listed companies |
| Green Finance | Bloomberg GB | ICMA Green Bond Principles compliance |

## Stranded Asset Trigger Logic
```
IF carbon_price > $100/tonne CO₂e
AND reserve_life < 10 years
→ STRANDED flag triggered

SUPPORTING TRIGGERS:
- Carbon intensity > 800 tCO₂e/USD M revenue
- Physical risk score > 8.0
- Transition risk score > 8.0
```

## Run Locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy to Streamlit Cloud
1. Push to GitHub
2. Connect repo at share.streamlit.io
3. Set main file: `app.py`

## Who Should Use This
- **Fund managers** — climate liability before allocation
- **Auditors (Big 4)** — IFRS 6/9/16 impairment evidence
- **Regulators (CBK, CMA)** — sector-wide stranded asset exposure
- **DFIs (IFC, AfDB)** — climate due diligence on Kenyan assets
- **Green bond issuers** — ICMA compliance self-assessment

## Portfolio Context
Part of SmartHaven Digital's 12-project Financial Engineering Portfolio targeting the Global Data Festival, Nairobi. Connects to P02 (TCFD Climate Risk Dashboard) as the accounting standards layer.

**Faith Ndinda · SmartHaven Digital · Nairobi, Kenya**
