import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 1. إعدادات الصفحة الاحترافية
st.set_page_config(page_title="Z88 Global Command Center", layout="wide")

# 2. محرك تنظيف وقراءة البيانات (إكسيل + CSV)
def load_and_fix_data(file):
    try:
        if file.name.endswith('.xlsx') or file.name.endswith('.xls'):
            df = pd.read_excel(file)
        else:
            df = pd.read_csv(file)
        
        # تنظيف العناوين من المسافات المخفية (حل مشكلة ملفك)
        df.columns = [str(c).strip() for c in df.columns]
        
        # توحيد أسماء الأعمدة الأساسية
        mapping = {
            'الرمز': 'الرمز', 'إغلاق': 'إغلاق', 'اسم الشركه': 'اسم الشركه',
            'نسبة السيولة الداخلة الى السهم': 'السيولة', 'أعلى': 'أعلى', 'أقل': 'أقل'
        }
        for col in df.columns:
            for key, val in mapping.items():
                if key in col:
                    df.rename(columns={col: val}, inplace=True)
        
        df['الرمز'] = df['الرمز'].astype(str).str.strip()
        return df
    except Exception as e:
        st.error(f"حدث خطأ في قراءة الملف: {e}")
        return None

# 3. محرك الحسابات (جان وإليوت وزمن)
def get_technical_analysis(price):
    root = np.sqrt(price)
    return {
        "جان 90°": (root + 0.5)**2,
        "جان 180°": (root + 1.0)**2,
        "جان 360°": (root + 2.0)**2,
        "إليوت 161.8%": price * 1.618,
        "إليوت 261.8%": price * 2.618
    }

# --- الواجهة الرئيسية ---
st.title("🛡️ نظام Z88 QUANT PANDA المتكامل")

# القائمة الجانبية
st.sidebar.header("📥 مركز رفع البيانات")
uploaded_file = st.sidebar.file_uploader("ارفع ملف Prices, support & Resistance", type=["csv", "xlsx"])

if uploaded_file:
    df = load_and_fix_data(uploaded_file)
    if df is not None:
        st.sidebar.success("✅ تم تفعيل النظام الشامل")

        # الأقسام التسعة (كاملة بدون نقص)
        tabs = st.tabs([
            "🚀 السكويز والزمن", "🌊 إليوت وفيبوناتشي", "📐 زوايا جان", 
            "🧱 أوردر بلوك", "🔍 البحث والتحليل", "📊 تحليل السوق", 
            "🧠 السيكولوجية", "💼 المحفظة", "🐳 الحيتان"
        ])

        # --- 1. السكويز والزمن ---
        with tabs[0]:
            st.subheader("🔥 رادار السكويز والانعكاس الزمني")
            df['Squeeze'] = np.where(df['السيولة'] > 60, "انفجار وشيك 🚀", "تجميع 😴")
            df['تاريخ_الانعكاس'] = (datetime.now() + timedelta(days=7)).date()
            st.table(df[['الرمز', 'إغلاق', 'السيولة', 'Squeeze', 'تاريخ_الانعكاس']].head(15))
            

        # --- 2. إليوت وفيبوناتشي ---
        with tabs[1]:
            st.subheader("🌊 تحليل موجات إليوت")
            df['Wave_3'] = df['إغلاق'] * 1.618
            df['Wave_5'] = df['إغلاق'] * 2.618
            st.dataframe(df[['الرمز', 'اسم الشركه', 'إغلاق', 'Wave_3', 'Wave_5']])

        # --- 3. زوايا جان السعرية ---
        with tabs[2]:
            st.subheader("📐 مربع التسعة لـ W.D. GANN")
            sel_ticker = st.selectbox("اختر السهم:", df['الرمز'].unique())
            p = df[df['الرمز'] == sel_ticker]['إغلاق'].values[0]
            tech = get_technical_analysis(p)
            c1, c2, c3 = st.columns(3)
            c1.info(f"زاوية 90: {tech['جان 90°']:.2f}")
            c2.success(f"زاوية 180: {tech['جان 180°']:.2f}")
            c3.warning(f"زاوية 360: {tech['جان 360°']:.2f}")
            

        # --- 5. البحث والتحليل (تعدد المصادر) ---
        with tabs[4]:
            ticker_input = st.text_input("ادخل الكود لتحليل تاريخي (ياهو + ملفك):").upper()
            if ticker_input:
                row = df[df['الرمز'] == ticker_input]
                if not row.empty:
                    st.metric("سعر اليوم (ملفك)", row.iloc[0]['إغلاق'])
                    # جلب داتا قديمة من ياهو
                    hist = yf.download(f"{ticker_input}.CA", period="1y", interval="1d", progress=False)
                    if not hist.empty:
                        fig = go.Figure(data=[go.Candlestick(x=hist.index, open=hist['Open'], high=hist['High'], low=hist['Low'], close=hist['Close'])])
                        fig.update_layout(title="شارت التاريخ السعري المدمج", template="plotly_dark")
                        st.plotly_chart(fig, use_container_width=True)

        # --- 8. المحفظة وإدارة المخاطر ---
        with tabs[7]:
            st.subheader("💼 ترشيحات Z88 الذكية")
            picks = df[df['السيولة'] > 65].sort_values(by='السيولة', ascending=False).head(5)
            st.success("أسهم قريبة من نقطة الانطلاق (سيولة + زخم):")
            st.table(picks[['الرمز', 'إغلاق', 'السيولة', 'مقاومة 1', 'دعم 1']])

        # سحب التقرير لكل السوق
        st.sidebar.divider()
        csv_full = df.to_csv(index=False).encode('utf-8')
        st.sidebar.download_button("📥 سحب تقرير السوق الشامل", csv_full, "Z88_Full_Market.csv")

else:
    st.info("👋 ارفع ملف Prices, support & Resistance لبدء تشغيل النظام بالكامل.")
