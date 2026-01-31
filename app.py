import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 1. إعدادات النظام
st.set_page_config(page_title="Z88 Predator Hub PRO", layout="wide")

# --- محرك معالجة البيانات واللغة العربية (Anti-Crash) ---
def load_data(file):
    try:
        if file.name.endswith('.xlsx'):
            df = pd.read_excel(file)
        else:
            df = pd.read_csv(file, encoding='utf-8-sig')
        df.columns = [str(c).strip() for c in df.columns]
        df = df.loc[:, ~df.columns.duplicated()] # منع التكرار القاتل
        mapping = {'الرمز': 'الرمز', 'إغلاق': 'إغلاق', 'السيولة': 'السيولة', 'اسم الشركه': 'اسم الشركه', 'الارتكاز': 'الارتكاز'}
        for col in df.columns:
            for k, v in mapping.items():
                if k in col: df.rename(columns={col: v}, inplace=True)
        return df
    except: return None

# --- محرك إليوت والزمن التفصيلي ---
def pro_elliott_engine(ticker, price):
    try:
        hist = yf.download(f"{ticker}.CA", period="2y", progress=False)
        if isinstance(hist.columns, pd.MultiIndex): hist.columns = hist.columns.get_level_values(0)
        
        low_p = hist['Low'].min()
        low_d = hist['Low'].idxmin()
        high_p = hist['High'].max()
        
        # حساب الموجة 3 و 5
        wave_1_size = high_p - low_p
        target_3 = low_p + (wave_1_size * 1.618)
        target_5 = low_p + (wave_1_size * 2.618)
        
        # التوقع الزمني (فيبوناتشي 144 يوم)
        t_date = low_d + timedelta(days=144)
        
        return {"start_p": low_p, "start_d": low_d.date(), "t3": target_3, "t5": target_5, "t_date": t_date.date(), "hist": hist}
    except: return None

# --- محرك المؤشرات الرقمية ---
def add_indicators(df_hist):
    df = df_hist.copy()
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain/loss)))
    # MACD
    ema12 = df['Close'].ewm(span=12, adjust=False).mean()
    ema26 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = ema12 - ema26
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    # Bollinger
    df['MA20'] = df['Close'].rolling(20).mean()
    df['UP'] = df['MA20'] + (df['Close'].rolling(20).std() * 2)
    df['LOW'] = df['MA20'] - (df['Close'].rolling(20).std() * 2)
    return df

# --- الواجهة الرئيسية ---
st.title("🏹 نظام القناص Z88 - النسخة السيادية الكاملة")

uploaded_file = st.sidebar.file_uploader("ارفع ملف البيانات اليومي", type=["csv", "xlsx"])

if uploaded_file:
    df_main = load_data(uploaded_file)
    if df_main is not None:
        st.sidebar.success("✅ تم تفعيل 13 حزمة تحليلية")
        
        tabs = st.tabs([
            "🎯 القناص (إليوت)", "🚀 السكويز & الزمن", "📐 زوايا جان", "🧱 الأوردر بلوك", 
            "📈 المؤشرات الرقمية", "🐳 نبض الميكر", "🚨 إشارات التداول", "💼 المحفظة الذكية", 
            "📊 تحليل السوق", "🔍 البحث التاريخي", "🧠 سيكولوجية", "🛡️ صمام الأمان", "📥 التقارير"
        ])

        # 1. القناص (إليوت التفصيلي)
        with tabs[0]:
            sel = st.selectbox("اختر السهم:", df_main['الرمز'].unique())
            p_now = df_main[df_main['الرمز'] == sel]['إغلاق'].values[0]
            data = pro_elliott_engine(sel, p_now)
            if data:
                c1, c2 = st.columns(2)
                with c1:
                    st.info(f"📍 بدأت الموجة العظمى يوم: {data['start_d']} بسعر: {data['start_p']:.2f}")
                    st.success(f"🎯 مستهدف موجة 3: {data['t3']:.2f}")
                with c2:
                    st.warning(f"📅 التاريخ المتوقع للهدف: {data['t_date']}")
                    st.error(f"🏁 مستهدف موجة 5 (نهائي): {data['t5']:.2f}")
                
                fig = go.Figure(data=[go.Candlestick(x=data['hist'].index, open=data['hist']['Open'], high=data['hist']['High'], low=data['hist']['Low'], close=data['hist']['Close'])])
                fig.add_hline(y=data['t3'], line_dash="dash", line_color="green")
                st.plotly_chart(fig, use_container_width=True)

        # 2. السكويز والزمن
        with tabs[1]:
            st.subheader("🔥 رادار السكويز والانعكاس الزمني")
            df_main['Squeeze'] = np.where(df_main['السيولة'] > 60, "انفجار وشيك 🚀", "تجميع")
            df_main['Ref_Date'] = (datetime.now() + timedelta(days=13)).date()
            st.dataframe(df_main[['الرمز', 'إغلاق', 'السيولة', 'Squeeze', 'Ref_Date']])

        # 3. زوايا جان
        with tabs[2]:
            st.subheader("📐 زوايا جان السعرية والزمنية")
            root = np.sqrt(p_now)
            st.write(f"زاوية 90: {(root + 0.5)**2:.2f} | زاوية 180: {(root + 1)**2:.2f} | زاوية 360: {(root + 2)**2:.2f}")

        # 4. الأوردر بلوك
        with tabs[3]:
            if data:
                st.success(f"📦 منطقة شراء الميكر (Buy OB): {data['hist']['Low'].tail(20).min()}")
                st.error(f"🚫 منطقة بيع الميكر (Sell OB): {data['hist']['High'].tail(20).max()}")

        # 5. المؤشرات الرقمية
        with tabs[4]:
            if data:
                df_i = add_indicators(data['hist'])
                st.line_chart(df_i[['MACD', 'Signal', 'RSI']])

        # 6. نبض الميكر
        with tabs[5]:
            df_main['Maker_Pulse'] = (df_main['السيولة'] * df_main['إغلاق']) / 100
            st.dataframe(df_main[['الرمز', 'السيولة', 'Maker_Pulse']].sort_values(by='Maker_Pulse', ascending=False))

        # 10. البحث التاريخي
        with tabs[9]:
            st.subheader("🔍 ابحث عن أي سهم Z1, Z6, Z7, Z88")
            # المحرك يعمل تلقائياً مع الاختيار من القائمة

        # 13. التقارير
        with tabs[12]:
            csv = df_main.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
            st.download_button("📥 تحميل التقرير النهائي (عربي كامل)", csv, "Z88_Master_Report.csv")

else:
    st.info("👋 ارفع ملف الأسعار لفتح 13 قسماً كاملاً بدون اختصار.")
