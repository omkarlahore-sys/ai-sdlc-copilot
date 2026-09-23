"""Design tokens and stylesheet."""

from __future__ import annotations

import streamlit as st

FONT = (
    '"Inter Tight", -apple-system, BlinkMacSystemFont, "Segoe UI", '
    "Roboto, sans-serif"
)
MONO = '"JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, monospace'

LEVELS = {
    "BR": {"c": "#2563eb", "light": "#7dabff", "bg": "rgba(37,99,235,.12)", "mid": "rgba(37,99,235,.22)", "line": "rgba(37,99,235,.35)"},
    "EP": {"c": "#059669", "light": "#4ade80", "bg": "rgba(5,150,105,.12)", "mid": "rgba(5,150,105,.22)", "line": "rgba(5,150,105,.35)"},
    "US": {"c": "#7c3aed", "light": "#a78bfa", "bg": "rgba(124,58,237,.12)", "mid": "rgba(124,58,237,.22)", "line": "rgba(124,58,237,.35)"},
    "AC": {"c": "#b45309", "light": "#fbbf24", "bg": "rgba(180,83,9,.14)", "mid": "rgba(180,83,9,.24)", "line": "rgba(180,83,9,.35)"},
    "TC": {"c": "#0d9488", "light": "#2dd4bf", "bg": "rgba(13,148,136,.12)", "mid": "rgba(13,148,136,.22)", "line": "rgba(13,148,136,.35)"},
}
TYPE_COLORS = {k: v["c"] for k, v in LEVELS.items()}

CSS = f"""
<style>
*{{box-sizing:border-box;}}
@keyframes blobA {{ 0%,100% {{ transform: translate(0,0) scale(1); }} 50% {{ transform: translate(-4%,4%) scale(1.18); }} }}
@keyframes blobB {{ 0%,100% {{ transform: translate(0,0) scale(1); }} 50% {{ transform: translate(4%,-5%) scale(1.12); }} }}
@keyframes gridPan {{ from {{ background-position: 0 0, 0 0; }} to {{ background-position: 64px 64px, 64px 64px; }} }}
@keyframes spin {{ to {{ transform: rotate(360deg); }} }}
@keyframes floatY {{ 0%,100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-5px); }} }}
@keyframes fadeUp {{ from {{ opacity:0; transform:translateY(18px); }} to {{ opacity:1; transform:translateY(0); }} }}
@keyframes fadeIn {{ from {{ opacity:0; }} to {{ opacity:1; }} }}
@keyframes popIn {{ 0% {{ opacity:0; transform:scale(.7); }} 60% {{ opacity:1; transform:scale(1.08); }} 100% {{ opacity:1; transform:scale(1); }} }}
@keyframes pulseGlow {{ 0%,100% {{ box-shadow:0 0 0 0 rgba(124,58,237,0); }} 50% {{ box-shadow:0 0 0 7px rgba(124,58,237,.12); }} }}
@keyframes dash {{ from {{ stroke-dashoffset:420; }} to {{ stroke-dashoffset:0; }} }}
@keyframes blink {{ 0%,100% {{ opacity:.28; }} 50% {{ opacity:1; }} }}
@keyframes drift {{ 0%,100% {{ opacity:.35; transform:scale(1); }} 50% {{ opacity:1; transform:scale(1.25); }} }}
@keyframes gradientShift {{ 0% {{ background-position:0% 50%; }} 100% {{ background-position:200% 50%; }} }}
@keyframes roll {{ from {{ opacity:0; transform:translateY(70%); }} to {{ opacity:1; transform:none; }} }}

:root {{
  --font: {FONT};
  --mono: {MONO};

  --bg: #f7f1e3;
  --surface: #ffffff;
  --card: #ffffff;
  --card-line: rgba(30,22,10,.10);
  --sunk: rgba(30,22,10,.045);
  --line: rgba(30,22,10,.09);
  --line-2: rgba(30,22,10,.16);

  --text: #221a0e;
  --text-2: #5c5142;
  --muted: #82765f;
  --dim: #9c9078;

  --accent: #7c3aed;
  --accent-2: #2563eb;
  --gradient: linear-gradient(135deg, #7c3aed, #2563eb);
  --accent-soft: rgba(124,58,237,.10);
  --accent-line: rgba(124,58,237,.35);

  --l1: {LEVELS["BR"]["c"]};  --l1-lt: {LEVELS["BR"]["c"]};  --l1-bg: {LEVELS["BR"]["bg"]};  --l1-mid: {LEVELS["BR"]["mid"]};  --l1-line: {LEVELS["BR"]["line"]};
  --l2: {LEVELS["EP"]["c"]};  --l2-lt: {LEVELS["EP"]["c"]};  --l2-bg: {LEVELS["EP"]["bg"]};  --l2-mid: {LEVELS["EP"]["mid"]};  --l2-line: {LEVELS["EP"]["line"]};
  --l3: {LEVELS["US"]["c"]};  --l3-lt: {LEVELS["US"]["c"]};  --l3-bg: {LEVELS["US"]["bg"]};  --l3-mid: {LEVELS["US"]["mid"]};  --l3-line: {LEVELS["US"]["line"]};
  --l4: {LEVELS["AC"]["c"]};  --l4-lt: {LEVELS["AC"]["c"]};  --l4-bg: {LEVELS["AC"]["bg"]};  --l4-mid: {LEVELS["AC"]["mid"]};  --l4-line: {LEVELS["AC"]["line"]};
  --l5: {LEVELS["TC"]["c"]};  --l5-lt: {LEVELS["TC"]["c"]};  --l5-bg: {LEVELS["TC"]["bg"]};  --l5-mid: {LEVELS["TC"]["mid"]};  --l5-line: {LEVELS["TC"]["line"]};

  --warn: #8a5a05; --warn-bg: rgba(250,204,21,.16); --warn-line: rgba(180,130,10,.4);
  --err: #b91c1c;  --err-bg: rgba(220,38,38,.08);   --err-line: rgba(220,38,38,.3);

  --r: 10px; --r-lg: 20px;
  --gap: clamp(1rem, 1.1vw, 1.4rem);
  --pad-x: clamp(1rem, 2.2vw, 1.75rem);

  --fs-xs: clamp(0.78rem, 0.7vw + 0.6rem, 0.92rem);
  --fs-sm: clamp(0.88rem, 0.7vw + 0.7rem, 1.02rem);
  --fs-base: clamp(0.98rem, 0.7vw + 0.78rem, 1.12rem);
  --fs-md: clamp(1.08rem, 0.9vw + 0.85rem, 1.28rem);
  --fs-lg: clamp(1.3rem, 1.1vw + 1rem, 1.55rem);
  --fs-xl: clamp(2.4rem, 6vw, 5.4rem);
  --fs-num: clamp(2.1rem, 1.8vw + 1.6rem, 2.6rem);
}}

body, .stApp, [data-testid="stAppViewContainer"] {{
  font-family: var(--font);
  color: var(--text);
  font-size: var(--fs-base);
  -webkit-font-smoothing: antialiased;
}}
::selection {{ background: #7c3aed; color: #fff; }}

/* ============================================================ cream canvas */
.stApp {{
  background: var(--bg);
  position: relative;
}}
.stApp::before, .stApp::after {{
  content: ""; position: fixed; z-index: 0; pointer-events: none;
  border-radius: 50%; filter: blur(80px);
}}
.stApp::before {{
  top: -16vw; right: -10vw; width: 44vw; height: 44vw; opacity: .16;
  background: radial-gradient(circle, rgba(124,58,237,.6) 0%, transparent 70%);
  animation: blobA 22s ease-in-out infinite;
}}
.stApp::after {{
  bottom: -14vw; left: -10vw; width: 38vw; height: 38vw; opacity: .14;
  background: radial-gradient(circle, rgba(37,99,235,.55) 0%, transparent 70%);
  animation: blobB 26s ease-in-out infinite;
}}
[data-testid="stAppViewContainer"] {{
  position: relative; z-index: 1;
}}

/* ============================================================ app chrome */
header[data-testid="stHeader"] {{
  background: transparent; height: 0; min-height: 0;
  overflow: visible; pointer-events: none; z-index: 50;
}}
[data-testid="stToolbar"] {{
  height: 0; min-height: 0; overflow: visible;
  pointer-events: none; background: transparent;
}}
[data-testid="stToolbarActions"], [data-testid="stActionButton"],
[data-testid="stStatusWidget"], [data-testid="stDecoration"],
#MainMenu, footer {{ display: none !important; }}
[data-testid="stCustomComponentV1"] {{
  background: transparent !important;
  border: 0 !important;
  border-radius: 999px;
  overflow: hidden;
}}

[data-testid="stExpandSidebarButton"] {{
  position: fixed !important; top: 0.6rem; left: 0.6rem;
  z-index: 1000; pointer-events: auto; display: block !important;
}}

[data-testid="stSidebar"] {{ display: none !important; }}
[data-testid="stSidebarCollapsedControl"] {{ display: none !important; }}

[data-testid="stMain"] .block-container {{
  max-width: min(1800px, 92vw);
  padding: 104px var(--pad-x) 90px;
  position: relative; z-index: 1;
}}
[data-testid="stMain"] .block-container {{ animation: fadeIn .3s ease both; }}

/* ============================================================= floating nav */
[class*="st-key-navbar"] {{
  position: fixed !important; top: 18px; left: 50%;
  transform: translateX(-50%); z-index: 60;
  width: auto !important; max-width: 94vw;
  background: rgba(255,253,244,.86);
  backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(30,22,10,.09);
  border-radius: 999px;
  box-shadow: 0 10px 30px rgba(60,45,20,.14);
  padding: 7px;
}}
[class*="st-key-navbar"] [data-testid="stHorizontalBlock"] {{
  align-items: center; gap: 2px;
  width: fit-content !important; flex-wrap: nowrap !important;
}}
[class*="st-key-navbar"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
[class*="st-key-navbar"] [data-testid="stHorizontalBlock"] > [data-testid="column"] {{
  flex: 0 0 auto !important; width: auto !important; min-width: 0 !important;
}}
[class*="st-key-navbar"] [data-testid="stColumn"]:first-child {{
  display: flex !important; align-items: center !important;
}}
[class*="st-key-navbar"] [data-testid="stColumn"]:first-child [data-testid="stVerticalBlock"],
[class*="st-key-navbar"] [data-testid="stColumn"]:first-child .stElementContainer,
[class*="st-key-navbar"] [data-testid="stColumn"]:first-child .stMarkdown,
[class*="st-key-navbar"] [data-testid="stColumn"]:first-child [data-testid="stMarkdownContainer"] {{
  display: contents !important;
}}
.nav-brand {{
  display: flex; align-items: center; gap: 8px;
  padding: 6px 14px 6px 8px; margin-right: 4px;
  border-right: 1px solid rgba(30,22,10,.09);
  white-space: nowrap;
}}
.nav-mark {{
  width: 24px; height: 24px; border-radius: 8px;
  background: var(--gradient);
  display: grid; place-items: center; flex: 0 0 auto;
  animation: floatY 4s ease-in-out infinite;
}}
.nav-mark span {{ width: 8px; height: 8px; border-radius: 2px; background: #fff; }}
.nav-brand b {{ font-weight: 700; font-size: 13px; letter-spacing: -.01em; color: var(--text); }}

[data-testid="stMain"] [class*="st-key-navbtn_"] .stButton button[kind="secondary"] {{
  display: flex; align-items: center; gap: 7px;
  border: none !important; background: transparent !important;
  color: var(--text-2); font-size: clamp(13px, 0.5vw + 11.5px, 15px); font-weight: 650;
  padding: clamp(9px, 0.5vw + 7px, 12px) clamp(16px, 0.9vw + 12px, 22px);
  border-radius: 999px;
  min-height: 0; white-space: nowrap;
  transition: background .15s ease, color .15s ease;
}}
[data-testid="stMain"] [class*="st-key-navbtn_"] .stButton button[kind="secondary"]:hover:not(:disabled) {{
  background: rgba(30,22,10,.06) !important; color: var(--text);
}}
[data-testid="stMain"] [class*="st-key-navbtn_"] .stButton button[kind="secondary"]:disabled {{
  color: #b6ab94 !important; cursor: not-allowed;
}}
[data-testid="stMain"] [class*="st-key-navon_"] .stButton button[kind="secondary"] {{
  background: var(--text) !important; color: #fffdf4 !important;
  font-weight: 700 !important;
}}
[data-testid="stMain"] [class*="st-key-navon_"] .stButton button[kind="secondary"] [data-testid="stIconMaterial"] {{
  color: #fffdf4;
}}
[data-testid="stMain"] [class*="st-key-navon_"] .stButton button[kind="secondary"]:hover:not(:disabled) {{
  background: var(--text) !important; color: #fffdf4 !important;
}}
[class*="st-key-navbtn_"] .stButton button [data-testid="stIconMaterial"] {{
  font-size: 1rem;
}}

/* ================================================================== card */
[class*="st-key-req_card"] {{
  background: var(--card); border: 1px solid var(--card-line);
  border-radius: var(--r-lg); padding: clamp(1.2rem, 1.6vw, 1.65rem);
  box-shadow: 0 14px 34px rgba(60,45,20,.07);
  animation: fadeUp .55s cubic-bezier(.2,.7,.3,1) both;
}}
.card {{
  background: var(--card); border: 1px solid var(--card-line);
  border-radius: var(--r-lg); padding: clamp(1.2rem, 1.6vw, 1.65rem);
  box-shadow: 0 14px 34px rgba(60,45,20,.07);
  margin-bottom: var(--gap);
  animation: fadeUp .55s cubic-bezier(.2,.7,.3,1) both;
}}
.card-head {{ display: flex; align-items: flex-start; gap: 12px; margin-bottom: 16px; }}
.step-badge {{
  width: 30px; height: 30px; border-radius: 50%; flex: 0 0 auto;
  background: var(--gradient); color: #fff;
  display: grid; place-items: center;
  font-size: 13px; font-weight: 800;
  animation: pulseGlow 2.6s ease-in-out infinite;
}}
.step-badge.n2 {{ background: rgba(30,22,10,.10); color: var(--text); animation: none; }}
.card-title {{ font-size: 16px; font-weight: 700; letter-spacing: -.01em; color: var(--text); }}
.card-sub {{ font-size: 13px; color: var(--muted); margin-top: 3px; }}
.card-sub b {{ color: var(--text); font-weight: 650; }}

/* ============================================================== hero */
.eyebrow {{
  display: inline-flex; align-items: center; gap: 8px;
  font-family: var(--mono); font-size: 12px; letter-spacing: .16em;
  text-transform: uppercase; color: var(--muted);
  margin-bottom: 18px;
}}
.eyebrow .dot {{
  width: 6px; height: 6px; border-radius: 50%; background: #16a34a;
  animation: blink 1.6s ease-in-out infinite;
}}
.head h1 {{
  font-size: var(--fs-xl) !important; font-weight: 800; letter-spacing: -.03em;
  line-height: 1.03; margin: 0 0 20px !important; padding: 0 !important;
  max-width: 16ch;
  background: linear-gradient(100deg, #221a0e 20%, #7c3aed 45%, #2563eb 60%, #221a0e 80%);
  background-size: 200% auto;
  -webkit-background-clip: text; background-clip: text; color: transparent;
  animation: gradientShift 7s linear infinite;
}}
.head p {{
  font-size: clamp(1rem, 1.4vw, 1.25rem); color: var(--text-2);
  max-width: 62ch; line-height: 1.6; margin: 0 0 2.2rem;
}}
.head {{ padding: 0; margin: 0; }}
.page-title {{ font-size: 22px; font-weight: 700; margin: 0 0 6px; letter-spacing: -.015em; color: var(--text); }}
.page-sub {{ font-size: 14px; color: var(--muted); margin: 0 0 18px; max-width: 70ch; line-height: 1.55; }}
.sec {{ font-size: 16px; font-weight: 700; margin: 0 0 4px; letter-spacing: -.01em; color: var(--text); }}
.sec-s {{ font-size: 13px; color: var(--muted); margin: 0 0 12px; line-height: 1.5; }}

/* ========================================================= level chain */
.lvl {{ display: flex; align-items: flex-start; gap: 12px; }}
.lvl-rail {{ display: flex; flex-direction: column; align-items: center; flex: 0 0 auto; padding-top: 2px; }}
.lvl-num {{
  width: 28px; height: 28px; border-radius: 50%;
  color: #fff; display: grid; place-items: center;
  font-size: 12px; font-weight: 800;
  animation: pulseGlow 2.6s ease-in-out infinite;
}}
.lvl-arrow {{ color: var(--dim); font-size: 15px; line-height: 1; padding: 4px 0; }}
.lvl-box {{
  flex: 1 1 auto; border-radius: var(--r); padding: 10px 14px; margin-bottom: 2px;
  display: flex; align-items: center; gap: 12px;
}}
.lvl-icon {{
  width: 34px; height: 34px; border-radius: 9px; flex: 0 0 auto;
  display: grid; place-items: center;
}}
.ho-eyebrow {{
  font-size: 11px; font-weight: 700; letter-spacing: .12em;
  text-transform: uppercase; color: var(--muted); margin-bottom: 6px;
}}
.lvl-text {{ flex: 1 1 auto; min-width: 0; }}
.lvl-t {{ font-size: 13.5px; font-weight: 700; color: var(--text); }}
.lvl-d {{ font-size: 12px; color: var(--text-2); margin-top: 2px; line-height: 1.4; }}
.lvl-tag {{
  flex: 0 0 auto; font-size: 11.5px; font-weight: 700;
  padding: 5px 11px; border-radius: 999px; white-space: nowrap;
}}
@media (max-width: 640px) {{ .lvl-tag {{ display: none; }} }}

/* ============================================================ example tree */
.tree {{ font-size: 13px; }}
.tree-row {{
  display: flex; align-items: baseline; gap: 10px;
  padding: 6px 0; line-height: 1.4;
}}
.tree-id {{
  font-family: var(--mono); font-size: 11px; font-weight: 700;
  flex: 0 0 auto; white-space: nowrap;
}}
.tree-label {{ color: var(--text-2); }}
.tree-children {{
  margin-left: 9px; padding-left: 15px;
  border-left: 2px solid var(--card-line);
}}
.ex-note {{ font-size: 13px; font-weight: 700; color: #6d28d9; }}

/* ================================================================= strip */
.strip {{
  display: flex; align-items: center; gap: 12px; flex-wrap: wrap;
  background: var(--accent-soft); border: 1px solid var(--accent-line);
  border-radius: var(--r); padding: 12px 16px; margin-top: 14px;
  font-size: 13.5px; color: var(--text-2);
}}
.strip .go {{ margin-left: auto; font-weight: 700; color: #6d28d9; }}

/* ================================================================= id tag */
.id {{
  display: inline-block; font-family: var(--mono); font-size: 12px; font-weight: 700;
  padding: 2px 8px; border-radius: 6px; border: 1px solid currentColor;
  margin-right: 6px; line-height: 1.5;
}}
.id.br {{ color: var(--l1-lt); }} .id.ep {{ color: var(--l2-lt); }}
.id.us {{ color: var(--l3-lt); }} .id.ac {{ color: var(--l4-lt); }}
.id.tc {{ color: var(--l5-lt); }}

/* ================================================================= source */
.source {{
  background: var(--card); border: 1px solid var(--card-line);
  border-left: 4px solid var(--l1-lt); border-radius: 16px;
  padding: 18px 22px; margin-bottom: 20px;
  box-shadow: 0 10px 26px rgba(60,45,20,.06);
  animation: fadeUp .4s both;
}}
.source .k {{ font-size: 11px; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; color: var(--dim); margin-bottom: 8px; }}
.source .q {{ font-size: 16px; line-height: 1.55; margin: 10px 0 0; max-width: 90ch; color: var(--text); }}
.sample-tag {{
  display: inline-flex; font-size: 11px; font-weight: 700; letter-spacing: .04em;
  text-transform: uppercase; color: var(--warn); background: var(--warn-bg);
  border: 1px solid var(--warn-line); border-radius: 5px; padding: 2px 7px;
}}
.source .sample-why {{
  font-size: 13px; color: var(--warn); margin: 10px 0 0; padding-top: 10px;
  border-top: 1px dashed var(--warn-line); line-height: 1.5;
}}

/* ================================================================= counts */
.counts {{
  display: grid; grid-template-columns: repeat(4, 1fr);
  border: 1px solid var(--card-line); border-radius: 16px;
  background: var(--surface); overflow: hidden; margin-bottom: 20px;
  box-shadow: 0 10px 26px rgba(60,45,20,.06);
}}
.counts > div {{ padding: 20px 22px; border-left: 1px solid var(--card-line); position: relative; }}
.counts > div:first-child {{ border-left: none; }}
.counts > div::before {{ content: ""; position: absolute; left: 0; right: 0; top: 0; height: 3px; background: var(--c, transparent); }}
.counts .v {{ font-size: var(--fs-num); font-weight: 800; letter-spacing: -.03em; font-variant-numeric: tabular-nums; color: var(--text); }}
.counts .k {{ font-size: 13px; color: var(--muted); margin-top: 5px; }}

/* ========================================================= odometer */
.odo {{ display: inline-flex; }}
.odo-col {{ display: inline-block; overflow: hidden; height: 1em; line-height: 1; vertical-align: top; }}
.odo-strip {{ display: flex; flex-direction: column; animation-timing-function: cubic-bezier(.32,.72,.35,1); animation-fill-mode: both; }}
.odo-strip span {{ height: 1em; line-height: 1; font-variant-numeric: tabular-nums; }}

/* ================================================================== tabs */
.tabbar {{ display: flex; gap: 6px; border-bottom: 1px solid var(--card-line); margin-bottom: 20px; flex-wrap: wrap; }}
.stTabs [data-baseweb="tab-list"] {{ gap: 6px; border-bottom: 1px solid var(--card-line); background: transparent; }}
.stTabs [data-baseweb="tab"] {{
  font-size: 13.5px; font-weight: 600; color: var(--muted);
  padding: 10px 16px; border-radius: 10px 10px 0 0;
  border-bottom: 2px solid transparent;
}}
.stTabs [aria-selected="true"] {{ color: var(--text); background: transparent; border-bottom-color: var(--accent); }}
.stTabs [data-baseweb="tab"]:hover {{ background: transparent; }}

/* ========================================================= artifact rows */
[class*="st-key-art_"] {{ margin-bottom: 8px; }}
[class*="st-key-art_"] .stButton > button {{
  width: 100%; display: flex; align-items: stretch; gap: 10px; text-align: left;
  background: var(--surface); border: 1px solid var(--card-line);
  border-radius: 10px; color: var(--text); font-size: 13.5px;
  padding: 11px 13px; min-height: 0; line-height: 1.4;
  transition: transform .15s ease, background .15s ease, border-color .15s ease;
}}
[class*="st-key-art_"] .stButton > button > div,
[class*="st-key-art_"] .stButton > button > div > span {{
  justify-content: flex-start !important; width: 100%; text-align: left !important; margin: 0;
}}
[class*="st-key-art_"] .stButton > button:hover {{ transform: translateX(2px); background: rgba(30,22,10,.03); }}
[class*="st-key-art_ep_on_"] .stButton > button {{ background: rgba(5,150,105,.08) !important; border-color: rgba(5,150,105,.4) !important; box-shadow: 0 4px 14px rgba(60,45,20,.08); }}
[class*="st-key-art_us_on_"] .stButton > button {{ background: rgba(124,58,237,.08) !important; border-color: rgba(124,58,237,.4) !important; box-shadow: 0 4px 14px rgba(60,45,20,.08); }}
[class*="st-key-art_ac_on_"] .stButton > button {{ background: rgba(180,83,9,.09) !important; border-color: rgba(180,83,9,.4) !important; box-shadow: 0 4px 14px rgba(60,45,20,.08); }}
[class*="st-key-art_tc_on_"] .stButton > button {{ background: rgba(13,148,136,.08) !important; border-color: rgba(13,148,136,.4) !important; box-shadow: 0 4px 14px rgba(60,45,20,.08); }}
[class*="st-key-art_"] .stButton > button code {{
  font-family: var(--mono); font-size: 11.5px; font-weight: 700;
  background: transparent; border: none; padding: 0; color: inherit;
}}

/* =============================================================== detail */
.panel {{ background: var(--card); border: 1px solid var(--card-line); border-radius: 16px; padding: 22px; box-shadow: 0 10px 26px rgba(60,45,20,.06); animation: fadeIn .3s both; }}
.crumb {{ font-family: var(--mono); font-size: 11px; color: var(--dim); margin-bottom: 12px; padding-bottom: 10px; border-bottom: 1px solid var(--card-line); display: flex; gap: 6px; flex-wrap: wrap; line-height: 1.8; }}
.panel h3 {{ font-size: 19px !important; font-weight: 700; margin: 2px 0 14px !important; padding: 0 !important; letter-spacing: -.01em; color: var(--text); }}
.lab {{ font-size: 11px; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; color: var(--dim); margin: 14px 0 5px; }}
.body {{ font-size: 14px; line-height: 1.6; color: var(--text-2); margin: 0; }}
.body ol {{ margin: 0; padding-left: 1.1rem; }}
.body ol li {{ margin-bottom: .22rem; }}
.gwt {{ display: grid; grid-template-columns: 64px 1fr; gap: 6px 10px; font-size: 14px; line-height: 1.5; margin-bottom: 6px; }}
.gwt b {{ font-size: 11px; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; color: var(--l4-lt); padding-top: 3px; }}
.gwt span {{ color: var(--text-2); }}
.child {{ border: 1px solid var(--card-line); border-radius: 10px; padding: 12px 14px; margin-bottom: 8px; background: var(--sunk); transition: background .15s ease, border-color .15s ease; }}
.child:hover {{ background: rgba(30,22,10,.055); border-color: rgba(30,22,10,.18); }}
.child-h {{ display: flex; align-items: center; gap: 6px; font-size: 13.5px; font-weight: 650; margin-bottom: 4px; color: var(--text); }}

/* ================================================================ notices */
.note {{ border: 1px solid var(--line-2); background: var(--sunk); border-radius: var(--r); padding: 10px 14px; font-size: 13px; line-height: 1.55; color: var(--text-2); margin-bottom: var(--gap); }}
.note.err {{ background: var(--err-bg); border-color: var(--err-line); color: var(--err); }}
.note b {{ color: var(--text); font-weight: 650; }}
.note.err b {{ color: var(--err); }}
.empty {{ border: 1px dashed var(--line-2); border-radius: var(--r-lg); background: var(--card); padding: 3rem 1.5rem; text-align: center; }}
.empty .t {{ font-size: var(--fs-md); font-weight: 680; margin-bottom: .3rem; color: var(--text); }}
.empty .s {{ font-size: var(--fs-sm); color: var(--text-2); max-width: 34rem; margin: 0 auto; line-height: 1.6; }}
.hint {{ font-size: 12px; color: var(--dim); }}

/* =================================================== native widget trim */
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-actions_row"]) {{
  order: 5; margin-top: 16px;
}}

.field-label {{
  font-size: 11px; font-weight: 700; letter-spacing: .08em;
  text-transform: uppercase; color: var(--muted); margin: 2px 0 8px;
}}

.stTextArea textarea {{
  font-family: var(--font); font-size: 15px; line-height: 1.6;
  border-radius: 12px; border: 1px solid rgba(30,22,10,.14);
  background: var(--sunk); color: var(--text);
  padding: 14px 16px; min-height: 150px !important;
}}
.stTextArea textarea:focus {{
  outline: none; border-color: rgba(30,22,10,.22);
  box-shadow: none;
}}
.stTextArea > div {{ border-color: transparent !important; }}
.stTextArea textarea::placeholder {{ color: var(--muted); }}
[data-testid="InputInstructions"] {{ display: none; }}

[data-testid="stMain"] .stButton > button, .stDownloadButton > button {{
  border-radius: 999px; font-weight: 700; font-size: 14px;
  padding: 12px 22px; min-height: 0; border: none;
  transition: transform .16s ease, box-shadow .16s ease, background .16s ease;
}}
[data-testid="stMain"] .stButton > button:hover, .stDownloadButton > button:hover {{
  transform: translateY(-2px) scale(1.02);
}}
[data-testid="stMain"] .stButton > button[kind="primary"], .stDownloadButton > button[kind="primary"] {{
  background: var(--gradient) !important; color: #fff !important;
  box-shadow: 0 8px 22px rgba(124,58,237,.28);
}}
[data-testid="stMain"] .stButton > button[kind="primary"]:hover, .stDownloadButton > button[kind="primary"]:hover {{
  box-shadow: 0 12px 28px rgba(124,58,237,.4);
}}
[data-testid="stMain"] .stButton > button[kind="secondary"] {{
  background: var(--sunk) !important; color: var(--text) !important;
  border: 1px solid rgba(30,22,10,.16) !important;
}}
[data-testid="stMain"] .stButton > button[kind="secondary"]:hover {{
  background: rgba(30,22,10,.08) !important; transform: translateY(-2px);
}}
[class*="st-key-art_"] .stButton > button,
[class*="st-key-navbtn_"] .stButton button {{
  transform: none !important; box-shadow: none !important; border-radius: 10px;
}}
[class*="st-key-navbtn_"] .stButton button {{ border-radius: 999px; }}

[data-testid="stDataFrame"] {{ border: 1px solid var(--card-line); border-radius: var(--r); overflow: hidden; }}
.stSelectbox [data-baseweb="select"] > div {{
  background: var(--sunk); border-color: rgba(30,22,10,.16);
  border-radius: 10px; color: var(--text);
}}
hr {{ margin: .9rem 0; border-color: var(--card-line); }}

/* ============================================================== motion */
.card, .source, .counts, .panel, .ex-col, .strip {{
  animation: fadeUp .55s cubic-bezier(.2,.7,.3,1) both;
}}
.counts .v {{ animation: roll .55s cubic-bezier(.2,.8,.25,1) both; }}
[class*="st-key-art_"] {{ animation: fadeUp .32s cubic-bezier(.21,.68,.31,1) both; }}
[class*="st-key-art_"]:nth-of-type(1) {{ animation-delay: .03s; }}
[class*="st-key-art_"]:nth-of-type(2) {{ animation-delay: .07s; }}
[class*="st-key-art_"]:nth-of-type(3) {{ animation-delay: .11s; }}
[class*="st-key-art_"]:nth-of-type(4) {{ animation-delay: .15s; }}
[class*="st-key-art_"]:nth-of-type(5) {{ animation-delay: .19s; }}
.trace-edge {{ stroke-dasharray: 420; animation: dash .8s cubic-bezier(.3,.7,.3,1) both; }}
.trace-node {{ animation: fadeIn .4s ease both; }}

/* ========================================================= generating */
.gen-overlay-note {{ display: none; }}
@keyframes genPopIn {{
  0%   {{ opacity: 0; transform: translate(-50%, -50%) scale(.7); }}
  60%  {{ opacity: 1; transform: translate(-50%, -50%) scale(1.08); }}
  100% {{ opacity: 1; transform: translate(-50%, -50%) scale(1); }}
}}
.gen {{
  position: fixed; isolation: isolate; overflow: hidden;
  top: 50%; left: 50%;
  z-index: 900; width: min(680px, calc(100vw - 3rem));
  background: var(--surface); border-radius: var(--r-lg);
  padding: clamp(28px, 1.6vw + 20px, 40px) clamp(30px, 1.6vw + 22px, 42px);
  box-shadow: 0 24px 60px rgba(30,22,10,.22), 0 0 0 100vmax rgba(10,8,4,.6);
  animation: genPopIn .3s cubic-bezier(.2,.75,.3,1.05) both;
}}
.gen::before {{
  content: ""; position: absolute; z-index: -2;
  top: 50%; left: 50%; width: 220%; height: 260%;
  background: conic-gradient(from 0deg, var(--l1), var(--l2), var(--l3), var(--l4), var(--l5), var(--l1));
  transform: translate(-50%, -50%);
  animation: spin 3.2s linear infinite;
}}
.gen::after {{ content: ""; position: absolute; z-index: -1; inset: 2px; border-radius: 18px; background: var(--surface); }}
.gen-eyebrow {{ display: flex; align-items: center; gap: 8px; font-family: var(--mono); font-size: 11px; letter-spacing: .14em; text-transform: uppercase; color: var(--muted); margin-bottom: 12px; }}
.gen-eyebrow::before {{ content: ""; width: 22px; height: 1px; background: #c2410c; }}
.gen-req {{ font-size: clamp(15px, 0.4vw + 13.5px, 18px); line-height: 1.5; margin: 0 0 18px; color: var(--text); }}
.gen-bar {{ height: 3px; background: var(--sunk); border-radius: 2px; overflow: hidden; margin-bottom: 18px; }}
.gen-bar i {{ display: block; height: 100%; background: var(--gradient); border-radius: 2px; transition: width .42s cubic-bezier(.3,.8,.3,1); }}
.gen-row {{ display: flex; align-items: center; gap: 14px; padding: clamp(9px, 0.4vw + 7px, 13px) 2px; border-bottom: 1px solid var(--card-line); font-size: clamp(13.5px, 0.35vw + 12px, 16px); }}
.gen-row:last-child {{ border-bottom: none; }}
.gen-row.waiting {{ opacity: .45; }}
.gen-mark {{ width: clamp(20px, 0.5vw + 17px, 25px); height: clamp(20px, 0.5vw + 17px, 25px); border-radius: 50%; flex: 0 0 auto; display: grid; place-items: center; font-size: .72rem; color: #fff; font-weight: 700; }}
.gen-mark.idle {{ border: 2px solid rgba(30,22,10,.18); background: transparent; }}
.gen-mark.spin {{ border: 2px solid rgba(30,22,10,.18); border-top-color: var(--c, var(--accent)); animation: spin .7s linear infinite; background: transparent; }}
.gen-mark.done {{ animation: popIn .3s cubic-bezier(.2,.8,.3,1.3) both; }}
.gen-label {{ flex: 1 1 auto; color: var(--text); font-weight: 500; }}
.gen-count {{ font-family: var(--mono); font-size: clamp(13px, 0.3vw + 11.5px, 15px); font-weight: 700; color: var(--text); }}

@media (prefers-reduced-motion: reduce) {{
  *, *::before, *::after {{
    animation-duration: .001ms !important; animation-delay: 0ms !important;
    transition-duration: .001ms !important;
  }}
}}

@media (max-width: 900px) {{
  [data-testid="stMain"] .block-container {{ padding: 92px 1rem 3rem; }}
  .counts {{ grid-template-columns: repeat(2, 1fr); }}
  .counts > div:nth-child(3) {{ border-left: none; }}
  .counts > div:nth-child(n+3) {{ border-top: 1px solid var(--card-line); }}
}}
</style>
"""


def inject() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
