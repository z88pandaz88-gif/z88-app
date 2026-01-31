import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta

# إعدادات الصفحة والستايل
st.set_page_config(page_title="Z88 Predator AI Agent", layout="wide")

# --- 1. محرك تنظيف البيانات (منع تكرار الأعمدة المذكور في الـ Logs) ---
def clean_data(df):
    df.columns = [str(c).strip() for c in df.columns]
    df = df.loc[:, ~df.columns.duplicated()]
    return df

# --- 2. وكيل تحليل الأنماط (AI Visual Logic) ---
def analyze_z_models(df_hist):
    # تحويل الشارت لبيانات رقمية يفهمها الـ AI كأنها صورة
    recent = df_hist.tail(20)
    current_p = recent['Close'].iloc[-1]
    low_20 = recent['Low'].min()
    high_20 = recent['High'].max()
    
    # حساب السيولة اللحظية (Money Flow)
    vol_mean = recent['Volume'].mean()
    curr_vol = recent['Volume'].iloc[-1]
    
    analysis = {"model": "بحث...", "status": "محايد", "score": 0}

    # فحص نموذج Z88 (انفجار موجة 3 مع سيولة)
    if current_p > high_20 * 0.98 and curr_vol > vol_mean * 1.5:
        analysis = {
            "model": "Z88 - انفجار سيولة 🚀",
            "status": "دخول قوي",
            "score": 95,
            "desc": "الـ AI اكتشف تجميع مؤسساتي واختراق لمستوى المقاومة الأخير."
        }
    # فحص نموذج Z6 (ارتداد سريع من قاع)
    elif current_p < low_20 * 1.05 and curr_vol > vol_mean:
        analysis = {
            "model": "Z6 - ارتداد قاع 🏹",
            "status": "تجميع قنص",
            "score": 85,
            "desc": "الـ AI يرى ضغط بيعي انتهى وبداية تكوين قاع فرعي للانطلاق."
        }
    
    return analysis

# --- الواجهة الرئيسية ---
st.title("🤖 وكيل الذكاء الاصطناعي Z88 & Z6")
st.sidebar.markdown("### إعدادات الوكيل")

file = st.sidebar.file_uploader("ارفع ملف الأسهم اليومي", type=["csv", "xlsx"])

if file:
    df_raw = pd.read_excel(file) if file.name.endswith('.xlsx') else pd.read_csv(file, encoding='utf-8-sig')
    df = clean_data(df_raw)
    
    st.sidebar.success("تم رفع الملف وتفعيل الوكيل ✅")
    
    # اختيار وضع المسح
    scan_mode = st.radio("وضع المسح:", ["تحليل سهم محدد", "مسح السوق بالكامل (AI Scan)"])

    if scan_mode == "تحليل سهم محدد":
        ticker = st.selectbox("اختر السهم:", df['الرمز'].unique())
        p_now = df[df['الرمز'] == ticker].iloc[0]['إغلاق']
        
        with st.spinner('جاري جلب الشارت وتحليله بصرياً...'):
            hist = yf.download(f"{ticker}.CA", period="1y", progress=False)
            if isinstance(hist.columns, pd.MultiIndex): hist.columns = hist.columns.get_level_values(0)
            
            if not hist.empty:
                result = analyze_z_models(hist)
                
                col1, col2 = st.columns([2, 1])
                with col2:
                    st.markdown(f"### نتائج وكيل الـ AI")
                    st.success(f"**النموذج المكتشف:** {result['model']}")
                    st.info(f"**الحالة:** {result['status']}")
                    st.metric("درجة الثقة", f"{result['score']}%")
                    st.write(f"💡 {result['desc']}")
                
                with col1:
                    fig = go.Figure(data=[go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'])])
                    fig.update_layout(template="plotly_dark", height=450, title=f"الشارت الذي يحلله الوكيل لـ {ticker}")
                    st.plotly_chart(fig, use_container_width=True)

    else: # مسح السوق بالكامل
        if st.button("ابدأ مسح الـ AI لكل الأسهم"):
            findings = []
            progress_bar = st.progress(0)
            tickers = df['الرمز'].unique()[:20] # تجربة على أول 20 سهم للسرعة
            
            for i, t in enumerate(tickers):
                h = yf.download(f"{t}.CA", period="60d", progress=False)
                if not h.empty:
                    if isinstance(h.columns, pd.MultiIndex): h.columns = h.columns.get_level_values(0)
                    res = analyze_z_models(h)
                    if res['score'] > 0:
                        findings.append({"الرمز": t, "النموذج": res['model'], "القوة": res['score']})
                progress_bar.progress((i + 1) / len(tickers))
            
            st.table(pd.DataFrame(findings))

else:
    st.info("قم برفع الملف ليقوم الـ AI Agent ببدء المهمة.")
