import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta

# إعدادات الواجهة
st.set_page_config(page_title="Z88 AI Agent", layout="wide")

# 1. تنظيف البيانات ومنع تكرار الأعمدة (حل مشكلة الـ Logs)
def fix_data(df):
    df.columns = [str(c).strip() for c in df.columns]
    df = df.loc[:, ~df.columns.duplicated()]
    return df

# 2. محرك الـ AI Agent (تحليل Z88 و Z6)
def run_ai_agent(ticker):
    try:
        # جلب البيانات وحل مشكلة الـ Multi-index اللي كانت في الـ Logs
        hist = yf.download(f"{ticker}.CA", period="150d", progress=False)
        if isinstance(hist.columns, pd.MultiIndex):
            hist.columns = hist.columns.get_level_values(0)
        
        if hist.empty: return None

        # حسابات الوكيل الذكي
        last_p = hist['Close'].iloc[-1]
        vol_avg = hist['Volume'].tail(20).mean()
        curr_vol = hist['Volume'].iloc[-1]
        h_20 = hist['High'].tail(20).max()
        l_20 = hist['Low'].tail(20).min()

        # نموذج Z88: اختراق قمة مع سيولة انفجارية
        if last_p >= h_20 and curr_vol > vol_avg * 1.5:
            return {"model": "Z88 - انفجار سعري 🚀", "score": 95, "desc": "الوكيل اكتشف اختراقاً قوياً مع دخول سيولة مؤسساتية.", "data": hist}
        
        # نموذج Z6: ارتداد من قاع مع فوليوم شرائي
        elif last_p <= l_20 * 1.05 and curr_vol > vol_avg:
            return {"model": "Z6 - قناص القاع 🏹", "score": 88, "desc": "الوكيل يرى منطقة تجميع مثالية وارتداد وشيك من القاع.", "data": hist}
        
        return None
    except: return None

# الواجهة الرئيسية
st.title("🤖 وكيل Z88 للذكاء الاصطناعي")
st.write("الوكيل يقوم الآن بمسح الصور والبيانات لتحديد نماذج الانفجار.")

file = st.sidebar.file_uploader("ارفع ملف الأسعار", type=["csv", "xlsx"])

if file:
    df = fix_data(pd.read_excel(file) if file.name.endswith('.xlsx') else pd.read_csv(file))
    st.sidebar.success("تم تفعيل الوكيل!")

    mode = st.radio("اختر المهمة:", ["مسح السوق بالكامل", "تحليل سهم محدد"])

    if mode == "تحليل سهم محدد":
        ticker = st.selectbox("اختر السهم:", df['الرمز'].unique())
        res = run_ai_agent(ticker)
        
        if res:
            col1, col2 = st.columns([2, 1])
            with col2:
                st.subheader("🧠 تقرير الوكيل")
                st.success(f"النموذج: {res['model']}")
                st.metric("قوة الإشارة", f"{res['score']}%")
                st.write(res['desc'])
            with col1:
                fig = go.Figure(data=[go.Candlestick(x=res['data'].index, open=res['data']['Open'], high=res['data']['High'], low=res['data']['Low'], close=res['data']['Close'])])
                fig.update_layout(template="plotly_dark", height=400)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("السهم لا يحقق شروط Z88 أو Z6 حالياً.")
            
    else:
        if st.button("ابدأ مسح الـ AI للسوق"):
            findings = []
            for t in df['الرمز'].unique()[:30]: # مسح عينة من السوق
                r = run_ai_agent(t)
                if r: findings.append({"الرمز": t, "النموذج": r['model'], "القوة": f"{r['score']}%"})
            
            if findings: st.table(pd.DataFrame(findings))
            else: st.info("لم يتم العثور على فرص مطابقة للنماذج حالياً.")



### يعني إيه الكلام ده ببساطة؟
* **Z88:** ده "الوحش" بتاعنا، بيدور على سهم بيخترق قمة والناس بتهجم عليه بسيولة (فوليوم) كبيرة.
* **Z6:** ده "القناص"، بيدور على سهم نزل كتير وبدأ يلم (تجميع) عند قاع الـ 20 يوم اللي فاتوا.
* **الوكيل (Agent):** هو اللي بيقوم بالليل والنهار يفتح "صور" الشارتات دي ويطلعلك الخلاصة عشان متتعبش نفسك في البحث اليدوي.

**إنجز وارفع الكود ده، وقولي لو محتاج الوكيل يركز على سهم معين أو يبعتلك تنبيهات بطريقة تانية؟**
