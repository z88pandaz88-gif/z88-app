import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 1. إعدادات النظام الاحترافية
st.set_page_config(page_title="Z88 Predator Master", layout="wide")

# دالة معالجة النصوص والملفات (عربي 100%)
def load_and_clean(file):
    try:
        df = pd.read_excel(file) if file.name.endswith('.xlsx') else pd.read_csv(file, encoding='utf-8-sig')
        df.columns = [str(c).strip() for c in df.columns]
        # منع تكرار الأعمدة (حل مشكلة الـ Logs)
        df = df.loc[:, ~df.columns.duplicated()]
        mapping = {'الرمز': 'الرمز', 'إغلاق': 'إغلاق', 'السيولة': 'السيولة', 'اسم الشركه': 'اسم الشركه', 'الارتكاز': 'الارتكاز'}
        for col in df.columns:
            for k, v in mapping.items():
                if k in col: df.rename(columns={col: v}, inplace=True)
        return df
    except: return None

# دالة محرك البحث والتحليل (إليوت + مؤشرات + جان)
def get_full_analysis(ticker, current_p):
    try:
        # جلب البيانات التاريخية ومعالجة مشكلة الـ Multi-index
        hist = yf.download(f"{ticker}.CA", period="2y", progress=False)
        if isinstance(hist.columns, pd.MultiIndex): hist.columns = hist.columns.get_level_values(0)
        if hist.empty: return None

        # --- 1. تحليل إليوت والزمن ---
        low_p = hist['Low'].min()
        low_d = hist['Low'].idxmin()
        high_p = hist['High'].max()
        wave_size = high_p - low_p
        t3 = low_p + (wave_size * 1.618)
        t5 = low_p + (wave_size * 2.618)
        target_date = low_d + timedelta(days=144) # دورة زمنية فيبوناتشي

        # --- 2. المؤشرات الرقمية ---
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi = 100 - (100 / (1 + (gain/loss)))
        ema12 = hist['Close'].ewm(span=12, adjust=False).mean()
        ema26 = hist['Close'].ewm(span=26, adjust=False).mean()
        macd = ema12 - ema26
        sig = macd.ewm(span=9, adjust=False).mean()

        return {
            "hist": hist, "low_p": low_p, "low_d": low_d.date(),
            "t3": t3, "t5": t5, "t_date": target_date.date(),
            "rsi": rsi.iloc[-1], "macd": macd.iloc[-1], "sig": sig.iloc[-1]
        }
    except: return None

# --- الواجهة الرئيسية ---
st.title("🏹 مركز قيادة Z88 PREDATOR - العرض المتدفق")

uploaded_file = st.sidebar.file_uploader("ارفع ملف الأسعار", type=["csv", "xlsx"])

if uploaded_file:
    df_main = load_and_clean(uploaded_file)
    if df_main is not None:
        st.sidebar.success("✅ البيانات جاهزة")
        
        # اختيار السهم (المحرك الرئيسي للوحة)
        st.subheader("🔍 اختر السهم لبدء التشغيل الشامل")
        sel_ticker = st.selectbox("", df_main['الرمز'].unique())
        
        row = df_main[df_main['الرمز'] == sel_ticker].iloc[0]
        p_now = row['إغلاق']
        
        st.markdown(f"## 🏛️ تحليل سهم: {row['اسم الشركه']} ({sel_ticker})")
        
        # سحب التحليل
        with st.spinner('جاري تشغيل الـ 13 محرك تحليل...'):
            data = get_full_analysis(sel_ticker, p_now)

        if data:
            # --- الترتيب العمودي حسب رؤيتي الفنية ---
            
            # 1. قسم القناص (إليوت والزمن)
            st.divider()
            st.subheader("🎯 1. محرك القناص (إليوت والزمن التفصيلي)")
            c1, c2, c3 = st.columns(3)
            c1.metric("سعر بداية الموجة", f"{data['low_p']:.2f}", f"بدأت في {data['low_d']}")
            c2.metric("المستهدف (موجة 3)", f"{data['t3']:.2f}", "🎯 هدف رئيسي")
            c3.metric("تاريخ الهدف المتوقع", f"{data['t_date']}")
            
            

            # 2. قسم زوايا جان والأوردر بلوك
            st.divider()
            st.subheader("🧱 2. السيولة المؤسساتية (Order Block) وزوايا جان")
            g1, g2, g3 = st.columns(3)
            root = np.sqrt(p_now)
            g1.success(f"دعم الحيتان (OB Buy): {data['hist']['Low'].tail(20).min():.2f}")
            g2.error(f"مقاومة الميكر (OB Sell): {data['hist']['High'].tail(20).max():.2f}")
            g3.info(f"زاوية جان 180 (انعكاس): {(root + 1)**2:.2f}")

            # 3. قسم المؤشرات والسكويز (Technical Health)
            st.divider()
            st.subheader("📈 3. نبض المؤشرات (MACD / RSI / Squeeze)")
            m1, m2, m3 = st.columns(3)
            m1.write(f"**RSI (14):** {data['rsi']:.2f}")
            m2.write(f"**حالة الماكد:** {'إيجابي ✅' if data['macd'] > data['sig'] else 'سلبي ❌'}")
            m3.write(f"**السكويز:** {'انفجار وشيك 🚀' if row['السيولة'] > 60 else 'تجميع 😴'}")

            # 4. الشارت الفني المتكامل
            st.divider()
            st.subheader("📊 4. الشارت الفني التفاعلي")
            fig = go.Figure(data=[go.Candlestick(x=data['hist'].index, open=data['hist']['Open'], 
                                                 high=data['hist']['High'], low=data['hist']['Low'], 
                                                 close=data['hist']['Close'], name='السعر')])
            fig.add_hline(y=data['t3'], line_dash="dash", line_color="green", annotation_text="هدف إليوت")
            fig.update_layout(template="plotly_dark", height=600)
            st.plotly_chart(fig, use_container_width=True)

            # 5. السيكولوجية وصمام الأمان
            st.divider()
            st.subheader("🧠 5. السيكولوجية وصمام الأمان")
            st.warning(f"⚠️ وقف الخسارة النهائي (إغلاق تحت): {p_now * 0.94:.2f}")
            st.info(f"💡 نصيحة الميكر: السهم في منطقة {'تجميع هادئ' if row['السيولة'] < 50 else 'دخول سيولة ذكية'}")

            # 6. تحميل الداتا
            st.divider()
            csv_out = data['hist'].to_csv(index=True, encoding='utf-8-sig').encode('utf-8-sig')
            st.download_button(f"📥 تحميل تقرير {sel_ticker} الكامل", csv_out, f"{sel_ticker}_Z88_Full.csv")

        # عرض جدول السوق بالكامل في النهاية
        st.divider()
        st.subheader("📋 ملخص حالة السوق بالكامل")
        st.dataframe(df_main[['الرمز', 'اسم الشركه', 'إغلاق', 'السيولة']])
        st.download_button("📥 تحميل داتا السوق كاملة", df_main.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig'), "Market_Report.csv")

else:
    st.info("👋 ارفع ملف الأسعار (Prices, support & Resistance) لتفعيل الرادار.")
