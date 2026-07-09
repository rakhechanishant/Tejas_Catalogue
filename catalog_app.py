
import streamlit as st
import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import os
import io
import base64
import time
import urllib.parse
from datetime import datetime

try:
    from st_keyup import st_keyup
    HAS_KEYUP = True
except ImportError:
    HAS_KEYUP = False



load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
APP_PASSWORD = os.getenv('APP_PASSWORD', 'TejasImpex@2026')
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_SECONDS = 60

st.set_page_config(
    page_title="TEJAS IMPEX — Product Catalog",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("❌ Supabase credentials not found. Check your .env file.")
    st.stop()

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'login_attempts' not in st.session_state:
    st.session_state.login_attempts = 0
if 'lockout_until' not in st.session_state:
    st.session_state.lockout_until = 0

def show_login():
    """Show branded login page with security limits."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap');
    * { font-family: 'Inter', sans-serif !important; }
    .stApp { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); }
    #MainMenu, header, footer { visibility: hidden; }
    .login-container {
        max-width: 420px; margin: 80px auto; padding: 40px;
        background: rgba(255,255,255,0.06); backdrop-filter: blur(20px);
        border-radius: 24px; border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    }
    .login-brand { text-align: center; margin-bottom: 32px; }
    .login-logo {
        font-size: 36px; font-weight: 900; color: #e94560;
        letter-spacing: 2px; margin-bottom: 4px;
    }
    .login-sub {
        font-size: 12px; color: rgba(255,255,255,0.35);
        letter-spacing: 3px; text-transform: uppercase;
    }
    .login-title {
        font-size: 22px; font-weight: 700; color: #fff;
        text-align: center; margin-bottom: 8px;
    }
    .login-desc {
        font-size: 13px; color: rgba(255,255,255,0.4);
        text-align: center; margin-bottom: 28px;
    }
    div[data-testid="stTextInput"] input {
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        color: #fff !important; border-radius: 12px !important;
        padding: 14px 18px !important; font-size: 15px !important;
    }
    div[data-testid="stTextInput"] input::placeholder { color: rgba(255,255,255,0.3) !important; }
    div[data-testid="stTextInput"] input:focus {
        border-color: #e94560 !important;
        box-shadow: 0 0 20px rgba(233,69,96,0.2) !important;
    }
    .stButton > button {
        width: 100%; background: linear-gradient(135deg, #e94560, #ff6b6b) !important;
        color: white !important; border: none !important; border-radius: 12px !important;
        padding: 14px !important; font-size: 16px !important; font-weight: 700 !important;
        letter-spacing: 1px !important; transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(233,69,96,0.4) !important;
    }
    .login-footer {
        text-align: center; margin-top: 24px;
        font-size: 11px; color: rgba(255,255,255,0.2);
    }
    .login-error {
        background: rgba(233,69,96,0.15); border: 1px solid rgba(233,69,96,0.3);
        border-radius: 10px; padding: 10px 16px; margin-top: 12px;
        color: #ff6b6b; font-size: 13px; text-align: center;
    }
    .login-locked {
        background: rgba(255,165,0,0.12); border: 1px solid rgba(255,165,0,0.25);
        border-radius: 10px; padding: 10px 16px; margin-top: 12px;
        color: #ffa500; font-size: 13px; text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="login-container">
        <div class="login-brand">
            <div class="login-logo">TEJAS IMPEX</div>
            <div class="login-sub">Product Catalog System</div>
        </div>
        <div class="login-title">Welcome Back</div>
        <div class="login-desc">Enter your team password to access the catalog</div>
    </div>
    """, unsafe_allow_html=True)

    # Check lockout
    now = time.time()
    if st.session_state.lockout_until > now:
        remaining = int(st.session_state.lockout_until - now)
        st.markdown(f"""
        <div style="max-width:420px;margin:0 auto;">
            <div class="login-locked">
                Account locked. Try again in {remaining}s
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    col_l, col_c, col_r = st.columns([1, 1.2, 1])
    with col_c:
        pwd = st.text_input("Password", type="password",
                           placeholder="Enter team password",
                           label_visibility="collapsed")
        if st.button("ACCESS CATALOG", use_container_width=True):
            if pwd == APP_PASSWORD:
                st.session_state.authenticated = True
                st.session_state.login_attempts = 0
                st.rerun()
            else:
                st.session_state.login_attempts += 1
                remaining_attempts = MAX_LOGIN_ATTEMPTS - st.session_state.login_attempts
                if remaining_attempts <= 0:
                    st.session_state.lockout_until = time.time() + LOCKOUT_SECONDS
                    st.session_state.login_attempts = 0
                    st.markdown("""
                    <div style="max-width:420px;margin:0 auto;">
                        <div class="login-locked">Too many attempts. Locked for 60 seconds.</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="max-width:420px;margin:0 auto;">
                        <div class="login-error">Incorrect password. {remaining_attempts} attempts remaining.</div>
                    </div>
                    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="login-footer">
        © 2026 TEJAS IMPEX PVT. LTD. — Authorized Access Only
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# Gate: show login if not authenticated
if not st.session_state.authenticated:
    show_login()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ── Global ── */
* { font-family: 'Inter', sans-serif !important; }

.stApp {
    background: linear-gradient(135deg, #f0f2f5 0%, #e8ecf1 50%, #f5f0f0 100%);
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1a2e 0%, #16213e 40%, #0f3460 100%);
    border-right: none;
}

[data-testid="stSidebar"] * {
    color: #e0e0e0 !important;
}

[data-testid="stSidebar"] input {
    color: #ffffff !important;
    background: rgba(255,255,255,0.1) !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
}

[data-testid="stSidebar"] input::placeholder {
    color: rgba(255,255,255,0.45) !important;
}

[data-testid="stSidebar"] label {
    color: #a0aec0 !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
}

[data-testid="stSidebar"] .stSelectbox > div > div {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 10px !important;
    color: #fff !important;
}

[data-testid="stSidebar"] .stSlider > div > div > div {
    background: #e94560 !important;
}

[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.08) !important;
}

/* ── Main Page Inputs & Dropdowns styling ── */
div[data-testid="stSelectbox"] label, div[data-testid="stSlider"] label {
    font-size: 11px !important;
    font-weight: 700 !important;
    color: #4a5568 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
    margin-bottom: 6px !important;
}

div[data-testid="stSelectbox"] > div > div {
    background: white !important;
    border: 2px solid #e8ecf1 !important;
    border-radius: 14px !important;
    color: #1a1a2e !important;
    min-height: 44px !important;
    box-shadow: 0 2px 10px rgba(0,0,0,0.04) !important;
    transition: all 0.3s ease !important;
}

div[data-testid="stSelectbox"] > div > div:hover {
    border-color: #e94560 !important;
}

div[data-testid="stSelectbox"] * {
    color: #1a1a2e !important;
}

div[data-testid="stTextInput"] input {
    background: white !important;
    border: 2px solid #e8ecf1 !important;
    border-radius: 14px !important;
    color: #1a1a2e !important;
    min-height: 44px !important;
    box-shadow: 0 2px 10px rgba(0,0,0,0.04) !important;
    transition: all 0.3s ease !important;
}

div[data-testid="stTextInput"] input:focus {
    border-color: #e94560 !important;
    box-shadow: 0 2px 12px rgba(233, 69, 96, 0.15) !important;
}

/* ── Header Banner ── */
.hero-banner {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    border-radius: 20px;
    padding: 32px 40px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 10px 40px rgba(26, 26, 46, 0.25);
}

.hero-banner::before {
    content: '';
    position: absolute;
    top: -60%;
    right: -10%;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(233,69,96,0.15) 0%, transparent 70%);
    border-radius: 50%;
}

.hero-banner::after {
    content: '';
    position: absolute;
    bottom: -50%;
    left: 20%;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(15,52,96,0.3) 0%, transparent 70%);
    border-radius: 50%;
}

.hero-content {
    position: relative;
    z-index: 2;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.hero-left { display: flex; align-items: center; gap: 20px; }

.hero-logo {
    background: linear-gradient(135deg, #e94560, #ff6b6b);
    color: white;
    font-size: 28px;
    font-weight: 900;
    padding: 14px 22px;
    border-radius: 16px;
    letter-spacing: 1px;
    box-shadow: 0 8px 25px rgba(233,69,96,0.35);
}

.hero-title {
    font-size: 28px;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: 0.5px;
}

.hero-sub {
    font-size: 14px;
    color: rgba(255,255,255,0.55);
    font-weight: 400;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: 4px;
}

.hero-stats {
    display: flex;
    gap: 30px;
    text-align: center;
}

.hero-stat-value {
    font-size: 32px;
    font-weight: 800;
    color: #ffffff;
    line-height: 1;
}

.hero-stat-label {
    font-size: 11px;
    color: rgba(255,255,255,0.45);
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-weight: 600;
    margin-top: 6px;
}

.hero-stat-divider {
    width: 1px;
    background: rgba(255,255,255,0.12);
    align-self: stretch;
}

/* ── Search Results Bar ── */
.results-bar {
    background: white;
    border-radius: 14px;
    padding: 14px 24px;
    margin-bottom: 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 2px 12px rgba(0,0,0,0.04);
    border: 1px solid rgba(0,0,0,0.04);
}

.results-text {
    font-size: 15px;
    color: #6c757d;
    font-weight: 500;
}

.results-text strong {
    color: #1a1a2e;
    font-weight: 700;
}

.results-accent {
    color: #e94560;
    font-weight: 700;
}

.sort-info {
    font-size: 13px;
    color: #a0aec0;
}

/* ── Animations ── */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(30px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes slideInPage {
    from { opacity: 0; transform: translateX(20px); }
    to { opacity: 1; transform: translateX(0); }
}

@keyframes pulseGlow {
    0% { box-shadow: 0 4px 20px rgba(0,0,0,0.06); }
    50% { box-shadow: 0 8px 35px rgba(233,69,96,0.12); }
    100% { box-shadow: 0 4px 20px rgba(0,0,0,0.06); }
}

@keyframes shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}

@keyframes heroFloat {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-8px); }
}

.stMain > div { animation: slideInPage 0.5s ease-out; }

/* ── Product Card ── */
.product-card {
    background: rgba(255,255,255,0.9);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-radius: 18px;
    padding: 0;
    box-shadow: 0 4px 20px rgba(0,0,0,0.06);
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    border: 1px solid rgba(255,255,255,0.6);
    overflow: hidden;
    height: 100%;
    animation: fadeInUp 0.6s ease-out both;
}

.product-card:hover {
    transform: translateY(-10px) scale(1.02);
    box-shadow: 0 20px 60px rgba(233,69,96,0.18), 0 8px 24px rgba(0,0,0,0.1);
    border-color: rgba(233,69,96,0.35);
}

.card-image-wrap {
    width: 100%;
    height: 200px;
    background: linear-gradient(135deg, #f8f9fa, #f0f2f5);
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    position: relative;
}

.card-image-wrap img {
    max-width: 90%;
    max-height: 90%;
    object-fit: contain;
    transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1), filter 0.4s ease;
}

.product-card:hover .card-image-wrap img {
    transform: scale(1.12) rotate(1deg);
    filter: brightness(1.05);
}

.product-card:hover .card-image-wrap {
    background: linear-gradient(135deg, #fff5f5, #f0f0ff);
}

.card-brand-ribbon {
    position: absolute;
    top: 12px;
    left: 0;
    background: linear-gradient(135deg, #e94560, #ff6b6b);
    color: white;
    font-size: 10px;
    font-weight: 700;
    padding: 4px 14px 4px 10px;
    letter-spacing: 1px;
    text-transform: uppercase;
    border-radius: 0 20px 20px 0;
}

.card-body {
    padding: 16px 18px 18px 18px;
}

.card-ref {
    font-size: 12px;
    font-weight: 600;
    color: #a0aec0;
    letter-spacing: 0.5px;
    margin-bottom: 4px;
}

.card-name {
    font-size: 15px;
    font-weight: 700;
    color: #1a1a2e;
    line-height: 1.4;
    margin-bottom: 8px;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    min-height: 42px;
}

.card-price {
    font-size: 24px;
    font-weight: 800;
    color: #1a1a2e;
    margin-bottom: 10px;
}

.card-price .currency {
    font-size: 14px;
    font-weight: 600;
    color: #6c757d;
    vertical-align: super;
    margin-right: 2px;
}

.card-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
    margin-bottom: 12px;
}

.chip {
    font-size: 10px;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 50px;
    display: inline-block;
    letter-spacing: 0.3px;
}

.chip-cat {
    background: linear-gradient(135deg, #fef0f2, #fce4ec);
    color: #e94560;
}

.chip-series {
    background: linear-gradient(135deg, #e8ecf1, #dce3ed);
    color: #0f3460;
}

.chip-sub {
    background: linear-gradient(135deg, #e8f5e9, #c8e6c9);
    color: #2e7d32;
}

.card-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 12px;
    border-top: 1px solid rgba(0,0,0,0.05);
}

.card-packing {
    font-size: 11px;
    color: #a0aec0;
    font-weight: 500;
}

.card-packing strong {
    color: #6c757d;
}

/* ── Detail Page ── */
.detail-hero {
    background: linear-gradient(135deg, #1a1a2e, #16213e, #0f3460);
    border-radius: 20px;
    padding: 36px 44px;
    margin-bottom: 28px;
    box-shadow: 0 10px 40px rgba(26,26,46,0.2);
}

.detail-breadcrumb {
    font-size: 13px;
    color: rgba(255,255,255,0.4);
    margin-bottom: 16px;
    font-weight: 500;
}

.detail-breadcrumb a {
    color: rgba(255,255,255,0.6);
    text-decoration: none;
}

.detail-title {
    font-size: 32px;
    font-weight: 800;
    color: #ffffff;
    margin-bottom: 6px;
}

.detail-ref {
    font-size: 16px;
    color: rgba(255,255,255,0.45);
    font-weight: 500;
}

.detail-image-container {
    background: white;
    border-radius: 18px;
    padding: 30px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.06);
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 400px;
    border: 1px solid rgba(0,0,0,0.04);
}

.detail-image-container img {
    max-width: 100%;
    max-height: 380px;
    object-fit: contain;
}

.detail-info-card {
    background: white;
    border-radius: 18px;
    padding: 28px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.06);
    border: 1px solid rgba(0,0,0,0.04);
    margin-bottom: 18px;
}

.detail-price {
    font-size: 38px;
    font-weight: 900;
    color: #1a1a2e;
    margin: 12px 0 20px 0;
}

.detail-price .cur {
    font-size: 20px;
    color: #6c757d;
    font-weight: 600;
}

.detail-meta-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    margin: 20px 0;
}

.detail-meta-box {
    background: linear-gradient(135deg, #f8f9fa, #f0f2f5);
    border-radius: 14px;
    padding: 16px;
    text-align: center;
    border: 1px solid rgba(0,0,0,0.04);
}

.detail-meta-num {
    font-size: 26px;
    font-weight: 800;
    color: #1a1a2e;
}

.detail-meta-lbl {
    font-size: 11px;
    font-weight: 700;
    color: #a0aec0;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 4px;
}

.detail-spec-card {
    background: white;
    border-radius: 18px;
    padding: 28px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.06);
    border: 1px solid rgba(0,0,0,0.04);
    animation: fadeInUp 0.6s ease-out 0.2s both;
}

.detail-spec-title {
    font-size: 18px;
    font-weight: 700;
    color: #1a1a2e;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 10px;
    padding-bottom: 12px;
    border-bottom: 2px solid #f0f2f5;
}

.detail-spec-content {
    background: linear-gradient(135deg, #f8f9fa, #f5f0f0);
    border-radius: 12px;
    padding: 0;
    font-size: 14px;
    line-height: 2;
    color: #2d3436;
    font-family: 'Inter', sans-serif !important;
    border: 1px solid rgba(0,0,0,0.04);
    overflow: hidden;
}

.spec-row {
    display: flex;
    padding: 12px 20px;
    border-bottom: 1px solid #f0f2f5;
    transition: background 0.2s ease;
}

.spec-row:last-child { border-bottom: none; }
.spec-row:hover { background: rgba(233,69,96,0.03); }

.spec-row:nth-child(even) { background: rgba(0,0,0,0.015); }
.spec-row:nth-child(even):hover { background: rgba(233,69,96,0.04); }

.spec-label {
    font-weight: 700;
    color: #1a1a2e;
    min-width: 180px;
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.spec-value {
    color: #4a5568;
    font-size: 14px;
    flex: 1;
}

.spec-plain {
    padding: 20px 24px;
    white-space: pre-wrap;
    font-size: 14px;
    line-height: 2;
    color: #2d3436;
}

.detail-badge-row {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-bottom: 14px;
}

.detail-chip {
    font-size: 12px;
    font-weight: 600;
    padding: 6px 16px;
    border-radius: 50px;
}

/* ── Pagination ── */
.pagination-container {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 6px;
    margin: 30px 0 10px 0;
}

/* ── Sidebar Stat Cards ── */
.sidebar-stat {
    background: rgba(255,255,255,0.06);
    border-radius: 12px;
    padding: 14px 16px;
    margin-bottom: 10px;
    border: 1px solid rgba(255,255,255,0.06);
}

.sidebar-stat-val {
    font-size: 24px;
    font-weight: 800;
    color: #e94560 !important;
}

.sidebar-stat-lbl {
    font-size: 11px;
    font-weight: 600;
    color: rgba(255,255,255,0.4) !important;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* ── Footer ── */
.app-footer {
    text-align: center;
    padding: 28px 20px 18px 20px;
    border-top: 1px solid rgba(0,0,0,0.06);
    margin-top: 40px;
}

.footer-brand {
    font-size: 16px;
    font-weight: 700;
    color: #1a1a2e;
    margin-bottom: 6px;
}

.footer-info {
    font-size: 13px;
    color: #8892b0;
    line-height: 1.8;
}

.footer-copy {
    font-size: 11px;
    color: #c0c0c0;
    margin-top: 10px;
}

/* ── Streamlit Overrides ── */
.stButton > button {
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1) !important;
    font-family: 'Inter', sans-serif !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(0,0,0,0.12) !important;
}

div[data-testid="stTextInput"] input {
    border-radius: 14px !important;
    border: 2px solid #e8ecf1 !important;
    padding: 12px 20px !important;
    font-size: 15px !important;
    color: #1a1a2e !important;
    transition: all 0.3s ease !important;
    background: white !important;
    box-shadow: 0 2px 10px rgba(0,0,0,0.04) !important;
}

div[data-testid="stTextInput"] input:focus {
    border-color: #e94560 !important;
    box-shadow: 0 4px 20px rgba(233,69,96,0.1) !important;
}

/* ── Logo in banner ── */
.hero-logo-img {
    height: 60px;
    border-radius: 12px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.2);
    transition: transform 0.4s ease;
    background: white;
    padding: 6px;
}

.hero-logo-img:hover {
    transform: scale(1.1);
}

.hero-logos {
    display: flex;
    gap: 14px;
    align-items: center;
}

/* Hide Streamlit elements */
#MainMenu { visibility: hidden; }
header { visibility: hidden; }
footer { visibility: hidden; }

/* ── No Image Placeholder ── */
.no-image-placeholder {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: #c0c0c0;
    font-size: 14px;
    gap: 8px;
}

.no-image-icon {
    font-size: 48px;
    opacity: 0.4;
}

/* ── WhatsApp Sharing Styles ── */
.whatsapp-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    width: 100%;
    background: linear-gradient(135deg, #25d366, #128c7e) !important;
    color: white !important;
    font-weight: 700;
    font-size: 14px;
    padding: 12px 20px;
    border-radius: 12px;
    border: none;
    cursor: pointer;
    box-shadow: 0 4px 15px rgba(37, 211, 102, 0.15);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    text-decoration: none;
    margin-top: 14px;
}
.whatsapp-btn:hover {
    transform: translateY(-2px) !important;
    color: white !important;
    box-shadow: 0 6px 22px rgba(37, 211, 102, 0.3) !important;
}

.card-wa-btn {
    background: #eafbee !important;
    color: #128c7e !important;
    border: 1px solid rgba(37, 211, 102, 0.2) !important;
    box-shadow: none !important;
    padding: 8px !important;
    font-size: 13px !important;
    margin-top: 8px !important;
}
.card-wa-btn:hover {
    background: #25d366 !important;
    color: white !important;
    box-shadow: 0 4px 12px rgba(37, 211, 102, 0.2) !important;
}
</style>
""", unsafe_allow_html=True)


defaults = {
    'view': 'catalog',       # 'catalog' or 'detail'
    'selected_product': None,
    'page': 1,
    'search_term': '',
    'category': 'All',
    'sub_category': 'All',
    'company': 'All',
    'series': 'All',
    'sort_by': 'Name A→Z',
    'price_range': (0, 100000),
}

for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val


@st.cache_data(ttl=300)
def load_products():
    try:
        all_data = []
        offset = 0
        batch_size = 1000
        while True:
            response = supabase.table('products').select('*').range(offset, offset + batch_size - 1).execute()
            if response.data:
                all_data.extend(response.data)
                if len(response.data) < batch_size:
                    break
                offset += batch_size
            else:
                break
        if all_data:
            df = pd.DataFrame(all_data)
            # Clean numeric columns
            df['mrp'] = pd.to_numeric(df['mrp'], errors='coerce').fillna(0)
            df['packing_pcs'] = pd.to_numeric(df['packing_pcs'], errors='coerce').fillna(0).astype(int)
            df['packing_bx'] = pd.to_numeric(df['packing_bx'], errors='coerce').fillna(0).astype(int)
            df['packing_car'] = pd.to_numeric(df['packing_car'], errors='coerce').fillna(0).astype(int)
            # Clean text columns
            for col in ['category', 'sub_category', 'company', 'series', 'product_name', 'ref_code', 'specification']:
                if col in df.columns:
                    df[col] = df[col].fillna('').astype(str).str.strip()
            return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading products: {e}")
        return pd.DataFrame()

with st.spinner('Loading catalog...'):
    df = load_products()

if df.empty:
    st.warning("⚠️ No products found. Check your Supabase connection.")
    st.stop()


def format_price(price):
    """Format price with commas (Indian style)."""
    if price == 0:
        return "—"
    price_str = f"{price:,.2f}"
    return price_str

def get_unique_sorted(series):
    """Get sorted unique non-empty values."""
    return sorted([v for v in series.dropna().unique().tolist() if v and str(v).strip()])

def load_logo_base64(filename):
    """Load a logo image as base64 for embedding in HTML."""
    filepath = os.path.join(os.path.dirname(__file__), filename)
    if os.path.exists(filepath):
        with open(filepath, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    return None

# Load logos
tejas_logo_b64 = load_logo_base64('Tejas.png')
deli_logo_b64 = load_logo_base64('delitools-logo (1).png')

def format_spec_html(spec_text):
    """Parse specification text into styled HTML rows."""
    if not spec_text or not str(spec_text).strip():
        return ''
    lines = str(spec_text).strip().split('\n')
    rows_html = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Try to parse key: value or key - value patterns
        for sep in [':', ' - ', '–', '\t']:
            if sep in line:
                parts = line.split(sep, 1)
                if len(parts) == 2 and parts[0].strip() and parts[1].strip():
                    rows_html.append(
                        f'<div class="spec-row">'
                        f'<div class="spec-label">{parts[0].strip()}</div>'
                        f'<div class="spec-value">{parts[1].strip()}</div>'
                        f'</div>'
                    )
                    break
        else:
            # No separator found, render as plain row
            rows_html.append(
                f'<div class="spec-row">'
                f'<div class="spec-value" style="min-width:100%">{line}</div>'
                f'</div>'
            )
    return '\n'.join(rows_html) if rows_html else f'<div class="spec-plain">{spec_text}</div>'

def get_whatsapp_share_url(product):
    """Generate a clean, professional WhatsApp share URL."""
    name = product.get('product_name', 'Unknown')
    ref = product.get('ref_code', '—')
    mrp = product.get('mrp', 0)
    category = product.get('category', '')
    brand = product.get('company', '')
    
    message = (
        "*TEJAS IMPEX PVT. LTD. | PRODUCT PROFILE*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"■ *Product Name:* {name}\n"
        f"■ *Model Reference:* {ref}\n"
        f"■ *Category:* {category}\n"
        f"■ *Brand / Company:* {brand}\n"
        f"■ *MRP:* NPR {mrp:,.2f} (Incl. of all taxes)\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🌐 *View catalog at:* http://localhost:8501"
    )
    encoded_message = urllib.parse.quote(message)
    return f"https://wa.me/?text={encoded_message}"

def export_to_excel(df_to_export):
    """Format catalog columns and export as Excel binary data (fallback to CSV if openpyxl lacks)."""
    # Select columns
    cols = [
        'ref_code', 'product_name', 'category', 'sub_category',
        'company', 'series', 'mrp', 'packing_pcs', 'packing_bx',
        'packing_car', 'specification', 'image_url'
    ]
    # Filter columns that actually exist
    valid_cols = [c for c in cols if c in df_to_export.columns]
    export_df = df_to_export[valid_cols].copy()
    
    # Rename columns to human-readable names
    rename_dict = {
        'ref_code': 'Model/Reference',
        'product_name': 'Product Name',
        'category': 'Category',
        'sub_category': 'Sub-Category',
        'company': 'Company/Brand',
        'series': 'Series',
        'mrp': 'MRP (NPR)',
        'packing_pcs': 'Packing (Pcs)',
        'packing_bx': 'Packing (Box)',
        'packing_car': 'Packing (Carton)',
        'specification': 'Specifications',
        'image_url': 'Image URL'
    }
    export_df = export_df.rename(columns={k: v for k, v in rename_dict.items() if k in export_df.columns})
    
    # Try openpyxl
    try:
        import openpyxl
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            export_df.to_excel(writer, index=False, sheet_name='Product Catalog')
        return buffer.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "xlsx"
    except Exception:
        # Fallback to CSV
        csv_str = export_df.to_csv(index=False)
        return csv_str.encode('utf-8'), "text/csv", "csv"




if st.session_state.view == 'detail' and st.session_state.selected_product is not None:
    p = st.session_state.selected_product

    col_back, col_logout = st.columns([8, 2])
    with col_back:
        if st.button("← Back to Catalog", type="primary"):
            st.session_state.view = 'catalog'
            st.session_state.selected_product = None
            st.rerun()
    with col_logout:
        if st.button("🔓 Logout", type="secondary", use_container_width=True, key="logout_btn_detail"):
            st.session_state.authenticated = False
            st.session_state.view = 'catalog'
            st.session_state.selected_product = None
            st.rerun()

    # Hero
    st.markdown(f"""
    <div class="detail-hero">
        <div class="detail-breadcrumb">
            Catalog &nbsp;›&nbsp; {p.get('category', '')} &nbsp;›&nbsp; {p.get('sub_category', '')}
        </div>
        <div class="detail-title">{p.get('product_name', 'Product')}</div>
        <div class="detail-ref">Model: {p.get('ref_code', '—')}</div>
    </div>
    """, unsafe_allow_html=True)

    # Two-column layout
    col_img, col_info = st.columns([1, 1], gap="large")

    with col_img:
        image_url = p.get('image_url', '')
        if image_url and str(image_url).strip():
            st.markdown(f"""
            <div class="detail-image-container">
                <img src="{image_url}" alt="{p.get('product_name', '')}">
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="detail-image-container">
                <div class="no-image-placeholder">
                    <div class="no-image-icon">📦</div>
                    <div>No image available</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col_info:
        # Info Card
        company = p.get('company', '')
        series = p.get('series', '')
        category = p.get('category', '')
        sub_cat = p.get('sub_category', '')
        mrp = p.get('mrp', 0)

        tags_html = f'<span class="detail-chip chip-cat">{category}</span>' if category else ''
        if sub_cat:
            tags_html += f' <span class="detail-chip chip-sub">{sub_cat}</span>'
        if series:
            tags_html += f' <span class="detail-chip chip-series">{series}</span>'
        if company:
            tags_html += f' <span class="detail-chip" style="background:linear-gradient(135deg,#fff3e0,#ffe0b2);color:#e65100;">{company}</span>'

        st.markdown(f"""
        <div class="detail-info-card">
            <div class="detail-badge-row">{tags_html}</div>
            <div class="detail-price"><span class="cur">₹</span> {format_price(mrp)}</div>
            <div style="font-size: 13px; color: #2d6a4f; font-weight: 600; margin-bottom: 16px;">
                ✅ MRP (Inclusive of all taxes)
            </div>
            <div class="detail-meta-grid">
                <div class="detail-meta-box">
                    <div class="detail-meta-num">{p.get('packing_pcs', 0)}</div>
                    <div class="detail-meta-lbl">Per Piece</div>
                </div>
                <div class="detail-meta-box">
                    <div class="detail-meta-num">{p.get('packing_bx', 0)}</div>
                    <div class="detail-meta-lbl">Per Box</div>
                </div>
                <div class="detail-meta-box">
                    <div class="detail-meta-num">{p.get('packing_car', 0)}</div>
                    <div class="detail-meta-lbl">Per Carton</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        wa_url = get_whatsapp_share_url(p)
        st.markdown(f"""
        <a href="{wa_url}" target="_blank" style="text-decoration: none;">
            <button class="whatsapp-btn">
                <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor" style="display:inline-block; vertical-align:-3px; margin-right:4px;">
                    <path d="M12.031 2c-5.514 0-9.99 4.476-9.99 9.99 0 2.057.625 3.993 1.8 5.617L2 22l4.56-1.328a9.92 9.92 0 005.47 1.62c5.514 0 9.99-4.476 9.99-9.99C22.02 6.476 17.545 2 12.031 2zm6.657 14.394c-.255.708-1.5 1.29-2.07 1.35-.55.06-1.27.08-2.03-.16-.62-.2-1.35-.45-2.09-.78-2.95-1.3-4.85-4.32-5-4.52-.15-.2-1.12-1.49-1.12-2.84 0-1.35.7-2.01.95-2.28.25-.26.56-.33.74-.33.18 0 .37 0 .53.01.17 0 .39-.06.6.46.22.54.76 1.85.83 1.99.07.14.12.31.02.51-.1.2-.15.31-.3.48-.15.17-.32.39-.46.52-.16.15-.33.31-.14.63.19.32.85 1.4 1.82 2.27.97.87 1.78 1.13 2.1 1.29.32.16.51.13.7-.09.19-.22.82-.95 1.04-1.28.22-.33.44-.28.75-.17.3.11 1.93.91 2.27 1.08.33.17.56.25.64.39.08.14.08.82-.17 1.53z"/>
                </svg>
                Share details on WhatsApp
            </button>
        </a>
        """, unsafe_allow_html=True)

    # Specifications (parsed into styled rows)
    spec = p.get('specification', '')
    spec_html = format_spec_html(spec)
    if spec_html:
        st.markdown(f"""
        <div class="detail-spec-card">
            <div class="detail-spec-title">📋 Specifications</div>
            <div class="detail-spec-content">{spec_html}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="detail-spec-card">
            <div class="detail-spec-title">📋 Specifications</div>
            <div class="detail-spec-content">
                <div class="spec-plain" style="color:#a0aec0; text-align:center;">
                    No specifications available for this product.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Source info (subtle)
    src_file = p.get('source_file', '')
    src_sheet = p.get('source_sheet', '')
    if src_file or src_sheet:
        st.markdown(f"""
        <div style="margin-top: 16px; padding: 12px 18px; background: #f8f9fa; border-radius: 12px;
                    font-size: 12px; color: #a0aec0;">
            📁 Source: {src_file} {f"/ {src_sheet}" if src_sheet else ""}
        </div>
        """, unsafe_allow_html=True)



elif st.session_state.view == 'catalog':
    # ── Stats Calculations ──
    categories_count = len(get_unique_sorted(df['category']))
    companies_count = len(get_unique_sorted(df['company']))

    # Hero Banner with logos
    logos_html = '<div class="hero-logos">'
    if tejas_logo_b64:
        logos_html += f'<img src="data:image/png;base64,{tejas_logo_b64}" class="hero-logo-img" alt="Tejas Impex">'
    if deli_logo_b64:
        logos_html += f'<img src="data:image/png;base64,{deli_logo_b64}" class="hero-logo-img" alt="Deli Tools">'
    logos_html += '</div>'

    st.markdown(f"""
    <div class="hero-banner">
        <div class="hero-content">
            <div class="hero-left">
                {logos_html}
                <div>
                    <div class="hero-title">TEJAS IMPEX PVT. LTD.</div>
                    <div class="hero-sub">Premium Product Catalog</div>
                </div>
            </div>
            <div class="hero-stats">
                <div>
                    <div class="hero-stat-value">{len(df)}</div>
                    <div class="hero-stat-label">Total Products</div>
                </div>
                <div class="hero-stat-divider"></div>
                <div>
                    <div class="hero-stat-value">{categories_count}</div>
                    <div class="hero-stat-label">Categories</div>
                </div>
                <div class="hero-stat-divider"></div>
                <div>
                    <div class="hero-stat-value">{companies_count}</div>
                    <div class="hero-stat-label">Brands</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Top-Bar Filters Grid ──
    # Row 1: Search, Sort, and Logout
    col_search, col_sort, col_logout = st.columns([6.5, 2.0, 1.5], gap="small")
    with col_search:
        if HAS_KEYUP:
            search = st_keyup(
                "Search",
                value=st.session_state.search_term,
                placeholder="Search products by name, reference code, specs...",
                label_visibility="collapsed",
                debounce=250,
                key="keyup_search_input"
            )
        else:
            search = st.text_input(
                "Search",
                value=st.session_state.search_term,
                placeholder="Search products by name, reference code, specs...",
                label_visibility="collapsed",
                key="text_search_input"
            )
        if search != st.session_state.search_term:
            st.session_state.search_term = search
            st.session_state.page = 1

    with col_sort:
        sort_options = ["Name A→Z", "Name Z→A", "Price ↑ Low to High", "Price ↓ High to Low", "Ref Code"]
        sort = st.selectbox(
            "Sort By", sort_options,
            index=sort_options.index(st.session_state.sort_by) if st.session_state.sort_by in sort_options else 0,
            label_visibility="collapsed",
            key="sort_selectbox"
        )
        st.session_state.sort_by = sort

    with col_logout:
        if st.button("🔓 Logout", type="secondary", use_container_width=True, key="logout_btn_catalog"):
            st.session_state.authenticated = False
            st.session_state.view = 'catalog'
            st.session_state.selected_product = None
            st.rerun()

    # Row 2: Categories, Sub-Categories, Companies, Series selectors
    col_cat, col_sub, col_comp, col_series = st.columns(4, gap="small")
    
    with col_cat:
        categories = get_unique_sorted(df['category'])
        cat = st.selectbox(
            "📂 Category", ["All Catalog"] + categories,
            index=(["All Catalog"] + categories).index("All Catalog" if st.session_state.category == "All" else st.session_state.category) if st.session_state.category in (["All"] + categories) else 0,
            key="cat_selectbox"
        )
        cat_val = "All" if cat == "All Catalog" else cat
        if cat_val != st.session_state.category:
            st.session_state.category = cat_val
            st.session_state.sub_category = 'All'
            st.session_state.page = 1

    with col_sub:
        if st.session_state.category != 'All':
            sub_cats_df = df[df['category'] == st.session_state.category]
        else:
            sub_cats_df = df
        sub_categories = get_unique_sorted(sub_cats_df['sub_category'])
        sub_cat = st.selectbox(
            "📁 Sub-Category", ["All Sub-Categories"] + sub_categories,
            index=(["All Sub-Categories"] + sub_categories).index("All Sub-Categories" if st.session_state.sub_category == "All" else st.session_state.sub_category) if st.session_state.sub_category in (["All"] + sub_categories) else 0,
            key="sub_cat_selectbox"
        )
        sub_cat_val = "All" if sub_cat == "All Sub-Categories" else sub_cat
        if sub_cat_val != st.session_state.sub_category:
            st.session_state.sub_category = sub_cat_val
            st.session_state.page = 1

    with col_comp:
        companies = get_unique_sorted(df['company'])
        comp = st.selectbox(
            "🏢 Brand", ["All Brands"] + companies,
            index=(["All Brands"] + companies).index("All Brands" if st.session_state.company == "All" else st.session_state.company) if st.session_state.company in (["All"] + companies) else 0,
            key="company_selectbox"
        )
        comp_val = "All" if comp == "All Brands" else comp
        if comp_val != st.session_state.company:
            st.session_state.company = comp_val
            st.session_state.page = 1

    with col_series:
        series_list = get_unique_sorted(df['series'])
        series_options = ["All Series"] + series_list if series_list else ["All Series"]
        ser = st.selectbox(
            "🎨 Series", series_options,
            index=series_options.index("All Series" if st.session_state.series == "All" else st.session_state.series) if st.session_state.series in (["All"] + series_list) else 0,
            key="series_selectbox"
        )
        ser_val = "All" if ser == "All Series" else ser
        if ser_val != st.session_state.series:
            st.session_state.series = ser_val
            st.session_state.page = 1

    # Row 3: Price Range Slider, Reset Button, and Export Button
    col_price, col_reset, col_export = st.columns([6.0, 2.0, 2.0], gap="small")
    
    with col_price:
        max_price = float(df['mrp'].max()) if df['mrp'].max() > 0 else 100000.0
        curr_low, curr_high = st.session_state.price_range
        curr_low = float(max(0.0, min(float(curr_low), max_price)))
        curr_high = float(max(0.0, min(float(curr_high), max_price)))
        if curr_low > curr_high:
            curr_low, curr_high = 0.0, max_price
            
        price_range = st.slider(
            "💰 Price Range (₹)",
            min_value=0.0,
            max_value=max_price,
            value=(curr_low, curr_high),
            format="₹%.0f",
            key="price_slider"
        )
        if price_range != st.session_state.price_range:
            st.session_state.price_range = (float(price_range[0]), float(price_range[1]))
            st.session_state.page = 1

    with col_reset:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("🔄 Reset Filters", use_container_width=True, key="reset_filters_btn"):
            st.session_state.search_term = ''
            st.session_state.category = 'All'
            st.session_state.sub_category = 'All'
            st.session_state.company = 'All'
            st.session_state.series = 'All'
            st.session_state.sort_by = 'Name A→Z'
            st.session_state.price_range = (0.0, max_price)
            st.session_state.page = 1
            st.rerun()

    # ── Apply Filtering Logic ──
    filtered = df.copy()
    
    if st.session_state.search_term:
        q = st.session_state.search_term.lower()
        filtered = filtered[
            filtered['product_name'].str.lower().str.contains(q, na=False) |
            filtered['ref_code'].str.lower().str.contains(q, na=False) |
            filtered['category'].str.lower().str.contains(q, na=False) |
            filtered['sub_category'].str.lower().str.contains(q, na=False) |
            filtered['specification'].str.lower().str.contains(q, na=False)
        ]
        
    if st.session_state.category != 'All':
        filtered = filtered[filtered['category'] == st.session_state.category]
    if st.session_state.sub_category != 'All':
        filtered = filtered[filtered['sub_category'] == st.session_state.sub_category]
    if st.session_state.company != 'All':
        filtered = filtered[filtered['company'] == st.session_state.company]
    if st.session_state.series != 'All':
        filtered = filtered[filtered['series'] == st.session_state.series]
        
    p_low, p_high = st.session_state.price_range
    filtered = filtered[(filtered['mrp'] >= p_low) & (filtered['mrp'] <= p_high)]
    
    # Sort
    sort_col = st.session_state.sort_by
    if sort_col == "Name A→Z":
        filtered = filtered.sort_values('product_name', ascending=True)
    elif sort_col == "Name Z→A":
        filtered = filtered.sort_values('product_name', ascending=False)
    elif sort_col == "Price ↑ Low to High":
        filtered = filtered.sort_values('mrp', ascending=True)
    elif sort_col == "Price ↓ High to Low":
        filtered = filtered.sort_values('mrp', ascending=False)
    elif sort_col == "Ref Code":
        filtered = filtered.sort_values('ref_code', ascending=True)

    with col_export:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        excel_data, mime_type, file_ext = export_to_excel(filtered)
        st.download_button(
            label="📥 Export List",
            data=excel_data,
            file_name=f"TEJAS_IMPEX_Catalog_{datetime.now().strftime('%Y%m%d')}.{file_ext}",
            mime=mime_type,
            use_container_width=True,
            key="export_btn_catalog"
        )

    # Results bar
    total_results = len(filtered)
    active_filters = []
    if st.session_state.category != 'All':
        active_filters.append(st.session_state.category)
    if st.session_state.sub_category != 'All':
        active_filters.append(st.session_state.sub_category)
    if st.session_state.company != 'All':
        active_filters.append(st.session_state.company)
    if st.session_state.series != 'All':
        active_filters.append(st.session_state.series)
    if st.session_state.search_term:
        active_filters.append(f'"{st.session_state.search_term}"')

    filter_text = " in " + ", ".join(active_filters) if active_filters else ""

    st.markdown(f"""
    <div class="results-bar">
        <div class="results-text">
            Showing <span class="results-accent">{total_results}</span> products{filter_text}
        </div>
        <div class="sort-info">Sorted by: {st.session_state.sort_by}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Pagination Setup ──
    PAGE_SIZE = 12
    total_products = len(filtered)
    total_pages = max(1, (total_products + PAGE_SIZE - 1) // PAGE_SIZE)

    if st.session_state.page > total_pages:
        st.session_state.page = total_pages

    start_idx = (st.session_state.page - 1) * PAGE_SIZE
    end_idx = min(start_idx + PAGE_SIZE, total_products)
    page_data = filtered.iloc[start_idx:end_idx]

    # ── Product Grid ──
    if len(page_data) == 0:
        st.markdown("""
        <div style="text-align: center; padding: 80px 20px;">
            <div style="font-size: 64px; margin-bottom: 16px;">🔍</div>
            <div style="font-size: 22px; font-weight: 700; color: #1a1a2e;">No products found</div>
            <div style="font-size: 15px; color: #6c757d; margin-top: 8px;">
                Try adjusting your search or filters to find what you're looking for
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Render in rows of 4
        rows = [page_data.iloc[i:i+4] for i in range(0, len(page_data), 4)]

        for row_chunk in rows:
            cols = st.columns(4, gap="medium")
            for idx, (_, product) in enumerate(row_chunk.iterrows()):
                with cols[idx]:
                    image_url = product.get('image_url', '')
                    if not image_url or not str(image_url).strip():
                        img_html = """
                        <div class="no-image-placeholder">
                            <div class="no-image-icon">📦</div>
                        </div>"""
                    else:
                        img_html = f'<img src="{image_url}" alt="{product.get("product_name", "")}" loading="lazy">'

                    company = product.get('company', '')
                    ref_code = product.get('ref_code', '')
                    name = product.get('product_name', 'Unknown')
                    mrp = product.get('mrp', 0)
                    category = product.get('category', '')
                    series = product.get('series', '')
                    sub_cat = product.get('sub_category', '')
                    pcs = product.get('packing_pcs', 0)
                    bx = product.get('packing_bx', 0)

                    tags = ""
                    if category:
                        tags += f'<span class="chip chip-cat">{category}</span>'
                    if series:
                        tags += f'<span class="chip chip-series">{series}</span>'
                    if sub_cat:
                        tags += f'<span class="chip chip-sub">{sub_cat}</span>'

                    packing_info = ""
                    if pcs:
                        packing_info += f"<strong>{pcs}</strong> pcs"
                    if bx:
                        packing_info += f" · <strong>{bx}</strong> /box"

                    st.markdown(f"""
                    <div class="product-card">
                        <div class="card-image-wrap">
                            {f'<div class="card-brand-ribbon">{company}</div>' if company else ''}
                            {img_html}
                        </div>
                        <div class="card-body">
                            <div class="card-ref">{ref_code}</div>
                            <div class="card-name">{name}</div>
                            <div class="card-price">
                                <span class="currency">₹</span>{format_price(mrp)}
                            </div>
                            <div class="card-tags">{tags}</div>
                            <div class="card-footer">
                                <div class="card-packing">{packing_info if packing_info else '—'}</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Streamlit buttons for Details & WhatsApp Share side-by-side
                    col_btn1, col_btn2 = st.columns([1.2, 1])
                    with col_btn1:
                        if st.button("🔎 Details", key=f"view_{product.get('id', idx)}", use_container_width=True):
                            st.session_state.selected_product = product.to_dict()
                            st.session_state.view = 'detail'
                            st.rerun()
                    with col_btn2:
                        wa_url = get_whatsapp_share_url(product)
                        st.markdown(f"""
                        <a href="{wa_url}" target="_blank" style="text-decoration: none;">
                            <button class="card-wa-btn" style="
                                width: 100%; height: 38px; display: flex; align-items: center;
                                justify-content: center; gap: 4px; border-radius: 12px;
                                font-family: 'Inter', sans-serif; font-weight: 600; cursor: pointer;
                                transition: all 0.3s ease; box-sizing: border-box; margin: 0;
                            ">
                                📲 Share
                            </button>
                        </a>
                        """, unsafe_allow_html=True)

    # ── Pagination Controls ──
    if total_pages > 1:
        st.markdown("<br>", unsafe_allow_html=True)

        # Calculate page range to show
        max_visible = 7
        if total_pages <= max_visible:
            page_nums = list(range(1, total_pages + 1))
        else:
            current = st.session_state.page
            if current <= 4:
                page_nums = list(range(1, 6)) + [0, total_pages]
            elif current >= total_pages - 3:
                page_nums = [1, 0] + list(range(total_pages - 4, total_pages + 1))
            else:
                page_nums = [1, 0] + list(range(current - 1, current + 2)) + [0, total_pages]

        # Layout: prev | pages | next | info
        num_page_buttons = len(page_nums)
        col_layout = [1] + [1] * num_page_buttons + [1, 3]
        page_cols = st.columns(col_layout)

        # Previous
        with page_cols[0]:
            if st.button("◀", disabled=(st.session_state.page <= 1), key="prev_p", use_container_width=True):
                st.session_state.page -= 1
                st.rerun()

        # Page numbers
        for i, p_num in enumerate(page_nums):
            with page_cols[i + 1]:
                if p_num == 0:
                    st.markdown("<div style='text-align:center; color:#a0aec0; padding-top:6px;'>…</div>", unsafe_allow_html=True)
                else:
                    btn_type = "primary" if p_num == st.session_state.page else "secondary"
                    if st.button(str(p_num), key=f"pg_{p_num}", type=btn_type, use_container_width=True):
                        st.session_state.page = p_num
                        st.rerun()

        # Next
        with page_cols[num_page_buttons + 1]:
            if st.button("▶", disabled=(st.session_state.page >= total_pages), key="next_p", use_container_width=True):
                st.session_state.page += 1
                st.rerun()

        # Page info
        with page_cols[num_page_buttons + 2]:
            st.markdown(
                f"<div style='text-align:right; color:#a0aec0; font-size:13px; padding-top:8px;'>"
                f"Page <strong style='color:#1a1a2e;'>{st.session_state.page}</strong> of "
                f"<strong style='color:#1a1a2e;'>{total_pages}</strong> &nbsp;·&nbsp; "
                f"Showing {start_idx+1}–{end_idx} of {total_products}"
                f"</div>",
                unsafe_allow_html=True
            )

    # ── Footer ──
    st.markdown("""
    <div class="app-footer">
        <div class="footer-brand">TEJAS IMPEX PVT. LTD.</div>
        <div class="footer-info">
            📍 Teku, Kathmandu, Nepal &nbsp;·&nbsp;
            ✉️ tejasimpex2023@gmail.com &nbsp;·&nbsp;
            📱 9801986465
        </div>
        <div class="footer-copy">© 2026 TEJAS IMPEX PVT. LTD. All Rights Reserved</div>
    </div>
    """, unsafe_allow_html=True)

