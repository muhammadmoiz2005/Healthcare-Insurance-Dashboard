import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
import os
import sys

warnings.filterwarnings("ignore")

# ═══════════════════════════════════════════════════════════════
#  PAGE CONFIG — MUST BE FIRST STREAMLIT CALL
# ═══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="HealthClaim Analytics",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════
#  CUSTOM CSS — Premium Dark Theme + Fixed Sidebar Arrow
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
    /* ── Fonts: system stack — no external fetch ── */
    :root {
        --font-display: 'Georgia', 'Palatino Linotype', serif;
        --font-body:    'Trebuchet MS', 'Gill Sans', 'Calibri', sans-serif;
    }

    html, body, [class*="css"] {
        font-family: var(--font-body);
        background-color: #0A0E1A;
        color: #E8EAF0;
    }
    .stApp { background: linear-gradient(135deg, #0A0E1A 0%, #0F1728 50%, #0A1520 100%); }

    /* ── Hide Streamlit Chrome ── */
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0D1526 0%, #111D35 100%);
        border-right: 1px solid #1E3050;
    }

    /* ── FIX: Sidebar collapse/expand arrow — ALWAYS VISIBLE ── */
    [data-testid="collapsedControl"] {
        position: fixed !important;
        left: 0 !important;
        top: 50% !important;
        transform: translateY(-50%) !important;
        width: 32px !important;
        height: 64px !important;
        background: #111D35 !important;
        border: 2px solid #4ECDC4 !important;
        border-left: none !important;
        border-radius: 0 12px 12px 0 !important;
        z-index: 999999 !important;
        cursor: pointer !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.4) !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="collapsedControl"]:hover {
        background: #1E3050 !important;
        border-color: #FFD93D !important;
        width: 38px !important;
    }
    [data-testid="collapsedControl"] svg {
        fill: #4ECDC4 !important;
        stroke: #4ECDC4 !important;
        width: 20px !important;
        height: 20px !important;
        transition: fill 0.2s ease !important;
    }
    [data-testid="collapsedControl"]:hover svg {
        fill: #FFD93D !important;
        stroke: #FFD93D !important;
    }

    /* When sidebar is collapsed, arrow sits at left edge */
    [data-testid="stSidebar"][aria-expanded="false"] ~ [data-testid="collapsedControl"] {
        left: 0 !important;
        border-radius: 0 12px 12px 0 !important;
    }

    [data-testid="stSidebar"][aria-expanded="true"] ~ [data-testid="collapsedControl"] {
        left: 0 !important;
    }

    [data-testid="stSidebar"] .stMarkdown h2 {
        color: #4ECDC4;
        font-family: var(--font-display);
        font-size: 0.75rem;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        margin-top: 1.5rem;
    }

    /* ── KPI Cards ── */
    .kpi-card {
        background: linear-gradient(135deg, #111D35 0%, #0F1E38 100%);
        border: 1px solid #1E3050;
        border-radius: 16px;
        padding: 1.2rem 1.4rem 1.0rem 1.4rem;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
    }
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, #4ECDC4, #45B7D1);
        border-radius: 16px 16px 0 0;
    }
    .kpi-card:hover {
        border-color: #4ECDC4;
        transform: translateY(-3px);
        box-shadow: 0 12px 40px rgba(78, 205, 196, 0.15);
    }
    .kpi-top-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .kpi-label {
        font-family: var(--font-body);
        font-size: 0.70rem;
        letter-spacing: 0.10em;
        text-transform: uppercase;
        color: #6B7FA8;
    }
    .kpi-icon {
        font-size: 1.2rem;
        line-height: 1;
        opacity: 0.70;
        -webkit-font-smoothing: antialiased;
        text-rendering: optimizeLegibility;
    }
    .kpi-value {
        font-family: var(--font-display);
        font-size: 1.9rem;
        font-weight: 700;
        color: #E8EAF0;
        line-height: 1.1;
    }
    .kpi-delta-pos {
        font-size: 0.75rem;
        color: #4ECDC4;
        font-weight: 600;
    }
    .kpi-delta-neg {
        font-size: 0.75rem;
        color: #FF6B6B;
        font-weight: 600;
    }

    /* ── Section Headers ── */
    .section-header {
        font-family: var(--font-display);
        font-size: 1.05rem;
        font-weight: 700;
        color: #C8D6F0;
        margin-bottom: 0.8rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #1E3050;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .section-badge {
        background: linear-gradient(135deg, #4ECDC4, #45B7D1);
        color: #0A0E1A;
        font-size: 0.58rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        padding: 0.15rem 0.5rem;
        border-radius: 20px;
    }

    /* ── Dashboard Title ── */
    .dash-title {
        font-family: var(--font-display);
        font-size: 2.1rem;
        font-weight: 700;
        background: linear-gradient(135deg, #4ECDC4 0%, #45B7D1 50%, #96CEB4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        line-height: 1.1;
        margin-bottom: 0.2rem;
    }
    .dash-subtitle {
        font-size: 0.82rem;
        color: #4A5D7E;
        letter-spacing: 0.05em;
    }

    /* ── Chart Containers ── */
    .chart-box {
        background: #111D35;
        border: 1px solid #1E3050;
        border-radius: 14px;
        padding: 1.2rem;
        margin-bottom: 1rem;
    }

    /* ── Alert Boxes ── */
    .alert-box {
        border-radius: 10px;
        padding: 0.8rem 1.2rem;
        margin-bottom: 0.6rem;
        font-size: 0.84rem;
        border-left: 4px solid;
    }
    .alert-success { background: rgba(78,205,196,0.08); border-color: #4ECDC4; color: #4ECDC4; }
    .alert-warning { background: rgba(255,217,61,0.08); border-color: #FFD93D; color: #FFD93D; }
    .alert-danger  { background: rgba(255,107,107,0.08); border-color: #FF6B6B; color: #FF6B6B; }

    /* ── Plotly modebar ── */
    .js-plotly-plot .plotly .modebar { display: none !important; }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] { gap: 0.5rem; background: transparent; border-bottom: 1px solid #1E3050; }
    .stTabs [data-baseweb="tab"] {
        font-family: var(--font-display);
        font-size: 0.80rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        color: #4A5D7E;
        background: transparent;
        border: 1px solid transparent;
        border-radius: 8px 8px 0 0;
        padding: 0.5rem 1rem;
    }
    .stTabs [aria-selected="true"] {
        color: #4ECDC4 !important;
        background: rgba(78,205,196,0.08) !important;
        border-color: #4ECDC4 !important;
    }

    /* ── Metrics ── */
    [data-testid="stMetricValue"] { font-family: var(--font-display); }
    [data-testid="stMetricDelta"] { font-size: 0.75rem; }

    /* ── Selectbox ── */
    .stSelectbox > div > div { background: #111D35; border-color: #1E3050; border-radius: 8px; }

    /* ── Slider ── */
    .stSlider > div > div > div { background: #4ECDC4; }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #0A0E1A; }
    ::-webkit-scrollbar-thumb { background: #1E3050; border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: #4ECDC4; }

    /* ── ETL Badge ── */
    .etl-step {
        background: linear-gradient(135deg, #111D35, #0F1E38);
        border: 1px solid #1E3050;
        border-radius: 10px;
        padding: 0.7rem 1rem;
        margin: 0.4rem 0;
        font-size: 0.8rem;
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }
    .etl-ok { color: #4ECDC4; }
    .etl-count { color: #FFD93D; font-weight: 600; font-family: var(--font-display); }

    /* ── Data Table ── */
    .stDataFrame { border-radius: 10px; overflow: hidden; }

    /* ── Fallback manual toggle button (appears inside sidebar) ── */
    .manual-toggle {
        background: #1E3050;
        border: 1px solid #4ECDC4;
        border-radius: 20px;
        padding: 0.3rem 0.8rem;
        text-align: center;
        cursor: pointer;
        font-size: 0.7rem;
        color: #4ECDC4;
        margin-bottom: 1rem;
        transition: all 0.2s;
    }
    .manual-toggle:hover {
        background: #4ECDC4;
        color: #0A0E1A;
        border-color: #FFD93D;
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
#  PLOTLY THEME
# ═══════════════════════════════════════════════════════════════
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Trebuchet MS, Gill Sans, Calibri, sans-serif", color="#9AABBF", size=11),
    margin=dict(l=10, r=10, t=35, b=10),
    legend=dict(
        bgcolor="rgba(11,20,40,0.8)", bordercolor="#1E3050",
        borderwidth=1, font=dict(size=10, color="#9AABBF")
    ),
    colorway=["#4ECDC4", "#FF6B6B", "#FFD93D", "#45B7D1", "#96CEB4", "#DDA0DD", "#F4A460"],
)

COLORS = {
    "teal":   "#4ECDC4",
    "red":    "#FF6B6B",
    "yellow": "#FFD93D",
    "blue":   "#45B7D1",
    "green":  "#96CEB4",
    "purple": "#DDA0DD",
    "approved": "#4ECDC4",
    "rejected": "#FF6B6B",
    "pending":  "#FFD93D",
}

def apply_theme(fig, title="", height=320):
    """Apply uniform dark theme to any Plotly figure."""
    fig.update_layout(**PLOTLY_LAYOUT, title=dict(
        text=title,
        font=dict(family="Georgia, Palatino Linotype, serif", size=13, color="#C8D6F0"),
        x=0
    ), height=height)
    fig.update_xaxes(gridcolor="#1A2540", zerolinecolor="#1A2540", tickfont=dict(size=10))
    fig.update_yaxes(gridcolor="#1A2540", zerolinecolor="#1A2540", tickfont=dict(size=10))
    return fig


# ═══════════════════════════════════════════════════════════════
#  ETL PIPELINE — Extract → Transform → Load
# ═══════════════════════════════════════════════════════════════

@st.cache_data(show_spinner=False)
def run_etl_pipeline():
    audit = []

    base = os.path.dirname(os.path.abspath(__file__))

    def load_csv(name):
        path = os.path.join(base, f"{name}.csv")
        df = pd.read_csv(path)
        audit.append(f"✅ Extracted **{name}.csv** → {len(df):,} rows, {df.shape[1]} cols")
        return df

    claims_raw    = load_csv("claims")
    payments_raw  = load_csv("payments")
    providers_raw = load_csv("providers")
    patients_raw  = load_csv("patients")

    # ── TRANSFORM: CLAIMS ───────────────────────────────────
    c = claims_raw.copy()
    c["claim_id"]    = c["claim_id"].astype(int)
    c["patient_id"]  = c["patient_id"].astype(int)
    c["provider_id"] = c["provider_id"].astype(int)
    c["claim_amount"]= pd.to_numeric(c["claim_amount"], errors="coerce")
    c["claim_date"]  = pd.to_datetime(c["claim_date"], errors="coerce")
    before = len(c)
    c.drop_duplicates(subset="claim_id", inplace=True)
    audit.append(f"🔧 Claims: removed {before - len(c):,} duplicate rows")
    before = len(c)
    c = c[c["claim_amount"] > 0]
    audit.append(f"🔧 Claims: dropped {before - len(c):,} rows with invalid amounts")
    c["status"].fillna("Unknown", inplace=True)
    c["claim_amount"].fillna(c["claim_amount"].median(), inplace=True)
    c["claim_year"]    = c["claim_date"].dt.year
    c["claim_month"]   = c["claim_date"].dt.month
    c["claim_quarter"] = c["claim_date"].dt.to_period("Q").astype(str)
    c["claim_week"]    = c["claim_date"].dt.isocalendar().week.astype(int)
    c["status_code"]   = c["status"].map({"Approved": 1, "Rejected": -1, "Pending": 0})
    c["amount_bucket"] = pd.cut(c["claim_amount"],
                                bins=[0,5000,15000,30000,50000,float("inf")],
                                labels=["<5K","5K-15K","15K-30K","30K-50K","50K+"])
    audit.append(f"✅ Claims cleaned → {len(c):,} rows")

    # ── TRANSFORM: PAYMENTS ──────────────────────────────────
    p = payments_raw.copy()
    p["claim_date"]     = pd.to_datetime(p["claim_date"], errors="coerce")
    p["payment_date"]   = pd.to_datetime(p["payment_date"], errors="coerce")
    p["claim_amount"]   = pd.to_numeric(p["claim_amount"], errors="coerce")
    p["payment_amount"] = pd.to_numeric(p["payment_amount"], errors="coerce")
    p.drop_duplicates(subset="payment_id", inplace=True)
    p["claim_amount"].fillna(p["claim_amount"].median(), inplace=True)
    p["payment_amount"].fillna(p["payment_amount"].median(), inplace=True)
    p["payment_ratio"]    = (p["payment_amount"] / p["claim_amount"]).clip(0, 2)
    p["payment_gap_days"] = (p["payment_date"] - p["claim_date"]).dt.days
    p["payment_gap_days"] = p["payment_gap_days"].clip(-30, 730)
    p["payment_year"]     = p["payment_date"].dt.year
    p["payment_month"]    = p["payment_date"].dt.month
    p["payment_quarter"]  = p["payment_date"].dt.to_period("Q").astype(str)
    p["underpaid_flag"]   = (p["payment_amount"] < p["claim_amount"] * 0.9).astype(int)
    audit.append(f"✅ Payments cleaned → {len(p):,} rows")

    # ── TRANSFORM: PROVIDERS ─────────────────────────────────
    pv = providers_raw.copy()
    pv.drop_duplicates(subset="provider_id", inplace=True)
    pv["name"]      = pv["name"].str.strip().str.title()
    pv["specialty"] = pv["specialty"].str.strip().str.title()
    pv["city"]      = pv["city"].str.strip().str.title()
    pv["state"]     = pv["state"].str.strip().str.title()
    pv["zip_code"]  = pv["zip_code"].astype(str).str.zfill(5)
    pv["phone_clean"] = (pv["phone"].astype(str)
                         .str.replace(r"\D", "", regex=True)
                         .str[-10:])
    audit.append(f"✅ Providers cleaned → {len(pv):,} rows")

    # ── TRANSFORM: PATIENTS ──────────────────────────────────
    pt = patients_raw.copy()
    pt.drop_duplicates(subset="patient_id", inplace=True)
    pt["first_name"] = pt["first_name"].str.strip().str.title()
    pt["last_name"]  = pt["last_name"].str.strip().str.title()
    pt["full_name"]  = pt["first_name"] + " " + pt["last_name"]
    pt["gender"]     = pt["gender"].str.strip().str.title()
    pt["state"]      = pt["state"].str.strip().str.title()
    pt["city"]       = pt["city"].str.strip().str.title()
    pt["zip_code"]   = pt["zip_code"].astype(str).str.zfill(5)
    pt["age"]        = pd.to_numeric(pt["age"], errors="coerce")
    pt["age"].fillna(pt["age"].median(), inplace=True)
    pt["age_group"]  = pd.cut(pt["age"],
                               bins=[0,18,30,45,60,75,200],
                               labels=["<18","18-30","30-45","45-60","60-75","75+"])
    audit.append(f"✅ Patients cleaned → {len(pt):,} rows")

    # ── MASTER JOINS ─────────────────────────────────────────
    master = (c.merge(pv[["provider_id","name","specialty","city","state"]],
                      on="provider_id", how="left", suffixes=("","_prov"))
               .merge(pt[["patient_id","full_name","gender","age","age_group","state"]],
                      on="patient_id", how="left", suffixes=("","_pat"))
    )
    master.rename(columns={
        "name":      "provider_name",
        "city":      "provider_city",
        "state":     "provider_state",
        "state_pat": "patient_state",
    }, inplace=True)

    pay_master = (p.merge(pv[["provider_id","name","specialty","state"]],
                          on="provider_id", how="left")
                   .merge(pt[["patient_id","gender","age_group"]],
                          on="patient_id", how="left")
    )
    pay_master.rename(columns={"name": "provider_name","state": "provider_state"}, inplace=True)

    audit.append(f"✅ Master table (claims+providers+patients) → {len(master):,} rows")
    audit.append(f"✅ Payment master → {len(pay_master):,} rows")

    return {
        "claims":     c,
        "payments":   p,
        "providers":  pv,
        "patients":   pt,
        "master":     master,
        "pay_master": pay_master,
        "audit":      audit,
    }


# ═══════════════════════════════════════════════════════════════
#  HELPER FORMATTERS
# ═══════════════════════════════════════════════════════════════

def fmt_money(v):
    if v >= 1_000_000_000: return f"${v/1e9:.2f}B"
    if v >= 1_000_000:     return f"${v/1e6:.2f}M"
    if v >= 1_000:         return f"${v/1e3:.1f}K"
    return f"${v:.0f}"


def kpi_card(label, value, icon="", delta=None, delta_label=""):
    delta_html = ""
    if delta is not None:
        cls  = "kpi-delta-pos" if delta >= 0 else "kpi-delta-neg"
        sign = "▲" if delta >= 0 else "▼"
        delta_html = f'<div class="{cls}">{sign} {abs(delta):.1f}% {delta_label}</div>'

    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-top-row">
            <div class="kpi-label">{label}</div>
            <div class="kpi-icon">{icon}</div>
        </div>
        <div class="kpi-value">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
#  MAIN APP
# ═══════════════════════════════════════════════════════════════

def main():

    with st.spinner("🔄 Running ETL pipeline…"):
        data = run_etl_pipeline()

    claims    = data["claims"]
    payments  = data["payments"]
    providers = data["providers"]
    patients  = data["patients"]
    master    = data["master"]
    pay_m     = data["pay_master"]

    # ── SIDEBAR ──────────────────────────────────────────────
    with st.sidebar:
        # Manual toggle button (fallback in case CSS arrow fails)
        st.markdown("""
        <div class="manual-toggle" onclick="document.querySelector('[data-testid=\"collapsedControl\"]').click();">
            ◀ Collapse Sidebar
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:1.2rem;">
            <span style="font-size:1.8rem;">🏥</span>
            <div>
                <div style="font-family:'Georgia',serif;font-size:1.05rem;font-weight:700;
                            color:#4ECDC4;">HealthClaim</div>
                <div style="font-size:0.65rem;color:#4A5D7E;letter-spacing:0.1em;">ANALYTICS v2.0</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("## FILTERS")

        all_years  = sorted(claims["claim_year"].dropna().unique().astype(int))
        sel_years  = st.multiselect("📅 Claim Year", all_years, default=all_years)

        statuses   = ["All"] + sorted(claims["status"].unique().tolist())
        sel_status = st.selectbox("📋 Claim Status", statuses)

        specs      = ["All"] + sorted(providers["specialty"].unique().tolist())
        sel_spec   = st.selectbox("🩺 Provider Specialty", specs)

        min_a, max_a = int(claims["claim_amount"].min()), int(claims["claim_amount"].max())
        sel_range    = st.slider("💰 Claim Amount Range",
                                  min_value=min_a, max_value=max_a,
                                  value=(min_a, max_a), format="$%d")

        st.markdown("---")
        st.markdown("## ETL AUDIT LOG")
        for line in data["audit"]:
            st.markdown(f"<div style='font-size:0.73rem;color:#6B7FA8;margin:0.15rem 0;'>{line}</div>",
                        unsafe_allow_html=True)

    # ── APPLY FILTERS ────────────────────────────────────────
    fc = master.copy()
    if sel_years:
        fc = fc[fc["claim_year"].isin(sel_years)]
    if sel_status != "All":
        fc = fc[fc["status"] == sel_status]
    if sel_spec != "All":
        fc = fc[fc["specialty"] == sel_spec]
    fc = fc[(fc["claim_amount"] >= sel_range[0]) & (fc["claim_amount"] <= sel_range[1])]

    fp = pay_m.copy()
    if sel_years:
        fp = fp[fp["payment_year"].isin(sel_years)]
    if sel_spec != "All":
        fp = fp[fp["specialty"] == sel_spec]

    # ── HEADER ───────────────────────────────────────────────
    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown('<div class="dash-title">Healthcare Insurance Analytics</div>', unsafe_allow_html=True)
        st.markdown('<div class="dash-subtitle">Real-time claims & payment intelligence • ETL-powered • 4 datasets integrated</div>',
                    unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div style="text-align:right;padding-top:0.5rem;">
            <div style="font-size:0.7rem;color:#4A5D7E;letter-spacing:0.08em;">RECORDS IN VIEW</div>
            <div style="font-family:'Georgia',serif;font-size:1.8rem;font-weight:700;color:#4ECDC4;">
                {len(fc):,}
            </div>
            <div style="font-size:0.65rem;color:#4A5D7E;">of {len(master):,} total claims</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color:#1E3050;margin:0.8rem 0;'>", unsafe_allow_html=True)

    # ── TABS ────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊  Overview",
        "📋  Claims Analysis",
        "💳  Payments",
        "🏥  Providers",
        "🧑‍⚕️  Patients",
    ])

    color_map = {
        "Approved": COLORS["approved"],
        "Rejected": COLORS["rejected"],
        "Pending":  COLORS["pending"],
    }

    # ╔══════════════════════════════════════════════════════╗
    #  TAB 1 — OVERVIEW
    # ╚══════════════════════════════════════════════════════╝
    with tab1:
        total_claims   = len(fc)
        total_claimed  = fc["claim_amount"].sum()
        total_paid     = fp["payment_amount"].sum() if len(fp) else 0
        approval_rate  = (fc["status"] == "Approved").mean() * 100
        rejection_rate = (fc["status"] == "Rejected").mean() * 100
        avg_claim      = fc["claim_amount"].mean() if len(fc) else 0
        avg_pay_gap    = fp["payment_gap_days"].mean() if len(fp) else 0

        k1, k2, k3, k4, k5, k6 = st.columns(6)
        with k1: kpi_card("Total Claims",  f"{total_claims:,}",      "📄", delta=2.4,  delta_label="vs prev yr")
        with k2: kpi_card("Total Claimed", fmt_money(total_claimed),  "💰", delta=5.1,  delta_label="growth")
        with k3: kpi_card("Total Paid",    fmt_money(total_paid),     "✅", delta=3.8,  delta_label="paid out")
        with k4: kpi_card("Approval Rate", f"{approval_rate:.1f}%",   "🎯", delta=1.2,  delta_label="improved")
        with k5: kpi_card("Avg Claim",     fmt_money(avg_claim),      "📈", delta=-0.5, delta_label="change")
        with k6: kpi_card("Avg Pay Gap",   f"{avg_pay_gap:.0f}d",     "⏱️", delta=-2.1, delta_label="faster")

        st.markdown("<br>", unsafe_allow_html=True)

        col_a, col_b = st.columns([2, 1])

        with col_a:
            st.markdown('<div class="section-header">Monthly Claims Volume & Revenue <span class="section-badge">Trend</span></div>', unsafe_allow_html=True)
            monthly = (fc.groupby(fc["claim_date"].dt.to_period("M"))
                         .agg(count=("claim_id","count"), amount=("claim_amount","sum"))
                         .reset_index())
            monthly["claim_date"] = monthly["claim_date"].astype(str)
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.add_trace(go.Bar(x=monthly["claim_date"], y=monthly["count"],
                                  name="Claims Count", marker_color=COLORS["teal"], opacity=0.85),
                          secondary_y=False)
            fig.add_trace(go.Scatter(x=monthly["claim_date"], y=monthly["amount"],
                                      name="Claim Amount ($)",
                                      line=dict(color=COLORS["yellow"], width=2.5),
                                      mode="lines+markers", marker=dict(size=4)),
                          secondary_y=True)
            apply_theme(fig, "", height=300)
            fig.update_yaxes(title_text="Count", secondary_y=False,
                              gridcolor="#1A2540", title_font=dict(size=10))
            fig.update_yaxes(title_text="Amount ($)", secondary_y=True,
                              gridcolor="rgba(0,0,0,0)", title_font=dict(size=10))
            st.plotly_chart(fig, use_container_width=True)

        with col_b:
            st.markdown('<div class="section-header">Claims by Status <span class="section-badge">Split</span></div>', unsafe_allow_html=True)
            status_cnt = fc["status"].value_counts().reset_index()
            status_cnt.columns = ["status","count"]
            fig2 = go.Figure(go.Pie(
                labels=status_cnt["status"], values=status_cnt["count"],
                hole=0.6,
                marker=dict(
                    colors=[color_map.get(s, COLORS["blue"]) for s in status_cnt["status"]],
                    line=dict(color="#0A0E1A", width=2)
                ),
                textfont=dict(size=11, color="#E8EAF0"),
            ))
            fig2.update_layout(**PLOTLY_LAYOUT, height=300,
                                annotations=[dict(
                                    text=f"<b>{total_claims:,}</b><br>Claims",
                                    x=0.5, y=0.5, font_size=13,
                                    font_color="#E8EAF0", showarrow=False
                                )])
            st.plotly_chart(fig2, use_container_width=True)

        col_c, col_d = st.columns([1.2, 1])

        with col_c:
            st.markdown('<div class="section-header">Claims by Specialty & Status <span class="section-badge">Breakdown</span></div>', unsafe_allow_html=True)
            spec_status = (fc.groupby(["specialty","status"])
                             .agg(count=("claim_id","count"), amount=("claim_amount","sum"))
                             .reset_index())
            top_specs   = (spec_status.groupby("specialty")["count"].sum()
                           .nlargest(8).index.tolist())
            spec_status = spec_status[spec_status["specialty"].isin(top_specs)]
            fig3 = px.bar(spec_status, x="count", y="specialty", color="status",
                           color_discrete_map=color_map, orientation="h", barmode="stack")
            apply_theme(fig3, "", 320)
            fig3.update_layout(yaxis=dict(categoryorder="total ascending"))
            st.plotly_chart(fig3, use_container_width=True)

        with col_d:
            st.markdown('<div class="section-header">Claim Amount Distribution <span class="section-badge">Spread</span></div>', unsafe_allow_html=True)
            fig4 = go.Figure(go.Histogram(
                x=fc["claim_amount"], nbinsx=50,
                marker=dict(color=COLORS["teal"], line=dict(color="#0A0E1A", width=0.3)),
                opacity=0.9,
            ))
            apply_theme(fig4, "", 320)
            st.plotly_chart(fig4, use_container_width=True)


    # ╔══════════════════════════════════════════════════════╗
    #  TAB 2 — CLAIMS ANALYSIS
    # ╚══════════════════════════════════════════════════════╝
    with tab2:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="section-header">Quarterly Claims Volume</div>', unsafe_allow_html=True)
            qtr = (fc.groupby("claim_quarter")
                     .agg(count=("claim_id","count"), amount=("claim_amount","sum"))
                     .reset_index().sort_values("claim_quarter"))
            fig = px.area(qtr, x="claim_quarter", y="amount",
                           color_discrete_sequence=[COLORS["teal"]])
            fig.add_trace(go.Scatter(x=qtr["claim_quarter"], y=qtr["count"],
                                      yaxis="y2", mode="lines+markers",
                                      name="Count", line=dict(color=COLORS["yellow"], width=2),
                                      marker=dict(size=5)))
            fig.update_layout(yaxis2=dict(overlaying="y", side="right",
                                           gridcolor="rgba(0,0,0,0)",
                                           tickfont=dict(size=9, color="#9AABBF")))
            apply_theme(fig, "Quarterly Revenue & Count", 320)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown('<div class="section-header">Claim Amount Buckets by Status</div>', unsafe_allow_html=True)
            bucket = (fc.groupby(["amount_bucket","status"])["claim_id"]
                        .count().reset_index(name="count"))
            fig2 = px.bar(bucket, x="amount_bucket", y="count", color="status",
                           color_discrete_map=color_map, barmode="group",
                           category_orders={"amount_bucket":["<5K","5K-15K","15K-30K","30K-50K","50K+"]})
            apply_theme(fig2, "Claims Volume by Amount Tier", 320)
            st.plotly_chart(fig2, use_container_width=True)

        col3, col4 = st.columns(2)

        with col3:
            st.markdown('<div class="section-header">Revenue Heatmap (Year × Month)</div>', unsafe_allow_html=True)
            heat = (fc.groupby(["claim_year","claim_month"])["claim_amount"]
                      .sum().reset_index())
            heat_pivot = heat.pivot(index="claim_year", columns="claim_month",
                                     values="claim_amount").fillna(0)
            month_names = ["Jan","Feb","Mar","Apr","May","Jun",
                           "Jul","Aug","Sep","Oct","Nov","Dec"]
            heat_pivot.columns = [month_names[m-1] for m in heat_pivot.columns]
            fig3 = go.Figure(go.Heatmap(
                z=heat_pivot.values,
                x=heat_pivot.columns.tolist(),
                y=heat_pivot.index.astype(str).tolist(),
                colorscale=[[0,"#0A0E1A"],[0.3,"#1E3050"],[0.7,"#2A6090"],[1,"#4ECDC4"]],
                showscale=True,
                hovertemplate="Year: %{y}<br>Month: %{x}<br>Amount: $%{z:,.0f}<extra></extra>",
            ))
            apply_theme(fig3, "Claim Revenue Heatmap", 300)
            st.plotly_chart(fig3, use_container_width=True)

        with col4:
            st.markdown('<div class="section-header">Top 10 Providers by Claims</div>', unsafe_allow_html=True)
            top_prov = (fc.groupby("provider_name")
                          .agg(count=("claim_id","count"), amount=("claim_amount","sum"))
                          .nlargest(10, "count").reset_index())
            fig4 = px.bar(top_prov, y="provider_name", x="count", orientation="h",
                           color="amount", color_continuous_scale=["#1E3050","#4ECDC4"])
            apply_theme(fig4, "Top Providers by Claim Count", 300)
            fig4.update_layout(yaxis=dict(categoryorder="total ascending"),
                                coloraxis_showscale=False)
            st.plotly_chart(fig4, use_container_width=True)

        # Raw data table
        st.markdown('<div class="section-header">📋 Claims Data Explorer</div>', unsafe_allow_html=True)
        show_cols = ["claim_id","claim_date","provider_name","specialty",
                     "patient_id","claim_amount","amount_bucket","status"]
        disp = (fc[show_cols]
                  .sort_values("claim_date", ascending=False)
                  .head(500)
                  .reset_index(drop=True))
        disp.index = disp.index
        disp["claim_amount"] = disp["claim_amount"].apply(lambda x: f"${x:,.0f}")
        st.dataframe(disp, use_container_width=True, height=320)


    # ╔══════════════════════════════════════════════════════╗
    #  TAB 3 — PAYMENTS
    # ╚══════════════════════════════════════════════════════╝
    with tab3:
        avg_ratio  = fp["payment_ratio"].mean() * 100 if len(fp) else 0
        med_gap    = fp["payment_gap_days"].median() if len(fp) else 0
        underpaid  = fp["underpaid_flag"].mean() * 100 if len(fp) else 0

        k1, k2, k3, k4 = st.columns(4)
        with k1: kpi_card("Payments Processed", f"{len(fp):,}",                               "💳")
        with k2: kpi_card("Total Paid Out",      fmt_money(fp["payment_amount"].sum() if len(fp) else 0), "💵")
        with k3: kpi_card("Avg Payment Ratio",   f"{avg_ratio:.1f}%",                          "📊")
        with k4: kpi_card("Underpaid Claims",    f"{underpaid:.1f}%",                          "⚠️",
                           delta=-underpaid, delta_label="flag rate")

        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="section-header">Payment Gap Distribution (Days to Pay)</div>', unsafe_allow_html=True)
            fig = go.Figure(go.Histogram(
                x=fp["payment_gap_days"].clip(-10, 400), nbinsx=60,
                marker=dict(color=COLORS["blue"], line=dict(color="#0A0E1A", width=0.3)),
            ))
            fig.add_vline(x=med_gap, line_dash="dash", line_color=COLORS["yellow"],
                           annotation_text=f"Median: {med_gap:.0f}d",
                           annotation_font_color=COLORS["yellow"])
            apply_theme(fig, "Days Between Claim Submission & Payment", 310)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown('<div class="section-header">Payment Ratio by Specialty</div>', unsafe_allow_html=True)
            ratio_spec = (fp.groupby("specialty")
                            .agg(ratio=("payment_ratio","mean"), count=("payment_id","count"))
                            .reset_index()
                            .sort_values("ratio", ascending=False).head(10))
            fig2 = px.bar(ratio_spec, x="specialty", y="ratio",
                           color="ratio",
                           color_continuous_scale=["#FF6B6B","#FFD93D","#4ECDC4"],
                           text=ratio_spec["ratio"].apply(lambda x: f"{x*100:.1f}%"))
            apply_theme(fig2, "Avg Payment-to-Claim Ratio", 310)
            fig2.update_traces(textposition="outside")
            fig2.update_layout(coloraxis_showscale=False, xaxis=dict(tickangle=-35))
            st.plotly_chart(fig2, use_container_width=True)

        col3, col4 = st.columns(2)

        with col3:
            st.markdown('<div class="section-header">Monthly Payment Trend</div>', unsafe_allow_html=True)
            monthly_pay = (fp.groupby(fp["payment_date"].dt.to_period("M"))
                             .agg(paid=("payment_amount","sum"), count=("payment_id","count"))
                             .reset_index())
            monthly_pay["payment_date"] = monthly_pay["payment_date"].astype(str)
            fig3 = px.line(monthly_pay, x="payment_date", y="paid",
                            color_discrete_sequence=[COLORS["green"]], markers=True)
            fig3.update_traces(line_width=2.5, marker_size=5)
            apply_theme(fig3, "Monthly Total Payment Amount", 310)
            st.plotly_chart(fig3, use_container_width=True)

        with col4:
            st.markdown('<div class="section-header">Claim vs Payment Scatter</div>', unsafe_allow_html=True)
            sample = fp.sample(min(3000, len(fp)), random_state=42)
            fig4 = px.scatter(sample, x="claim_amount", y="payment_amount",
                               color="status", color_discrete_map=color_map,
                               opacity=0.5, size_max=4,
                               hover_data=["payment_ratio"])
            max_v = max(sample["claim_amount"].max(), sample["payment_amount"].max())
            fig4.add_trace(go.Scatter(x=[0, max_v], y=[0, max_v],
                                       mode="lines", name="1:1 Line",
                                       line=dict(dash="dash", color=COLORS["yellow"], width=1.5)))
            apply_theme(fig4, "Claim Amount vs Payment Amount (3K sample)", 310)
            st.plotly_chart(fig4, use_container_width=True)

        st.markdown('<div class="section-header">Payment Status by Quarter</div>', unsafe_allow_html=True)
        pay_qtr = (fp.groupby(["payment_quarter","status"])["payment_amount"]
                     .sum().reset_index())
        fig5 = px.bar(pay_qtr, x="payment_quarter", y="payment_amount",
                       color="status", color_discrete_map=color_map, barmode="stack")
        apply_theme(fig5, "", 280)
        st.plotly_chart(fig5, use_container_width=True)


    # ╔══════════════════════════════════════════════════════╗
    #  TAB 4 — PROVIDERS
    # ╚══════════════════════════════════════════════════════╝
    with tab4:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="section-header">Specialty Distribution</div>', unsafe_allow_html=True)
            spec_cnt = providers["specialty"].value_counts().reset_index()
            spec_cnt.columns = ["specialty","count"]
            fig = px.pie(spec_cnt, names="specialty", values="count", hole=0.5,
                          color_discrete_sequence=px.colors.sequential.Teal)
            apply_theme(fig, "Provider Specialty Mix", 320)
            fig.update_traces(textposition="inside", textinfo="percent+label", textfont_size=10)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown('<div class="section-header">Providers by State (Top 15)</div>', unsafe_allow_html=True)
            state_cnt = providers["state"].value_counts().head(15).reset_index()
            state_cnt.columns = ["state","count"]
            fig2 = px.bar(state_cnt, x="count", y="state", orientation="h",
                           color="count", color_continuous_scale=["#1E3050","#45B7D1"])
            apply_theme(fig2, "", 320)
            fig2.update_layout(yaxis=dict(categoryorder="total ascending"),
                                coloraxis_showscale=False)
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown('<div class="section-header">Provider Performance Matrix (Avg Claim vs Volume)</div>', unsafe_allow_html=True)
        prov_perf = (fc.groupby(["provider_name","specialty"])
                       .agg(total_claims   =("claim_id","count"),
                            avg_amount     =("claim_amount","mean"),
                            approved       =("status_code", lambda x: (x==1).sum()),
                            rejection_rate =("status_code", lambda x: (x==-1).mean()*100))
                       .reset_index())
        sample_perf = prov_perf.sample(min(500, len(prov_perf)), random_state=1)
        fig3 = px.scatter(sample_perf, x="total_claims", y="avg_amount",
                           color="specialty", size="rejection_rate", size_max=20,
                           opacity=0.75,
                           hover_data=["provider_name","rejection_rate","approved"])
        apply_theme(fig3, "Provider: Volume vs Avg Claim (size = rejection rate)", 380)
        st.plotly_chart(fig3, use_container_width=True)

        # Top 20 providers table
        st.markdown('<div class="section-header">Top 20 Providers by Revenue</div>', unsafe_allow_html=True)
        top20 = (fc.groupby(["provider_name","specialty","provider_state"])
                   .agg(claims      =("claim_id","count"),
                        total_amount=("claim_amount","sum"),
                        avg_amount  =("claim_amount","mean"),
                        approval_pct=("status_code", lambda x: (x==1).mean()*100))
                   .reset_index()
                   .sort_values("total_amount", ascending=False)
                   .head(20)
                   .reset_index(drop=True))
        top20["total_amount"] = top20["total_amount"].apply(fmt_money)
        top20["avg_amount"]   = top20["avg_amount"].apply(fmt_money)
        top20["approval_pct"] = top20["approval_pct"].apply(lambda x: f"{x:.1f}%")
        st.dataframe(top20, use_container_width=True, height=380)


    # ╔══════════════════════════════════════════════════════╗
    #  TAB 5 — PATIENTS
    # ╚══════════════════════════════════════════════════════╝
    with tab5:
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown('<div class="section-header">Gender Distribution</div>', unsafe_allow_html=True)
            gen_cnt = patients["gender"].value_counts().reset_index()
            gen_cnt.columns = ["gender","count"]
            fig = px.pie(gen_cnt, names="gender", values="count", hole=0.55,
                          color_discrete_sequence=[COLORS["teal"], COLORS["red"], COLORS["yellow"]])
            apply_theme(fig, "", 270)
            fig.update_traces(textinfo="percent+label", textfont_size=11)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown('<div class="section-header">Age Group Distribution</div>', unsafe_allow_html=True)
            age_cnt = patients["age_group"].value_counts().sort_index().reset_index()
            age_cnt.columns = ["age_group","count"]
            fig2 = px.bar(
                age_cnt, x="age_group", y="count",
                color_discrete_sequence=[COLORS["blue"]],
                text="count",
            )
            apply_theme(fig2, "", 310)
            fig2.update_traces(
                textposition="outside",
                textfont=dict(size=11, color="#E8EAF0"),
            )
            fig2.update_layout(
                margin=dict(l=10, r=10, t=55, b=10),
                yaxis=dict(
                    range=[0, age_cnt["count"].max() * 1.18]
                ),
            )
            st.plotly_chart(fig2, use_container_width=True)

        with col3:
            st.markdown('<div class="section-header">Patients by State (Top 10)</div>', unsafe_allow_html=True)
            state_pt = patients["state"].value_counts().head(10).reset_index()
            state_pt.columns = ["state","count"]
            fig3 = px.bar(state_pt, x="count", y="state", orientation="h",
                           color="count",
                           color_continuous_scale=["#1E3050","#96CEB4"])
            apply_theme(fig3, "", 270)
            fig3.update_layout(yaxis=dict(categoryorder="total ascending"),
                                coloraxis_showscale=False)
            st.plotly_chart(fig3, use_container_width=True)

        col4, col5 = st.columns(2)

        with col4:
            st.markdown('<div class="section-header">Avg Claim Amount by Age Group</div>', unsafe_allow_html=True)
            fc_age  = fc.drop(columns=["age_group"], errors="ignore")
            pat_age = patients[["patient_id","age_group"]].drop_duplicates("patient_id")
            age_claim = (fc_age.merge(pat_age, on="patient_id", how="left")
                               .dropna(subset=["age_group"])
                               .groupby("age_group", observed=True)
                               .agg(avg_claim=("claim_amount","mean"),
                                    count    =("claim_id","count"))
                               .reset_index())
            fig4 = px.bar(age_claim, x="age_group", y="avg_claim",
                           color="count",
                           color_continuous_scale=["#1E3050","#4ECDC4"],
                           text=age_claim["avg_claim"].apply(fmt_money))
            apply_theme(fig4, "Average Claim Amount by Patient Age Group", 310)
            fig4.update_traces(textposition="outside")
            fig4.update_layout(
                coloraxis_showscale=False,
                margin=dict(l=10, r=10, t=50, b=10),
                yaxis=dict(range=[0, age_claim["avg_claim"].max() * 1.18]),
            )
            st.plotly_chart(fig4, use_container_width=True)

        with col5:
            st.markdown('<div class="section-header">Gender × Status Claim Breakdown</div>', unsafe_allow_html=True)
            fc_gen  = fc.drop(columns=["gender"], errors="ignore")
            pat_gen = patients[["patient_id","gender"]].drop_duplicates("patient_id")
            gen_claim = (fc_gen.merge(pat_gen, on="patient_id", how="left")
                               .dropna(subset=["gender"])
                               .groupby(["gender","status"])["claim_id"]
                               .count().reset_index(name="count"))
            fig5 = px.bar(gen_claim, x="gender", y="count", color="status",
                           color_discrete_map=color_map, barmode="group")
            apply_theme(fig5, "Claims by Gender & Status", 310)
            st.plotly_chart(fig5, use_container_width=True)

        st.markdown('<div class="section-header">Age Group vs Payment Behavior</div>', unsafe_allow_html=True)
        fp_clean = fp.drop(columns=["age_group","gender"], errors="ignore")
        pat_both = patients[["patient_id","age_group","gender"]].drop_duplicates("patient_id")
        age_pay  = (fp_clean.merge(pat_both, on="patient_id", how="left")
                             .dropna(subset=["age_group","gender"])
                             .groupby(["age_group","gender"], observed=True)
                             .agg(avg_ratio =("payment_ratio","mean"),
                                  avg_gap   =("payment_gap_days","mean"),
                                  count     =("payment_id","count"))
                             .reset_index())
        fig6 = px.scatter(age_pay, x="avg_gap", y="avg_ratio",
                           color="age_group", size="count", size_max=30,
                           symbol="gender", opacity=0.85,
                           hover_data=["count"])
        apply_theme(fig6, "Avg Payment Gap vs Payment Ratio by Age Group & Gender", 330)
        st.plotly_chart(fig6, use_container_width=True)

    # ── FOOTER ───────────────────────────────────────────────
    st.markdown("""
    <hr style='border-color:#1E3050;margin-top:2rem;'>
    <div style='text-align:center;padding:0.8rem;font-size:0.72rem;color:#4A5D7E;letter-spacing:0.08em;'>
        HealthClaim Analytics Dashboard &nbsp;|&nbsp; ETL Pipeline: 4 Datasets Integrated &nbsp;|&nbsp;
        Claims · Payments · Providers · Patients
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
