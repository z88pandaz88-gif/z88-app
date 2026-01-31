import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta

# إعدادات النظام السيادي
st.set_page_config(page_title="Z88 AI Predator Agent", layout="wide")

# --- 1. محرك معالجة البيانات (حل مشاكل الـ Logs) ---
def clean_and_fix_df(df):
    # مسح المسافات وحل تكرار الأعمدة
    df.columns = [str(c).strip() for c in df.columns]
    df = df.loc[:, ~df.columns.duplicated()]
    return df

# --- 2. وكيل تحليل النماذج (Z88 & Z6 AI Logic) ---
def ai_agent_scan(ticker):
    try:
        # جلب البيانات وحل مشكلة الـ Multi-index فوراً
        hist = yf.download(f"{ticker}.CA", period="150d", progress=False)
        if isinstance(hist.columns, pd.MultiIndex):
            hist.columns = hist.columns.get_level_values(0)
        
        if hist.empty: return None

        last_close = hist['Close'].iloc[-1]
        vol_avg = hist['Volume'].rolling(20).mean().iloc[-1]
        curr_vol = hist['Volume'].iloc[-1]
        high_20 = hist['High'].rolling(20).max().iloc[-1]
        low_20 = hist['Low'].rolling(20).min().iloc[-1]

        # منطق نموذج Z88 (انفجار اختراق مع سيولة)
        if last_close >= high_20 and curr_vol > vol_avg * 1.5:
            return {"model": "Z88 - انفجار اختراق 🚀", "score": 95, "action": "دخول تأكيدي", "data": hist}
        
        # منطق نموذج Z6 (ارتداد قاع مع فوليوم شرائي)
        elif last_close <= low_20 * 1.05 and curr_vol > vol_avg:
            return {"model": "Z6 - قناص القاع 🏹", "score": 88, "action": "تجميع مبكر", "data": hist}
        
        return {"model": "بحث عن فرصة...", "score": 0, "action": "مراقبة", "data": hist}
    except:
        return None

# --- الواجهة الرئيسية ---
st.title("🤖 وكيل الذكاء الاصطناعي القناص (Z88 & Z6)")
st.markdown("---")

file = st.sidebar.file_uploader("ارفع ملف الأسهم اليومي", type=["csv", "xlsx"])

if file:
    df_raw = pd.read_excel(file) if file.name.endswith('.xlsx') else pd.read_csv(file, encoding='utf-8-sig')
    df = clean_and_fix_df(df_raw)
    
    st.sidebar.success("تم تفعيل الوكيل الذكي بنجاح ✅")
    
    # اختيار وضع المسح
    mode = st.radio("اختر مهمة الوكيل:", ["تحليل سهم محدد (Detailed Visual)", "مسح السوق (AI Market Scanner)"])

    if mode == "تحليل سهم محدد (Detailed Visual)":
        ticker = st.selectbox("اختر السهم ليرسل الوكيل تقريره:", df['الرمز'].unique())
        
        with st.spinner('الوكيل يقوم بتصوير وتحليل الشارت الآن...'):
            res = ai_agent_scan(ticker)
            
            if res and res['data'] is not None:
                c1, c2 = st.columns([2, 1])
                with c2:
                    st.subheader("🧠 رؤية الوكيل")
                    st.success(f"**النموذج:** {res['model']}")
                    st.info(f"**الإجراء المقترح:** {res['action']}")
                    st.metric("قوة الإشارة", f"{res['score']}%")
                
                with c1:
                    # رسم الشارت الذي يراه الـ AI
                    fig = go.Figure(data=[go.Candlestick(x=res['data'].index, open=res['data']['Open'], 
                                                         high=res['data']['High'], low=res['data']['Low'], 
                                                         close=res['data']['Close'])])
                    fig.update_layout(template="plotly_dark", height=450, title=f"تحليل الوكيل لـ {ticker}")
                    st.plotly_chart(fig, use_container_width=True)

                

    else: # وضع مسح السوق بالكامل
        if st.button("بدء عملية مسح الـ AI لكل الأسهم"):
            st.subheader("🔦 الأسهم التي لفتت انتباه الوكيل (موديل Z)")
            findings = []
            tickers = df['الرمز'].unique()
            
            for t in tickers:
                result = ai_agent_scan(t)
                if result and result['score'] > 80:
                    findings.append({"الرمز": t, "النموذج المكتشف": result['model'], "القوة": f"{result['score']}%", "التوصية": result['action']})
            
            if findings:
                st.table(pd.DataFrame(findings))
            else:
                st.warning("الوكيل لم يجد فرصاً محققة لشروط Z88 أو Z6 في هذه اللحظة.")

else:
    st.info("قم برفع ملفك وسأقوم بتشغيل الـ AI Agent فوراً.")
