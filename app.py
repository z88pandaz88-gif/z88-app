import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Z88 Global Engine", layout="wide")

# دالة لتنظيف ملفك الخاص
def load_and_clean_data(file):
    df = pd.read_csv(file)
    # تنظيف أي مسافات مخفية في أسماء الأعمدة
    df.columns = [c.strip() for c in df.columns]
    # تنظيف الأكواد
    df['الرمز'] = df['الرمز'].astype(str).str.strip()
    return df

# دالة جلب الداتا القديمة (الـ History)
def get_historical_data(ticker):
    try:
        # إضافة .CA للأكواد المصرية
        full_ticker = f"{ticker}.CA"
        data = yf.download(full_ticker, period="2y", interval="1d", progress=False)
        return data
    except:
        return None

st.title("🛡️ محرك Z88 الذكي (تحليل شامل)")

# رفع ملفك المرفق
uploaded_file = st.sidebar.file_uploader("ارفع ملف Prices, support & Resistance", type="csv")

if uploaded_file:
    df = load_and_clean_data(uploaded_file)
    st.sidebar.success("✅ تم قبول ملفك وتنظيف البيانات")

    # الأقسام المطلوبة
    tab_list = ["البحث & الداتا القديمة", "إليوت & زوايا جان", "الزمن & السيولة", "المحفظة & الحيتان"]
    tabs = st.tabs(tab_list)

    # القسم الأول: البحث وجلب الداتا القديمة من الإنترنت
    with tabs[0]:
        search_ticker = st.text_input("ادخل كود السهم (مثلاً COMI):").upper()
        if search_ticker:
            # 1. الداتا اللحظية من ملفك
            current_data = df[df['الرمز'] == search_ticker]
            
            if not current_data.empty:
                st.subheader(f"📊 تحليل السهم: {current_data.iloc[0]['اسم الشركه']}")
                
                # 2. جلب الداتا القديمة فوراً
                hist_data = get_historical_data(search_ticker)
                
                if hist_data is not None:
                    # رسم شارت يدمج بين الماضي (ياهو) والحاضر (ملفك)
                    fig = go.Figure(data=[go.Candlestick(x=hist_data.index,
                                    open=hist_data['Open'], high=hist_data['High'],
                                    low=hist_data['Low'], close=hist_data['Close'])])
                    fig.update_layout(title="التاريخ السعري (سنتين) + جلسة اليوم", template="plotly_dark")
                    st.plotly_chart(fig, use_container_width=True)
                    
                else:
                    st.warning("⚠️ تعذر جلب الداتا القديمة من ياهو، جاري استخدام بيانات ملفك فقط.")

    # القسم الثاني: زوايا جان وإليوت (تستخدم الداتا المدمجة)
    with tabs[1]:
        if search_ticker and not current_data.empty:
            price = current_data.iloc[0]['إغلاق']
            root = np.sqrt(price)
            st.write(f"### 📐 زوايا جان للسعر {price}")
            st.info(f"زاوية 180 (انعكاس): {(root + 1)**2:.2f}")
            st.info(f"زاوية 360 (دورة): {(root + 2)**2:.2f}")
            
            st.write("### 🌊 مستهدفات إليوت (Z88)")
            st.success(f"مستهدف الموجه الثالثة (161.8%): {price * 1.618:.2f}")

    # زر سحب إكسيل لكل السوق
    st.sidebar.divider()
    full_csv = df.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button("📥 سحب تحليل السوق بالكامل", full_csv, "Z88_Full_Report.csv")

else:
    st.info("💡 من فضلك ارفع ملفك (Prices, support & Resistance) من القائمة الجانبية.")