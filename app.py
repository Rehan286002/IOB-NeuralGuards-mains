import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import time
import random

st.set_page_config(
    page_title="IOB NeuralGuard | SOC",
    layout="wide",
    page_icon="https://www.iob.in/favicon.ico"
)

# ─────────────────────────────────────────────────────────────────────
# USERS DATABASE (demo — in production this would be PostgreSQL)
# ─────────────────────────────────────────────────────────────────────
if "users_db" not in st.session_state:
    st.session_state.users_db = {
        "admin":   {"password": "iob@2025",  "role": "SOC Administrator", "name": "Admin User"},
        "analyst": {"password": "neural123", "role": "Risk Analyst",       "name": "Risk Analyst"},
        "demo":    {"password": "demo",      "role": "Demo Access",        "name": "Demo User"},
    }

# ─────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────
for key, val in [
    ("authenticated", False),
    ("user", None),
    ("login_error", ""),
    ("signup_error", ""),
    ("signup_success", ""),
    ("show_password", False),
    ("show_signup_password", False),
    ("auth_tab", "login"),
]:
    if key not in st.session_state:
        st.session_state[key] = val

# ─────────────────────────────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');
*, html, body, [class*="css"] { font-family: 'Inter', sans-serif; box-sizing: border-box; }
.stApp { background-color: #0b0e13; }
.block-container { padding: 0 1.5rem 1rem 1.5rem !important; }

[data-testid="stSidebar"] { background-color: #0e1219 !important; border-right: 1px solid #1e2530 !important; }
[data-testid="stSidebar"] > div:first-child { padding-top: 0 !important; }

div[data-testid="stTextInput"] input {
    background: #111621 !important;
    border: 1px solid #1e2530 !important;
    border-radius: 4px !important;
    color: #e2e8f0 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.85rem !important;
    padding: 10px 14px !important;
}
div[data-testid="stTextInput"] input:focus {
    border-color: #1e3a5f !important;
    box-shadow: 0 0 0 2px rgba(30,58,95,0.25) !important;
}
div[data-testid="stTextInput"] label {
    color: #4a5568 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.66rem !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}
/* Tab styling */
div[data-testid="stTabs"] button {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: #4a5568 !important;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    color: #e2e8f0 !important;
    border-bottom-color: #0f3460 !important;
}
/* Buttons */
.stButton button {
    background: #0f3460 !important;
    color: #e2e8f0 !important;
    border: 1px solid #1e3a5f !important;
    border-radius: 4px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    width: 100% !important;
    padding: 10px !important;
}
.stButton button:hover { background: #1a4a80 !important; border-color: #3b82f6 !important; }

/* Signout button smaller */
.signout-btn button {
    background: transparent !important;
    border: 1px solid #1e2530 !important;
    color: #4a5568 !important;
    font-size: 0.65rem !important;
    padding: 5px !important;
}
.signout-btn button:hover { border-color: #ef4444 !important; color: #ef4444 !important; }

/* Metrics */
div[data-testid="stMetric"] {
    background: #111621; border: 1px solid #1e2530;
    border-radius: 4px; padding: 12px 16px !important;
}
div[data-testid="stMetric"] label {
    color: #4a5568 !important; font-size: 0.68rem !important;
    font-family: 'JetBrains Mono', monospace !important;
    text-transform: uppercase; letter-spacing: 0.1em;
}
div[data-testid="stMetricValue"] {
    color: #e2e8f0 !important; font-family: 'JetBrains Mono', monospace !important;
    font-size: 1.55rem !important; font-weight: 500 !important;
}
div[data-testid="stMetricDelta"] { font-family: 'JetBrains Mono', monospace !important; font-size: 0.72rem !important; }
.stDataFrame { border: 1px solid #1e2530 !important; border-radius: 4px !important; }
iframe { border-radius: 4px; }
div[data-testid="stCaption"] p {
    font-family: 'JetBrains Mono', monospace; font-size: 0.65rem; color: #2d3748; letter-spacing: 0.04em;
}
#MainMenu, footer, header { visibility: hidden; }
div[data-testid="stCheckbox"] label {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.68rem !important;
    color: #4a5568 !important;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────
# LOGIN / SIGNUP PAGE
# ─────────────────────────────────────────────────────────────────────
def show_auth():
    _, col, _ = st.columns([1, 1.1, 1])
    with col:
        st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)

        # IOB Logo
        st.markdown("""
<div style="text-align:center; margin-bottom:28px;">
  <svg width="68" height="68" viewBox="0 0 68 68" xmlns="http://www.w3.org/2000/svg">
    <rect width="68" height="68" rx="12" fill="#0f3460"/>
    <rect width="68" height="68" rx="12" fill="url(#grad)" opacity="0.3"/>
    <defs>
      <linearGradient id="grad" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%" stop-color="#1a4a80"/>
        <stop offset="100%" stop-color="#0a1f40"/>
      </linearGradient>
    </defs>
    <text x="34" y="40" text-anchor="middle" font-family="Inter,sans-serif"
      font-weight="700" font-size="22" fill="#ffffff" letter-spacing="2">IOB</text>
    <rect x="14" y="50" width="40" height="3" rx="1.5" fill="#e8a020"/>
  </svg>
  <div style="color:#e2e8f0; font-size:1.2rem; font-weight:600; margin-top:12px; letter-spacing:0.01em;">
    NeuralGuard
  </div>
  <div style="color:#2d3748; font-size:0.6rem; font-family:'JetBrains Mono',monospace;
    letter-spacing:0.16em; text-transform:uppercase; margin-top:3px;">
    Indian Overseas Bank · Fraud Intelligence Platform
  </div>
</div>
""", unsafe_allow_html=True)

        # Card container
        st.markdown("""
<div style="background:#0e1219; border:1px solid #1e2530; border-top:2px solid #0f3460;
  border-radius:8px; padding:24px 24px 20px 24px;">
  <div style="font-family:'JetBrains Mono',monospace; font-size:0.6rem; color:#1e2d3d;
    text-transform:uppercase; letter-spacing:0.14em; margin-bottom:18px;
    padding-bottom:12px; border-bottom:1px solid #1a2230; text-align:center;">
    &#128274; Restricted Access — Authorised Personnel Only
  </div>
""", unsafe_allow_html=True)

        # Tabs: Sign In / Sign Up
        tab1, tab2 = st.tabs(["Sign In", "Sign Up"])

        # ── SIGN IN TAB ──
        with tab1:
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

            login_user = st.text_input("Username", key="login_user", placeholder="Enter username")

            # Password with eye toggle BELOW the field
            login_pass = st.text_input(
                "Password",
                type="default" if st.session_state.get("show_login_pw", False) else "password",
                key="login_pass",
                placeholder="Enter password"
            )
            show_pw = st.checkbox("👁  Show password", key="show_login_pw")

            if st.button("Sign In to NeuralGuard", key="login_btn"):
                if login_user in st.session_state.users_db:
                    if st.session_state.users_db[login_user]["password"] == login_pass:
                        st.session_state.authenticated = True
                        st.session_state.user = {
                            "username": login_user,
                            "name":     st.session_state.users_db[login_user]["name"],
                            "role":     st.session_state.users_db[login_user]["role"],
                        }
                        st.session_state.login_error = ""
                        st.rerun()
                    else:
                        st.session_state.login_error = "Incorrect password. Access denied."
                else:
                    st.session_state.login_error = "Username not found."

            if st.session_state.login_error:
                st.markdown(f"""
<div style="background:#0f0505; border:1px solid #7f1d1d; border-left:3px solid #dc2626;
  border-radius:3px; padding:8px 14px; margin-top:6px;">
  <span style="font-family:'JetBrains Mono',monospace; font-size:0.68rem; color:#ef4444;">
    &#9888; {st.session_state.login_error}
  </span>
</div>
""", unsafe_allow_html=True)

            # Demo credentials hint
            st.markdown("""
<div style="margin-top:18px; padding:10px 12px; background:#0b0e13;
  border:1px solid #1a2230; border-radius:4px;">
  <div style="font-family:'JetBrains Mono',monospace; font-size:0.58rem; color:#2d3748;
    text-transform:uppercase; letter-spacing:0.1em; margin-bottom:8px;">Demo Credentials</div>
  <div style="font-family:'JetBrains Mono',monospace; font-size:0.65rem; line-height:2;">
    <span style="color:#374151;">admin</span>
    <span style="color:#1e2530;"> / </span>
    <span style="color:#4a5568;">iob@2025</span>
    <span style="color:#1e2530; margin:0 8px;">·</span>
    <span style="color:#374151;">SOC Administrator</span><br>
    <span style="color:#374151;">analyst</span>
    <span style="color:#1e2530;"> / </span>
    <span style="color:#4a5568;">neural123</span>
    <span style="color:#1e2530; margin:0 8px;">·</span>
    <span style="color:#374151;">Risk Analyst</span><br>
    <span style="color:#374151;">demo</span>
    <span style="color:#1e2530;"> / </span>
    <span style="color:#4a5568;">demo</span>
    <span style="color:#1e2530; margin:0 8px;">·</span>
    <span style="color:#374151;">Demo Access</span>
  </div>
</div>
""", unsafe_allow_html=True)

        # ── SIGN UP TAB ──
        with tab2:
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

            new_name     = st.text_input("Full Name",        key="su_name",  placeholder="e.g. Rehan Ahmed")
            new_user     = st.text_input("Username",         key="su_user",  placeholder="Choose a username")
            new_role     = st.selectbox("Role", [
                "Risk Analyst", "SOC Operator", "Compliance Officer",
                "Branch Manager", "IT Security", "Demo Access"
            ], key="su_role")
            new_pass     = st.text_input(
                "Password",
                type="default" if st.session_state.get("show_su_pw", False) else "password",
                key="su_pass",
                placeholder="Min 6 characters"
            )
            new_pass2    = st.text_input(
                "Confirm Password",
                type="default" if st.session_state.get("show_su_pw", False) else "password",
                key="su_pass2",
                placeholder="Re-enter password"
            )
            st.checkbox("👁  Show password", key="show_su_pw")

            if st.button("Create Account", key="signup_btn"):
                if not new_name or not new_user or not new_pass:
                    st.session_state.signup_error = "All fields are required."
                    st.session_state.signup_success = ""
                elif len(new_pass) < 6:
                    st.session_state.signup_error = "Password must be at least 6 characters."
                    st.session_state.signup_success = ""
                elif new_pass != new_pass2:
                    st.session_state.signup_error = "Passwords do not match."
                    st.session_state.signup_success = ""
                elif new_user in st.session_state.users_db:
                    st.session_state.signup_error = f"Username '{new_user}' already exists."
                    st.session_state.signup_success = ""
                else:
                    st.session_state.users_db[new_user] = {
                        "password": new_pass,
                        "role":     new_role,
                        "name":     new_name,
                    }
                    st.session_state.signup_error = ""
                    st.session_state.signup_success = f"Account created. You can now sign in as '{new_user}'."

            if st.session_state.signup_error:
                st.markdown(f"""
<div style="background:#0f0505; border:1px solid #7f1d1d; border-left:3px solid #dc2626;
  border-radius:3px; padding:8px 14px; margin-top:6px;">
  <span style="font-family:'JetBrains Mono',monospace; font-size:0.68rem; color:#ef4444;">
    &#9888; {st.session_state.signup_error}
  </span>
</div>
""", unsafe_allow_html=True)

            if st.session_state.signup_success:
                st.markdown(f"""
<div style="background:#0b1a0e; border:1px solid #166534; border-left:3px solid #22c55e;
  border-radius:3px; padding:8px 14px; margin-top:6px;">
  <span style="font-family:'JetBrains Mono',monospace; font-size:0.68rem; color:#86efac;">
    &#10003; {st.session_state.signup_success}
  </span>
</div>
""", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        st.markdown("""
<div style="text-align:center; font-family:'JetBrains Mono',monospace; font-size:0.56rem; color:#1a2230; line-height:1.8;">
  RESTRICTED SYSTEM · UNAUTHORISED ACCESS IS A CRIMINAL OFFENCE<br>
  Indian Overseas Bank · Treasury &amp; Risk Division · Chennai HQ
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────
# MAIN DASHBOARD
# ─────────────────────────────────────────────────────────────────────
def show_dashboard():

    with st.sidebar:
        # Logo
        st.markdown("""
<div style="padding:18px 16px 14px 16px; border-bottom:1px solid #1e2530; margin-bottom:4px;">
  <div style="display:flex; align-items:center; gap:12px;">
    <svg width="40" height="40" viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg">
      <rect width="40" height="40" rx="6" fill="#0f3460"/>
      <text x="20" y="23" text-anchor="middle" font-family="Inter,sans-serif"
        font-weight="600" font-size="13" fill="#ffffff" letter-spacing="1.2">IOB</text>
      <rect x="6" y="29" width="28" height="2" rx="1" fill="#e8a020"/>
    </svg>
    <div>
      <div style="color:#e2e8f0; font-size:0.88rem; font-weight:600;">NeuralGuard</div>
      <div style="color:#3a7bd5; font-size:0.6rem; letter-spacing:0.14em; font-family:'JetBrains Mono',monospace; margin-top:2px;">FRAUD INTELLIGENCE v1.0</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

        # User info
        user = st.session_state.user
        initials = "".join([w[0].upper() for w in user['name'].split()][:2])
        st.markdown(f"""
<div style="padding:10px 16px 10px 16px; border-bottom:1px solid #1e2530; margin-bottom:4px;">
  <div style="display:flex; align-items:center; gap:10px;">
    <div style="width:30px; height:30px; border-radius:50%; background:#0f3460; border:1px solid #1e3a5f;
      display:flex; align-items:center; justify-content:center; flex-shrink:0;
      font-family:'JetBrains Mono',monospace; font-size:0.68rem; color:#93c5fd; font-weight:600;">
      {initials}
    </div>
    <div>
      <div style="font-size:0.78rem; color:#cbd5e1; font-weight:500;">{user['name']}</div>
      <div style="font-family:'JetBrains Mono',monospace; font-size:0.58rem; color:#374151; margin-top:1px;">{user['role']}</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

        # Sign out
        st.markdown("<div style='padding:6px 16px 4px 16px;'>", unsafe_allow_html=True)
        if st.button("Sign Out", key="signout"):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.login_error = ""
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        # Engine Status
        st.markdown("""
<div style="padding:10px 16px 6px 16px; margin-top:4px;">
  <div style="font-family:'JetBrains Mono',monospace; font-size:0.59rem; color:#374151;
    letter-spacing:0.14em; text-transform:uppercase; margin-bottom:8px;
    border-left:2px solid #1e3a5f; padding-left:6px;">Engine Status</div>
</div>
""", unsafe_allow_html=True)

        def engine_row(label, tag, bg, border, dot, text, tag_c):
            st.markdown(f"""
<div style="margin:0 16px 4px 16px; display:flex; align-items:center; gap:8px;
  padding:6px 10px; background:{bg}; border:1px solid {border}; border-radius:3px;">
  <div style="width:6px; height:6px; border-radius:50%; background:{dot}; flex-shrink:0;"></div>
  <span style="font-family:'JetBrains Mono',monospace; font-size:0.67rem; color:{text};">{label}</span>
  <span style="margin-left:auto; font-family:'JetBrains Mono',monospace; font-size:0.59rem; color:{tag_c};">{tag}</span>
</div>
""", unsafe_allow_html=True)

        engine_row("FastAPI Orchestrator",   ":8000",  "#0b1a0e","#1a3320","#22c55e","#86efac","#166534")
        engine_row("Apache Kafka",           "INGEST", "#0b1a0e","#1a3320","#22c55e","#86efac","#166534")
        engine_row("Redis Speed Gate",       "&lt;2ms","#0b1a0e","#1a3320","#22c55e","#86efac","#166534")
        engine_row("Mule Hunter (Neo4j)",    "ONLINE", "#0b1a0e","#1a3320","#22c55e","#86efac","#166534")
        engine_row("Voice Shield (Librosa)", "ONLINE", "#0b1a0e","#1a3320","#22c55e","#86efac","#166534")

        st.markdown("""
<div style="padding:10px 16px 6px 16px; margin-top:6px; border-top:1px solid #1e2530;">
  <div style="font-family:'JetBrains Mono',monospace; font-size:0.59rem; color:#374151;
    letter-spacing:0.14em; text-transform:uppercase; margin-bottom:8px;
    border-left:2px solid #78350f; padding-left:6px;">Active Rule Engines</div>
</div>
""", unsafe_allow_html=True)

        engine_row("Velocity Gate (Redis)",       "5/min",  "#12100a","#2a2310","#f59e0b","#fcd34d","#78350f")
        engine_row("Spectral Flatness (Librosa)", "123Pay", "#12100a","#2a2310","#f59e0b","#fcd34d","#78350f")
        engine_row("Star Topology (Neo4j)",       "RING",   "#12100a","#2a2310","#f59e0b","#fcd34d","#78350f")

        st.markdown("""
<div style="padding:10px 16px 6px 16px; margin-top:6px; border-top:1px solid #1e2530;">
  <div style="font-family:'JetBrains Mono',monospace; font-size:0.59rem; color:#374151;
    letter-spacing:0.14em; text-transform:uppercase; margin-bottom:10px;
    border-left:2px solid #1e3a5f; padding-left:6px;">Protected IOB Channels</div>
  <div style="font-family:'JetBrains Mono',monospace; font-size:0.64rem; color:#4b5563; line-height:2.1;">
    UPI / 123Pay &nbsp;&nbsp;&nbsp;(NPCI Gateway)<br>
    IOB Nanban &nbsp;&nbsp;&nbsp;&nbsp;(Mobile App)<br>
    IOB NetBanking &nbsp;(Retail + Corp)<br>
    ATM / POS &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(FSS Switch)<br>
    Branch Teller &nbsp;&nbsp;(Finacle Core)<br>
    NEFT / RTGS / IMPS
  </div>
</div>
""", unsafe_allow_html=True)

        st.markdown("""
<div style="margin:10px 16px 16px 16px; border-top:1px solid #1e2530; padding-top:10px;">
  <div style="display:flex; align-items:center; gap:8px; padding:8px 10px;
    background:#0b1a0e; border:1px solid #166534; border-radius:3px;">
    <div style="width:6px; height:6px; border-radius:50%; background:#22c55e; flex-shrink:0;"></div>
    <div>
      <div style="font-family:'JetBrains Mono',monospace; font-size:0.67rem; color:#86efac;">Fail-Open: ACTIVE</div>
      <div style="font-family:'JetBrains Mono',monospace; font-size:0.58rem; color:#166534; margin-top:2px;">
        Timeout &gt;200ms &#8594; auto ALLOW
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── HEADER ───────────────────────────────────────────────────────
    st.markdown("""
<div style="display:flex; align-items:center; gap:14px;
  padding:14px 0 12px 0; border-bottom:1px solid #1e2530; margin-bottom:14px;">
  <svg width="36" height="36" viewBox="0 0 36 36" xmlns="http://www.w3.org/2000/svg">
    <rect width="36" height="36" rx="5" fill="#0f3460"/>
    <text x="18" y="21" text-anchor="middle" font-family="Inter,sans-serif"
      font-weight="600" font-size="11" fill="#ffffff" letter-spacing="1">IOB</text>
    <rect x="5" y="27" width="26" height="1.8" rx="0.9" fill="#e8a020"/>
  </svg>
  <div style="border-right:1px solid #1e2530; padding-right:14px;">
    <div style="font-size:0.78rem; font-weight:600; color:#cbd5e1;">Indian Overseas Bank</div>
    <div style="font-size:0.59rem; color:#374151; letter-spacing:0.1em;
      font-family:'JetBrains Mono',monospace; text-transform:uppercase; margin-top:2px;">
      Chennai HQ &nbsp;·&nbsp; Treasury &amp; Risk Division
    </div>
  </div>
  <div>
    <span style="font-size:1.25rem; font-weight:300; color:#94a3b8;">NeuralGuard</span>
    <span style="font-size:1.25rem; font-weight:300; color:#334155;"> — Active Threat Intelligence</span>
  </div>
  <div style="margin-left:auto; display:flex; align-items:center; gap:7px;
    padding:5px 12px; border:1px solid #166534; border-radius:3px; background:#0b1a0e;">
    <div style="width:5px; height:5px; border-radius:50%; background:#22c55e;"></div>
    <span style="font-family:'JetBrains Mono',monospace; font-size:0.65rem; color:#4ade80; letter-spacing:0.1em;">LIVE</span>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── DATA ─────────────────────────────────────────────────────────
    CHANNELS     = ['UPI / 123Pay','IOB Nanban','IOB NetBanking','ATM (FSS Switch)','Branch (Finacle)','NEFT / RTGS / IMPS']
    THREAT_TYPES = ['None','Mule Ring','Velocity Spike','Voice Deepfake','Account Takeover']
    ENGINES      = ['Velocity Gate (Redis)','Mule Hunter (Neo4j)','Voice Shield (Librosa)','AI Router (Llama 3)']

    def gen(n=120):
        now = pd.Timestamp.now()
        channels     = np.random.choice(CHANNELS, n, p=[0.35,0.20,0.15,0.15,0.05,0.10])
        amounts      = np.random.randint(500, 200000, n)
        risk_scores  = np.random.randint(10, 100, n)
        threat_types = np.random.choice(THREAT_TYPES, n, p=[0.76,0.08,0.07,0.05,0.04])
        engines      = np.random.choice(ENGINES, n, p=[0.5,0.25,0.15,0.10])
        latencies    = np.random.randint(18, 185, n)
        accts        = [f"IOB{random.randint(10000000000,99999999999)}" for _ in range(n)]
        statuses = []
        for i in range(n):
          r, t, a = risk_scores[i], threat_types[i], amounts[i]
          # Stricter logic: lower thresholds
          if t != "None":
            statuses.append("BLOCKED")
          else:
            statuses.append("ALLOWED")
        return pd.DataFrame({
            "Timestamp":   pd.date_range(end=now, periods=n, freq="30S"),
            "Channel":     channels,
            "Amount_INR":  amounts,
            "Risk_Score":  risk_scores,
            "Status":      statuses,
            "Threat_Type": threat_types,
            "Latency_ms":  latencies,
            "Sender_Acct": accts,
            "Engine":      engines,
        })

    def chart_layout(**extra):
        base = dict(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='#0e1219',
            font=dict(family="JetBrains Mono", color="#4b5563", size=10),
            margin=dict(l=0, r=0, t=10, b=0),
            xaxis=dict(gridcolor='#1e2530', linecolor='#1e2530', tickfont=dict(size=9)),
            yaxis=dict(gridcolor='#1e2530', linecolor='#1e2530', tickfont=dict(size=9)),
        )
        base.update(extra)
        return base

    def section(label):
        st.markdown(f"""
<div style="font-family:'JetBrains Mono',monospace; font-size:0.62rem; color:#374151;
  text-transform:uppercase; letter-spacing:0.14em; margin-bottom:8px;
  padding-left:8px; border-left:2px solid #1e3a5f;">{label}</div>
""", unsafe_allow_html=True)

    placeholder = st.empty()

    while True:
        df      = gen()
        blocked = df[df['Status'] == 'BLOCKED']
        tps     = random.randint(1100, 1400)
        avg_lat = int(df['Latency_ms'].mean())

        with placeholder.container():

            # KPIs
            k1,k2,k3,k4,k5 = st.columns(5)
            k1.metric("Live TPS",             f"{tps:,}",          delta=f"{random.randint(-30,60)}")
            k2.metric("Engine Latency",       f"{avg_lat} ms",     delta=f"{random.randint(-8,8)} ms",  delta_color="inverse")
            k3.metric("Threats Blocked (2H)", len(blocked),        delta=f"+{random.randint(1,4)}",     delta_color="inverse")
            k4.metric("Mule Rings Detected",  random.randint(2,5), delta="+1",                          delta_color="inverse")
            k5.metric("Fail-Open Triggers",   "0",                 delta="0")

            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

            # Charts
            c1,c2,c3 = st.columns([2.2,1.4,1.4])

            with c1:
                section("IOB Omni-Channel Traffic vs. Threat Interceptions")
                ch = df.groupby(['Channel','Status']).size().reset_index(name='Count')
                fig1 = px.bar(ch, x="Channel", y="Count", color="Status",
                    color_discrete_map={"ALLOWED":"#1f6b45","BLOCKED":"#991b1b"},
                    template="plotly_dark", barmode="group")
                fig1.update_layout(**chart_layout(legend=dict(orientation="h", y=1.1, font=dict(size=9))))
                fig1.update_traces(marker_line_width=0)
                st.plotly_chart(fig1, use_container_width=True)

            with c2:
                section("Threat Vector Distribution")
                threats = df[df['Threat_Type'] != 'None']
                fig2 = px.pie(threats, names='Threat_Type', hole=0.6,
                    color_discrete_sequence=['#7f1d1d','#78350f','#1e3a5f','#3b1e63'],
                    template="plotly_dark")
                fig2.update_traces(
                    textposition='inside', textinfo='percent+label',
                    textfont=dict(size=8, color="#9ca3af"),
                    marker=dict(line=dict(color='#0e1219', width=2)))
                fig2.update_layout(**chart_layout(showlegend=False,
                    annotations=[dict(text=f"<b>{len(threats)}</b><br>alerts",
                        x=0.5, y=0.5, showarrow=False,
                        font=dict(color="#6b7280", family="JetBrains Mono", size=10))]))
                st.plotly_chart(fig2, use_container_width=True)

            with c3:
                section("Risk Score Distribution")
                fig3 = go.Figure()
                fig3.add_trace(go.Histogram(x=df[df['Status']=='BLOCKED']['Risk_Score'],
                    name='Blocked', marker_color='#7f1d1d', opacity=0.9, nbinsx=15))
                fig3.add_trace(go.Histogram(x=df[df['Status']=='ALLOWED']['Risk_Score'],
                    name='Allowed', marker_color='#1f6b45', opacity=0.5, nbinsx=15))
                fig3.update_layout(**chart_layout(barmode='overlay',
                    legend=dict(orientation="h", y=1.1, font=dict(size=9)),
                    xaxis=dict(title=dict(text="Risk Score", font=dict(size=9)), gridcolor='#1e2530', tickfont=dict(size=9)),
                    yaxis=dict(title=dict(text="Count",      font=dict(size=9)), gridcolor='#1e2530', tickfont=dict(size=9))))
                fig3.update_traces(marker_line_width=0)
                st.plotly_chart(fig3, use_container_width=True)

            # Alert banner
            st.markdown("""
<div style="display:flex; align-items:center; gap:16px; background:#0f0505;
  border:1px solid #7f1d1d; border-left:3px solid #dc2626; border-radius:3px;
  padding:10px 16px; margin-bottom:10px;">
  <div style="flex-shrink:0;">
    <div style="font-family:'JetBrains Mono',monospace; font-size:0.62rem;
      color:#ef4444; letter-spacing:0.1em; text-transform:uppercase; font-weight:600;">
      &#9888;&nbsp; Critical &mdash; Mule Ring Active
    </div>
    <div style="font-family:'Inter',sans-serif; font-size:0.8rem; color:#9ca3af; margin-top:4px;">
      Hub account&nbsp;
      <code style="background:#1e1010; padding:1px 5px; border-radius:2px;
        color:#fca5a5; font-family:'JetBrains Mono',monospace; font-size:0.75rem;">IOB98412XXXXXX</code>
      &nbsp;funnelling into 7 satellite accounts &nbsp;&middot;&nbsp;
      <span style="color:#d97706;">Mule Hunter (Neo4j)</span> confirmed Star Topology
      &nbsp;&middot;&nbsp; SAR auto-drafted for RBI
    </div>
  </div>
  <div style="margin-left:auto; text-align:right; white-space:nowrap; flex-shrink:0;">
    <div style="font-family:'JetBrains Mono',monospace; font-size:0.65rem; color:#374151;">Decision: 47ms</div>
    <div style="font-family:'JetBrains Mono',monospace; font-size:0.65rem; color:#166534; margin-top:2px;">Fail-Open: Safe</div>
  </div>
</div>
""", unsafe_allow_html=True)

            # Event log
            section("Live Interception Feed — IOB Payment Switch")

            recent = df.sort_values('Timestamp', ascending=False).head(15)[[
                'Timestamp','Channel','Sender_Acct','Amount_INR',
                'Risk_Score','Engine','Threat_Type','Status','Latency_ms'
            ]].copy()
            recent['Timestamp']  = recent['Timestamp'].dt.strftime('%H:%M:%S')
            recent['Amount_INR'] = recent['Amount_INR'].apply(lambda x: f"\u20b9{x:,}")
            recent['Latency_ms'] = recent['Latency_ms'].apply(lambda x: f"{x}ms")

            # 1. Custom CSS for High Contrast and Maximum Boldness
            st.markdown("""
            <style>
            .live-table { 
                width: 100%; 
                border-collapse: collapse; 
                font-family: 'JetBrains Mono', monospace; 
                font-size: 0.78rem; /* Slightly larger font */
                background: transparent !important; 
            }
            .live-table th { 
                background: #0e1219 !important; 
                color: #ffffff !important; 
                text-align: left; 
                padding: 12px 10px; 
                border-bottom: 2px solid #1e2530; 
                text-transform: uppercase; 
                font-weight: 800 !important; 
            }
            .live-table td { 
                padding: 12px 10px; 
                border-bottom: 1px solid #1e2530; 
                background: transparent !important; 
                color: #ffffff !important; /* Brighter white for ALL letters */
                font-weight: 700 !important; /* Bold for ALL letters */
            }
            /* Hover effect */
            .live-table tr:hover { background: rgba(255, 255, 255, 0.05) !important; }
            </style>
            """, unsafe_allow_html=True)

            # 2. Bold Logic with High-Impact Colors
            styled = recent.style \
                .applymap(lambda v: 'color:#22c55e; font-weight:900;' if v=='ALLOWED' else 'color:#ef4444; font-weight:900;', subset=['Status']) \
                .applymap(lambda v: 'color:#f59e0b; font-weight:900;' if v!='None' else 'color:#555555;', subset=['Threat_Type']) \
                .applymap(lambda _: 'color:#60a5fa; font-weight:800;', subset=['Engine']) \
                .applymap(lambda _: 'color:#ffffff; font-weight:800;', subset=['Amount_INR', 'Timestamp', 'Sender_Acct', 'Channel'])

            # 3. Render
            table_html = f'<div style="height:380px; overflow-y:auto;">{styled.to_html(classes="live-table", escape=False, index=False)}</div>'
            st.write(table_html, unsafe_allow_html=True)

            st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
            st.caption(
                f"IOB NeuralGuard v1.0  ·  Sidecar — Zero impact on Finacle Core  ·  "
                f"Air-Gapped · RBI Compliant  ·  All decisions <200ms  ·  "
                f"Signed in as {st.session_state.user['name']} ({st.session_state.user['role']})  ·  "
                f"Refresh {pd.Timestamp.now().strftime('%H:%M:%S')} IST"
            )

        time.sleep(4)


# ─────────────────────────────────────────────────────────────────────
# ROUTER
# ─────────────────────────────────────────────────────────────────────
if not st.session_state.authenticated:
    show_auth()
else:
    show_dashboard()