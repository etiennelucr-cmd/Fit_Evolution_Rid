"""V5.8 visual dashboard, weather and weekly coaching. Weather is optional."""
from datetime import datetime,date,timedelta
from zoneinfo import ZoneInfo
from urllib.parse import urlencode
from urllib.request import Request,urlopen
import json,html
import streamlit as st
import streamlit.components.v1 as components
import moteur as m
import journal as j
import coach as c

STYLE="""<style>
:root{--wine:#811b37;--wine2:#a12b4a;--ink:#18121a;--muted:#685b66;--cream:#faf7f7}
[data-testid="stAppViewContainer"]{background:#faf7f8;color:#211a20}
[data-testid="stHeader"]{background:#24131b!important}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#21121b,#3a1826)!important}
[data-testid="stSidebar"] *{color:#fff!important}
[data-testid="stSidebar"] [role="radiogroup"] label{border-radius:10px;padding:8px 10px;margin:2px 0}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked){background:#912542!important}
[data-testid="stSidebar"] button{border:1px solid #c98b9f!important;background:#481d2d!important}
.block-container{max-width:1500px;padding-top:1rem;padding-bottom:4rem}
h1,h2,h3{color:#3c1424!important}
.stButton>button[kind="primary"],button[kind="primary"]{background:#8f2443!important;border-color:#8f2443!important;color:white!important}
.stButton>button{border-radius:10px;min-height:42px}
[data-testid="stMetric"]{background:#fff;border:1px solid #e7d4db;border-radius:14px;padding:14px;box-shadow:0 2px 8px #34121b08}
[data-testid="stMetricValue"]{color:#58172e!important}
.hero{background:linear-gradient(110deg,#381522,#8d2a49);color:white;padding:22px;border-radius:14px}
.hero h2,.hero p{color:white!important}
.sidebar-brand{font-size:21px;font-weight:900;letter-spacing:.3px;padding:15px 4px 22px;color:white}
.sidebar-brand small{font-size:12px;color:#f1b4c7}
.fe-top{background:linear-gradient(115deg,#080a0e,#2a2e35 72%,#57471d);border-radius:14px;color:#fff;padding:18px 22px;margin-bottom:18px;display:flex;justify-content:space-between;align-items:center;gap:18px}
.fe-top strong{font-size:26px}.fe-top small{color:#f1c8d5}
.fe-panel{background:#fff;border:1px solid #e7d4db;border-radius:14px;padding:17px;margin:12px 0;box-shadow:0 3px 12px #38121e0a}
.fe-panel h3{margin:0 0 12px 0;font-size:20px}
.fe-pill{display:inline-block;border-radius:20px;background:#f9e6eb;color:#7e1939;padding:5px 10px;font-weight:700;font-size:12px}
@media(max-width:700px){.block-container{padding:.5rem .7rem 3rem}.fe-top{padding:12px;display:block}.fe-top strong{font-size:20px}.fe-panel{padding:12px}.sidebar-brand{font-size:18px}h1{font-size:1.7rem!important}}

/* V5.8: design system bordeaux / noir, responsive et navigation compacte */
[data-testid="stSidebar"]{min-width:252px!important}
[data-testid="stSidebar"] [role="radiogroup"]{gap:4px}
[data-testid="stSidebar"] [role="radiogroup"] label{padding:10px 12px!important;border:1px solid transparent!important;transition:background .15s ease}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked){background:linear-gradient(100deg,#9b294b,#711b38)!important;border-color:#b95977!important}
[data-testid="stSidebar"] [role="radiogroup"] label:hover{background:#522338!important}
.sidebar-sub{font-size:10px;letter-spacing:1.6px;font-weight:500;color:#e8b9c9;margin-top:5px}
.sidebar-footer{font-size:12px;color:#e8b9c9;padding:20px 6px 14px;line-height:1.9}
[data-testid="stAppViewContainer"]{background:#f7f4f6}
[data-testid="stMetric"]{min-height:114px;background:#fff;border:1px solid #eadce1;box-shadow:0 5px 18px #3715220d}
[data-testid="stMetricLabel"]{font-weight:600}
[data-testid="stVerticalBlockBorderWrapper"]{border-radius:14px}
.stTabs [data-baseweb="tab-list"]{gap:12px}
.fe-welcome{background:linear-gradient(115deg,#3c1526,#842644);border-radius:18px;padding:25px;color:white;margin:16px 0 22px}
.fe-welcome h1{color:white!important;margin:0;font-size:31px}
.fe-welcome p{color:#f3d6df;margin:8px 0 0}
.fe-panel{box-shadow:0 4px 20px #3613210c}
@media(max-width:780px){[data-testid="stSidebar"]{min-width:0!important}.fe-welcome{padding:18px}.fe-welcome h1{font-size:24px}.block-container{padding-top:.5rem}}

/* Gotham 1989 theme: charcoal, cinematic black and golden yellow */
:root{--wine:#f2c230;--wine2:#ffe06b;--ink:#f4f0e5;--muted:#a8a9ad;--cream:#101319}
html,body,[data-testid="stApp"],[data-testid="stAppViewContainer"],.stApp{background:#101319!important;color:#f0eee7!important}
[data-testid="stHeader"]{background:#080a0e!important}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#050608,#171b24)!important;border-right:1px solid #80691d!important}
[data-testid="stSidebar"] *{color:#f6e7aa!important}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked){background:linear-gradient(95deg,#65501b,#2b2b26)!important;border-color:#f2c230!important}
[data-testid="stSidebar"] [role="radiogroup"] label:hover{background:#272c33!important}
[data-testid="stSidebar"] button{background:#20242c!important;border:1px solid #f2c230!important}
h1,h2,h3,h4,h5,h6{color:#f2c230!important;letter-spacing:.025em}
p,li,label,[data-testid="stMarkdownContainer"], [data-testid="stWidgetLabel"], [data-testid="stMetricLabel"]{color:#eeeae1!important}
[data-testid="stMetric"],.fe-panel{background:#1a1e27!important;border:1px solid #645520!important;box-shadow:0 4px 18px #0006!important;color:#f0eee7!important}
[data-testid="stMetricValue"]{color:#f2c230!important}
.fe-panel h3{color:#f2c230!important}
.fe-top,.hero,.fe-welcome{background:linear-gradient(120deg,#090b10,#252b35 65%,#51411a)!important;border:1px solid #857026!important;color:#f4f0e5!important}
.fe-top strong,.fe-welcome h1,.hero h2{color:#f2c230!important}
.fe-top small,.fe-welcome p,.hero p,.sidebar-sub,.sidebar-footer{color:#d9c990!important}
.fe-pill{background:#3a331c!important;color:#ffe078!important}
.stButton>button,.stDownloadButton>button{background:#242832!important;color:#f2c230!important;border:1px solid #8b7426!important}
.stButton>button[kind="primary"],button[kind="primary"]{background:#f2c230!important;color:#101319!important;border-color:#f2c230!important;font-weight:800!important}
.stTabs [data-baseweb="tab"]{color:#f2c230!important}
[data-baseweb="input"], [data-baseweb="select"], [data-baseweb="textarea"]{background:#242832!important;color:#fff!important}
[data-testid="stAlert"]{background:#252b34!important;color:#f0eee7!important}
@media(max-width:700px){.block-container{padding:.6rem .75rem 3rem}.fe-top,.fe-welcome{border-radius:10px}}

/* Gotham 1989 - enhanced contrast, polished controls and dark charts */
[data-testid="stAppViewContainer"]{background:radial-gradient(ellipse at 75% 0%,#1c2530 0%,#0a0d13 58%)!important}
[data-testid="stSidebar"]{background:linear-gradient(170deg,#030507,#101821 70%,#07090e)!important}
[data-testid="stMetric"],.fe-panel,[data-testid="stVerticalBlockBorderWrapper"]{background:linear-gradient(145deg,#151b24,#0c1118)!important;border:1px solid #8a6b24!important;border-radius:15px!important}
[data-testid="stMetricValue"]{color:#ffd34d!important}
.stButton>button[kind="primary"],button[kind="primary"]{background:linear-gradient(110deg,#e7ac20,#ffe06c)!important;color:#090b0e!important;box-shadow:0 0 15px #e9b32c30!important}
.stButton>button:hover{border-color:#ffe38c!important;box-shadow:0 0 13px #e8b52d33!important}
[data-testid="stExpander"], [data-testid="stForm"]{background:#121922!important;border:1px solid #6c5828!important;border-radius:12px!important}
[data-testid="stDataFrame"], [data-testid="stTable"], [data-testid="stPlotlyChart"]{background:#111722!important;border-radius:12px!important}
[data-testid="stSlider"] [role="slider"]{background:#ffd04b!important}
[data-testid="stProgressBar"]>div>div{background:#e8b631!important}
.fe-free-hero{padding:22px;border:1px solid #a17d27;border-radius:16px;background:linear-gradient(110deg,#0a0d12,#1d2935 65%,#3b321a);margin-bottom:16px}
.fe-free-hero h1{margin:0;color:#ffce45!important}.fe-free-hero p{color:#d8dbe1!important}
.fe-muscle-title{color:#ffcf4b;font-size:18px;font-weight:800;margin:10px 0}
@media(max-width:700px){.fe-free-hero{padding:15px}.fe-free-hero h1{font-size:25px!important}}

/* GOTHAM REFINED: coherent contrast and accessible components */
[data-testid="stAppViewContainer"]{background:radial-gradient(circle at 90% 0%,#1a2532 0%,#0b1017 45%,#080b10 100%)!important}
.block-container{max-width:1540px!important;padding-top:1.2rem!important}
[data-testid="stSidebar"]{border-right:1px solid #9b792b!important}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked){background:linear-gradient(100deg,#f4c746,#a67c1c)!important;border:1px solid #ffdf70!important}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) *{color:#0b1017!important;font-weight:800!important}
[data-testid="stMetric"]{padding:16px!important;box-shadow:inset 0 1px 0 #ffffff12,0 8px 25px #0005!important}
[data-testid="stMetricLabel"] p{color:#d4d8e1!important}
[data-testid="stMetricValue"]{font-size:2rem!important}
[data-testid="stSlider"] [data-baseweb="slider"] [role="slider"]{background:#f4c746!important;border-color:#f4c746!important}
[data-baseweb="radio"] input:checked+div,[data-baseweb="checkbox"] input:checked+div{background:#f4c746!important;border-color:#f4c746!important}
[data-testid="stSegmentedControl"] button[aria-pressed="true"]{background:#f4c746!important;color:#0a0e13!important}
[data-testid="stSegmentedControl"] button{background:#1a222c!important;color:#f1d889!important;border:1px solid #6f5928!important}
[data-testid="stCheckbox"] label,[data-testid="stRadio"] label{color:#f1f2f4!important}
[data-testid="stExpander"]{overflow:hidden}
.fe-dashboard-panel{background:linear-gradient(135deg,#141c26,#0d121a);border:1px solid #8a6c2b;border-radius:16px;padding:18px 20px;margin:8px 0 14px;min-height:90px}
.fe-dashboard-panel h3{margin:0 0 10px!important;font-size:1.15rem!important}
.fe-upcoming{padding:10px 12px;margin:8px 0;border:1px solid #3b4654;border-left:3px solid #f3c341;border-radius:9px;background:#141d28;color:#f2f3f5}
.fe-upcoming small{display:block;color:#b9c3ce;margin-top:3px}
.fe-free-hero{background:linear-gradient(110deg,#070a0e,#152333 70%,#483717)!important;box-shadow:inset 0 1px 0 #ffe58a25,0 12px 28px #0005!important}
.fe-free-hero h1{font-size:clamp(1.6rem,3vw,2.5rem)!important}
[data-testid="stPlotlyChart"],[data-testid="stVegaLiteChart"]{border:1px solid #705924;border-radius:14px;overflow:hidden;background:#111822!important}
[data-testid="stAlert"]{border:1px solid #66552e!important}
@media(max-width:800px){.block-container{padding:10px 12px 35px!important}.fe-dashboard-panel{padding:12px}.fe-free-hero{padding:16px!important}}

.gotham-table{width:100%;border-collapse:collapse;border:1px solid #8b6e2c;border-radius:12px;overflow:hidden;background:#121b26;color:#f3ebd7;font-size:14px}
.gotham-table th{background:#29313a;color:#ffd35c;text-align:left;padding:12px}
.gotham-table td{padding:11px;border-bottom:1px solid #303b48}
.gotham-table tr:nth-child(even){background:#18222e}
/* Gotham Ultimate: consistent native controls, charts and tables */
[data-testid="stAppViewContainer"]{background:radial-gradient(ellipse at 75% 0%,#172331 0%,#090d14 55%,#05070a 100%)!important}
.block-container{max-width:1500px!important;padding:1.3rem 2rem 4rem!important}
[data-testid="stSidebar"]{background:linear-gradient(160deg,#030507,#101822)!important}
[data-testid="stSidebar"] [role="radiogroup"] label{border-radius:12px!important}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked){background:linear-gradient(110deg,#b68822,#ffdb66)!important}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) *{color:#10151b!important}
[data-testid="stMetric"]{background:linear-gradient(135deg,#151d29,#0c1119)!important;border:1px solid #98752b!important}
[data-testid="stMetricValue"]{color:#ffcf45!important}
[data-testid="stDataFrame"], [data-testid="stTable"], [data-testid="stVegaLiteChart"], [data-testid="stArrowVegaLiteChart"], [data-testid="stPlotlyChart"]{background:#101824!important;border-radius:12px!important;overflow:hidden!important}
[data-testid="stDataFrame"] canvas{filter:invert(.88) hue-rotate(175deg) saturate(.65)}
[data-testid="stTable"] table{background:#111923!important;color:#f3e9d2!important}
[data-testid="stTable"] th,[data-testid="stTable"] td{background:#151d28!important;color:#f3e9d2!important;border-color:#37404b!important}
[data-baseweb="select"]>div,[data-baseweb="input"]>div,[data-baseweb="popover"]{background:#1b2430!important;color:#f9e9bc!important;border-color:#a27b29!important}
[data-baseweb="select"] *,[data-baseweb="input"] input{color:#f9e9bc!important}
[data-baseweb="slider"] [role="slider"]{background:#f7c744!important;border-color:#f7c744!important}
[data-baseweb="slider"] div[style*="background-color: rgb(255, 75, 75)"]{background:#f7c744!important}
[data-testid="stRadio"] [role="radio"], [data-testid="stCheckbox"] [role="checkbox"]{accent-color:#f7c744!important}
[data-testid="stSegmentedControl"] button{background:#1a2430!important;color:#f3e9d2!important;border-color:#78622e!important}
[data-testid="stSegmentedControl"] button[aria-checked="true"], [data-testid="stSegmentedControl"] button[aria-pressed="true"]{background:#f7c744!important;color:#0c1016!important}
.fe-upcoming{display:flex;justify-content:space-between;align-items:center;gap:12px;background:#141d29;border:1px solid #514522;border-radius:10px;padding:12px 14px;margin:8px 0;color:#f5edd9}
.fe-upcoming small{color:#f5c84e;white-space:nowrap}
.fe-panel{margin-bottom:6px!important}
.fe-free-hero{background:linear-gradient(105deg,#0b111b,#182838 70%,#423719)!important;border:1px solid #d1a135!important;box-shadow:0 10px 28px #0008}
.fe-muscle-title{font-size:18px!important;color:#ffd25c!important}
@media(max-width:780px){.block-container{padding:.7rem .8rem 3rem!important}.fe-upcoming{flex-direction:column;align-items:flex-start}.fe-free-hero h1{font-size:1.55rem!important}}
/* GOTHAM 1989 — unified visual layer */
:root{color-scheme:dark;--g-bg:#080d13;--g-panel:#111923;--g-gold:#f4c747}
[data-testid="stAppViewContainer"]{background:radial-gradient(ellipse at 85% 0%,#1c2732,#0b1017 55%,#070a0f)!important}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#05080d,#131c26)!important}
.block-container{max-width:1510px!important}
h1{font-size:clamp(1.8rem,3vw,2.7rem)!important}
[data-testid="stMetric"],[data-testid="stVerticalBlockBorderWrapper"]{background:#131b26!important;border:1px solid #6c5625!important;border-radius:14px!important}
[data-testid="stSelectbox"] [data-baseweb="select"]>div,
[data-testid="stDateInput"] [data-baseweb="input"]>div,
[data-testid="stNumberInput"] [data-baseweb="input"]>div,
[data-testid="stTextInput"] [data-baseweb="input"]>div{background:#192330!important;color:#f6e9c8!important;border:1px solid #7d632b!important}
[data-baseweb="popover"],[role="listbox"],[role="option"]{background:#192330!important;color:#fff2d0!important}
[data-baseweb="slider"] [role="slider"]{background:#f4c747!important;border:2px solid #ffe49a!important}
[data-baseweb="slider"] [data-testid="stTickBar"]{color:#d8caa7!important}
[data-testid="stCheckbox"] input,[data-testid="stRadio"] input{accent-color:#f4c747!important}
[data-testid="stSegmentedControl"] button{background:#1a2430!important;color:#e9dfc8!important;border:1px solid #67562d!important}
[data-testid="stSegmentedControl"] button[aria-pressed="true"]{background:#f4c747!important;color:#10151b!important}
[data-testid="stProgress"] [role="progressbar"]>div{background:#f4c747!important}
.stButton button{background:#18212c!important;color:#f8d66a!important;border:1px solid #8b6e2b!important}
.stButton button[kind="primary"]{background:linear-gradient(90deg,#dca626,#ffdf70)!important;color:#101319!important}
.gotham-table{width:100%!important;table-layout:fixed;border-collapse:separate;border-spacing:0 5px;color:#eee8d9!important}
.gotham-table th{background:#25303c!important;color:#ffd76a!important;text-align:left;padding:13px!important}
.gotham-table td{background:#141e29!important;border-top:1px solid #3a3c36!important;border-bottom:1px solid #3a3c36!important;padding:13px!important;overflow-wrap:anywhere}
.gotham-table tr td:first-child{border-left:3px solid #c59b37!important}
[data-testid="stDataFrame"],[data-testid="stTable"]{background:#111923!important}
.fe-panel{margin-bottom:0!important;border-bottom-left-radius:0!important;border-bottom-right-radius:0!important}
.fe-dashboard-panel{border-color:#8b6e2b!important}
@media(max-width:750px){.gotham-table th,.gotham-table td{padding:7px 4px!important;font-size:11px!important}.block-container{padding-left:.7rem!important;padding-right:.7rem!important}}


/* FIT EVOLUTION — GOTHAM 1989 / FINITIONS V6.4 */
:root{color-scheme:dark;--g-gold:#f4c747;--g-bright:#ffdc69;--g-bg:#090e15;--g-card:#131d29;--g-border:#76602c}
html,body,[data-testid="stAppViewContainer"]{color:#f3f1eb!important}
[data-testid="stAppViewContainer"]{background:radial-gradient(ellipse at 100% 0%,#1a2835 0%,#0d141d 48%,#080c12 100%)!important}
[data-testid="stHeader"]{background:#080c12ed!important}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#05080d,#111a25)!important;border-right:1px solid #94732e!important}
[data-testid="stSidebar"] [role="radiogroup"] label{border-radius:11px!important;margin:3px 0!important;min-height:40px;transition:background .18s,border-color .18s}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked){background:linear-gradient(100deg,#b98d2c,#ffe078)!important;border:1px solid #f7d45e!important}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) *{color:#10151d!important;font-weight:750!important}
[data-testid="stSidebar"] [role="radiogroup"] label:hover:not(:has(input:checked)){background:#202d3b!important}
.block-container{max-width:1510px!important;padding-top:1.5rem!important;padding-bottom:3rem!important}
h1,h2,h3{letter-spacing:.012em!important}h1{line-height:1.16!important;margin-bottom:.8rem!important}
[data-testid="stMetric"], [data-testid="stVerticalBlockBorderWrapper"]{background:#131d29!important;border:1px solid #715b2a!important;border-radius:15px!important;box-shadow:0 8px 24px #0003!important}
[data-testid="stMetric"]{padding:16px 18px!important;min-height:108px!important}
[data-testid="stMetricValue"]{color:#ffdc69!important;font-weight:700!important}
.fe-panel{border-radius:14px!important;margin:12px 0!important;background:#131d29!important}
.fe-top,.hero,.fe-welcome,.fe-free-hero{background:linear-gradient(108deg,#0c1420 0%,#1b2b3a 66%,#44391c 100%)!important;border:1px solid #b78b30!important;border-radius:16px!important;box-shadow:0 10px 28px #0004!important}
.fe-top{padding:18px 22px!important}.fe-upcoming{border-color:#6f5927!important}
.stButton>button,.stDownloadButton>button{border-radius:10px!important;min-height:42px!important;transition:filter .15s,transform .15s,background .15s!important}
.stButton>button:hover,.stDownloadButton>button:hover{filter:brightness(1.15)!important;border-color:#f4c747!important}
.stButton>button:active{transform:translateY(1px)!important}
.stButton>button[kind="primary"],button[kind="primary"]{background:linear-gradient(95deg,#dca626,#ffdc69)!important;color:#111720!important;border:1px solid #f7d25c!important}
[data-testid="stTextInput"] input,[data-testid="stNumberInput"] input,[data-testid="stDateInput"] input,[data-testid="stSelectbox"] [data-baseweb="select"]>div,[data-testid="stTextArea"] textarea{background:#192533!important;color:#f7eed7!important;border:1px solid #77612f!important;border-radius:9px!important}
[data-testid="stTextInput"] input:focus,[data-testid="stNumberInput"] input:focus,[data-testid="stTextArea"] textarea:focus{border-color:#f4c747!important;box-shadow:0 0 0 1px #f4c747!important}
[data-baseweb="popover"],[role="listbox"],[role="option"]{background:#192533!important;color:#fff0d0!important}
[data-testid="stSlider"] [role="slider"]{background:#f4c747!important;border-color:#ffe59c!important}
[data-testid="stProgress"] [role="progressbar"]{background:#283443!important;border-radius:99px!important;overflow:hidden!important}
[data-testid="stProgress"] [role="progressbar"]>div{background:linear-gradient(90deg,#c99420,#ffe078)!important}
[data-testid="stSegmentedControl"] button{background:#1c2937!important;color:#f4ebd8!important;border:1px solid #75602d!important}
[data-testid="stSegmentedControl"] button[aria-pressed="true"], [data-testid="stSegmentedControl"] button[aria-checked="true"]{background:#f4c747!important;color:#10151b!important}
[data-testid="stAlert"]{background:#203148!important;border:1px solid #65552e!important;border-radius:10px!important}
[data-testid="stExpander"]{background:#131d29!important;border:1px solid #6f5929!important;border-radius:11px!important;overflow:hidden!important;margin-bottom:9px!important}
[data-testid="stExpander"] summary:hover{background:#1d2b3b!important}
.gotham-table{width:100%!important;table-layout:fixed!important;border-collapse:separate!important;border-spacing:0!important;border:1px solid #78602a!important;border-radius:13px!important;overflow:hidden!important;font-size:clamp(12px,1vw,14px)!important}
.gotham-table th{background:#283441!important;color:#ffdc69!important;padding:13px!important;border-bottom:1px solid #77602a!important}
.gotham-table td{background:#121d29!important;color:#f3ead8!important;padding:12px!important;border-bottom:1px solid #33404d!important;overflow-wrap:anywhere!important}
.gotham-table tbody tr:nth-child(even) td{background:#182432!important}
.gotham-table tbody tr:hover td{background:#253347!important}
.gotham-table tr:last-child td{border-bottom:0!important}
.gotham-table tr td:first-child{border-left:0!important}
[data-testid="stDataFrame"],[data-testid="stTable"]{border-radius:12px!important;overflow:hidden!important}
:focus-visible{outline:2px solid #ffda67!important;outline-offset:2px!important}
@media(max-width:850px){.block-container{padding:1rem .75rem 3rem!important}.fe-top{padding:14px!important;flex-wrap:wrap!important}.fe-top strong{font-size:21px!important}.gotham-table th,.gotham-table td{padding:8px 5px!important;font-size:11px!important}h1{font-size:clamp(1.6rem,5vw,2.15rem)!important}}
@media(max-width:480px){[data-testid="stMetric"]{min-height:90px!important;padding:12px!important}.fe-panel{padding:12px!important}.fe-upcoming{gap:5px!important}.block-container{padding-left:.55rem!important;padding-right:.55rem!important}}
@media(prefers-reduced-motion:reduce){*,*:before,*:after{transition:none!important;animation:none!important}}


/* V6.5 — finitions : contrastes, jauges, composants et mobile */
[data-testid="stProgress"] [role="progressbar"] > div {width:auto;max-width:100%;}
[data-testid="stProgress"] [role="progressbar"]{background:#263341!important}
[data-testid="stProgress"] [role="progressbar"] > div {background:linear-gradient(90deg,#d9a32c,#ffdf70)!important}
[data-testid="stSlider"] [data-baseweb="slider"] [role="slider"], [data-baseweb="slider"] [role="slider"]{background:#f4c747!important;border:2px solid #ffe39b!important}
[data-testid="stSlider"] [data-baseweb="slider"] > div > div{accent-color:#f4c747}
[data-testid="stFormSubmitButton"] button{background:#dba82d!important;color:#101720!important;border-color:#f4c747!important;font-weight:700!important}
[data-testid="stFormSubmitButton"] button:hover{background:#ffdc68!important;color:#101720!important}
[data-testid="stSegmentedControl"] button{color:#f8e9c8!important;background:#1a2735!important}
[data-testid="stSegmentedControl"] button[aria-pressed="true"], [data-testid="stSegmentedControl"] button[aria-checked="true"]{background:#e3b43c!important;color:#111923!important}
[data-testid="stSelectbox"] [data-baseweb="select"]>div{background:#1b2837!important;color:#fff1d0!important}
[data-testid="stSelectbox"] [data-baseweb="select"] *{color:inherit}
[data-testid="stMetric"]{min-width:0!important}
@media(max-width:800px){.block-container{padding-left:1rem!important;padding-right:1rem!important}.fe-top{gap:8px!important}.gotham-table{font-size:12px!important}.gotham-table th,.gotham-table td{padding:8px 5px!important}}
</style>"""

@st.cache_data(ttl=1200,show_spinner=False)
def weather(city):
 # Geocoding + weather: no API key, no device geolocation.
 city=(city or 'Paris').strip()[:80]
 def get(url):
  req=Request(url,headers={'User-Agent':'FitEvolution/5.4 (personal weather dashboard)'})
  with urlopen(req,timeout=5) as resp:return json.load(resp)
 geo=get('https://geocoding-api.open-meteo.com/v1/search?'+urlencode({'name':city,'count':1,'language':'fr','format':'json'}))
 places=geo.get('results') or []
 if not places:return None
 place=places[0]
 data=get('https://api.open-meteo.com/v1/forecast?'+urlencode({'latitude':place['latitude'],'longitude':place['longitude'],'current':'temperature_2m,weather_code','timezone':'auto'}))
 curr=data.get('current') or {}
 code=int(curr.get('weather_code',0))
 label='Ciel dégagé' if code<=1 else 'Nuageux' if code<=3 else 'Brouillard' if code<=48 else 'Pluie' if code<=67 else 'Neige' if code<=77 else 'Averses / orage'
 icon='☀️' if code<=1 else '⛅' if code<=3 else '🌫️' if code<=48 else '🌧️' if code<=67 else '❄️' if code<=77 else '⛈️'
 return {'city':place['name'],'temp':curr.get('temperature_2m'),'label':label,'icon':icon}

def header():
 city=st.session_state.get('fe_weather_city','Paris')
 try: w=weather(city)
 except Exception:w=None
 cityname=html.escape(w['city'] if w else city)
 wx=(f"{w['icon']} {w['temp']}°C · {html.escape(w['label'])}" if w and w['temp'] is not None else 'Météo indisponible · connexion requise')
 # iframe browser clock keeps time without rerunning Streamlit.
 markup="""<div style="background:linear-gradient(115deg,#080a0e,#2a2e35 72%,#57471d);border-radius:14px;color:white;padding:14px 20px;font:15px system-ui;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px"><div><b style="font-size:24px">🦇 Fit Evolution <small style="font-size:12px">GOTHAM 1989</small></b><div style="font-size:12px;color:#f2c230">Ton coach sportif · Ta progression · Ta motivation</div></div><div style="background:#15191f;color:#f2c230;padding:10px 18px;border-radius:12px;min-width:220px;text-align:center"><div id="day" style="font-size:12px"></div><b id="clock" style="font-size:25px"></b><div style="font-size:13px">__CITY__ · __WX__</div></div></div><script>function tick(){let d=new Date();document.getElementById('day').textContent=new Intl.DateTimeFormat('fr-FR',{weekday:'long',day:'numeric',month:'long',year:'numeric'}).format(d);document.getElementById('clock').textContent=d.toLocaleTimeString('fr-FR',{hour12:false});}tick();setInterval(tick,1000);</script>"""
 components.html(markup.replace('__CITY__',cityname).replace('__WX__',wx),height=125)

def overview(p,prog,ws):
 st.title('Vue d’ensemble de ma progression')
 s=c.summary(); done=s['done']; calories=m.calories_history(); recent=j.daily(7)
 today=date.today().isoformat(); today_row=next((r for r in recent if r['day']==today),None)
 a,b,d,e=st.columns(4)
 a.metric('🏋️ Séances terminées',done)
 b.metric('🔥 Streak',s['streak'])
 d.metric('👟 Pas aujourd’hui',f'{j.steps(today):,}'.replace(',',' '))
 e.metric('⭐ Niveau',s['level'])
 a,b=st.columns([1.1,1])
 with a:
  st.markdown('<div class="fe-panel"><h3>📈 Mes tendances</h3></div>',unsafe_allow_html=True)
  weights=m.weight_history()
  if weights:
   import pandas as pd
   import altair as alt
   df=pd.DataFrame(weights);df['Date']=pd.to_datetime(df['measured'])
   df['Poids (kg)']=pd.to_numeric(df['weight'],errors='coerce')
   df=df.dropna(subset=['Date','Poids (kg)'])
   if not df.empty:
    chart=(alt.Chart(df).mark_line(color='#f4c746',strokeWidth=3,point=alt.OverlayMarkDef(color='#f4c746',size=65))
      .encode(x=alt.X('Date:T',axis=alt.Axis(title=None,labelColor='#bac4d0',gridColor='#273341',format='%d/%m')),
              y=alt.Y('Poids (kg):Q',scale=alt.Scale(zero=False),axis=alt.Axis(labelColor='#bac4d0',titleColor='#e6d19b',gridColor='#273341')),
              tooltip=[alt.Tooltip('Date:T',format='%d/%m/%Y'),alt.Tooltip('Poids (kg):Q',format='.1f')])
      .properties(height=265,background='#111822').configure_view(strokeOpacity=0).configure_axis(labelColor='#d4dbe5',titleColor='#f7ca50',gridColor='#283445').configure_legend(labelColor='#d4dbe5',titleColor='#f7ca50'))
    st.altair_chart(chart,use_container_width=True,theme=None)
  else:st.info('Enregistre tes premières pesées dans Progression pour voir la courbe.')
  st.caption('Poids enregistré, sans projection automatique sur la courbe.')
 with b:
  st.markdown('<div class="fe-panel"><h3>🎯 Prochaines séances</h3></div>',unsafe_allow_html=True)
  upcoming=[w for w in ws if w['status']=='planned'][:4]
  if upcoming:
   for w in upcoming:
    title=html.escape(str(w['title']));day=html.escape(str(w['planned_date']))
    st.markdown(f'<div class="fe-upcoming">🏋️ <strong>{title}</strong><small>📅 {day}</small></div>',unsafe_allow_html=True)
  else:st.info('Aucune séance à venir : crée ton programme.')
  try:
   import seance_libre as free
   free_rows=free.history()
   if free_rows:
    st.markdown('<div class="fe-dashboard-panel"><h3>🦇 Séances libres récentes</h3>',unsafe_allow_html=True)
    for r in free_rows[:3]:
     st.markdown(f'<div class="fe-upcoming">{html.escape(str(r["completed_at"])[:10])} · {int(r["duration"])} min · {int(r["estimated_kcal"])} kcal estimées</div>',unsafe_allow_html=True)
    st.markdown('</div>',unsafe_allow_html=True)
  except Exception:pass
 st.markdown('### 📊 Bilan des 7 derniers jours')
 report=c.weekly_report();a,b,d=st.columns(3)
 a.metric('Séances effectuées',report['done'])
 b.metric('Séances prévues',report['scheduled'])
 try:
  import seance_libre as free
  free_cal=sum(int(r['estimated_kcal']) for r in free.history())
 except Exception:free_cal=0
 d.metric('Calories sport estimées (historique)',f"{sum(x['estimated_kcal'] for x in calories)+free_cal:.0f} kcal")
 st.caption('Les calories sportives sont des estimations et le total affiché couvre tout l’historique enregistré.')


def welcome():
 st.markdown('<div class="fe-welcome"><h1>Bienvenue sur Fit Evolution 💪</h1><p>Ton espace personnel pour t’entraîner et suivre ta progression.</p></div>',unsafe_allow_html=True)
 a,b,c1,d=st.columns(4)
 a.metric('⚖️ Poids actuel','À renseigner')
 b.metric('🎯 Objectif','À définir')
 c1.metric('🏋️ Séances','0')
 d.metric('👟 Pas du jour','—')

def coach_page(p,prog,ws):
 st.title('📈 Mon bilan coach hebdomadaire')
 st.caption('Bilan indicatif : aide à observer les tendances, sans diagnostic ni restriction calorique automatique.')
 with st.expander('🌤️ Ville pour la météo du tableau de bord'):
  city=st.text_input('Ville',value=st.session_state.get('fe_weather_city','Paris'),max_chars=80)
  if st.button('Mettre à jour la météo'):
   st.session_state['fe_weather_city']=city.strip() or 'Paris';st.rerun()
 report=c.weekly_report();history=m.weight_history();daily=j.daily(7)
 total_steps=sum(int(x['steps']) for x in daily)
 a,b,d=st.columns(3)
 a.metric('Séances / 7 jours',f"{report['done']} / {report['scheduled']}")
 b.metric('Pas saisis / 7 jours',f'{total_steps:,}'.replace(',',' '))
 d.metric('Pesées enregistrées',len(history))
 st.subheader('📏 Tour de taille')
 with st.form('waist_v54'):
  waist=st.number_input('Tour de taille mesuré (cm)',min_value=40.0,max_value=200.0,value=85.0,step=.5)
  when=st.date_input('Date de mesure',date.today())
  if st.form_submit_button('Enregistrer la mesure'):save_waist(when.isoformat(),waist);st.success('Tour de taille enregistré.');st.rerun()
 rows=waist_history()
 if rows:
  import pandas as pd
  df=pd.DataFrame(rows);df['Date']=pd.to_datetime(df['day']);st.line_chart(df.set_index('Date')['waist_cm'],color='#8d2a49')
  if len(rows)>=2:st.write(f"Évolution mesurée : **{rows[-1]['waist_cm']-rows[0]['waist_cm']:+.1f} cm**")
 st.subheader('💬 Conseils de ton coach')
 for tip in c.recommendations():st.info(tip)
 if report['scheduled'] and report['done']<report['scheduled']:
  st.write('La régularité compte, mais les séances manquées ne doivent pas être compensées par un HIIT excessif.')
 if total_steps==0:st.write('Tu peux enregistrer tes pas dans Objectifs de pas pour suivre ton activité quotidienne.')
 fc=j.weight_forecast()
 if fc['status']=='ok':st.write(f"Tendance des pesées : **{fc['weekly_change']:+.2f} kg/semaine**, avec une forte incertitude. Ce n’est pas une prévision fiable du poids de demain.")
 else:st.caption('La projection du poids nécessite au moins 3 pesées réparties sur 14 jours.')
 st.caption('La graisse abdominale ne se réduit pas localement : suis la tendance du tour de taille, ton énergie et tes performances.')

def init():
 with m.connect() as db:
  db.execute('CREATE TABLE IF NOT EXISTS waist_log(day TEXT PRIMARY KEY,waist_cm REAL NOT NULL CHECK(waist_cm BETWEEN 40 AND 200))')

def save_waist(day,cm):
 with m.connect() as db:db.execute('INSERT INTO waist_log(day,waist_cm) VALUES(?,?) ON CONFLICT(day) DO UPDATE SET waist_cm=excluded.waist_cm',(day,float(cm)))

def waist_history():return m.all_rows('SELECT day,waist_cm FROM waist_log ORDER BY day')
init()
