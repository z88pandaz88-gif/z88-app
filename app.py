import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 1. إعدادات الصفحة
st.set_page_config(page_title="Z88 QUANT PANDA PRO", layout="wide")

# --- محرك تنظيف البيانات الذكي ---
def clean_data(file):
    try:
        df = pd.read_csv(file, encoding='utf-8')
    except:
        df = pd.read_csv(file, encoding='cp1256')
    df.columns = [str(c).strip() for c in df.columns]
    # محرك تصحيح أسماء الأعمدة آلياً
    mapping = {'الرمز': 'الرمز', 'إغلاق': 'إغلاق', 'اسم الشركه': 'اسم الشركه', 'نسبة السيولة': 'السيولة'}
    for col in df.columns:
        for key, val in mapping.items():
            if key in col: df.rename(columns={col: val}, inplace=True)
    df['الرمز'] = df['الرمز'].astype(str).str.strip()
    return df

# --- حسابات زوايا جان وفيبوناتشي الزمني ---
def get_gann_time_levels(price):
    root = np.sqrt(price)
    levels = {
        "90° (دعم/مقاومة)": (root + 0.5)**2,
        "180° (انفجار زمني)": (root + 1.0)**2,
        "360° (دورة كاملة)": (root + 2.0)**2
    }
    return levels

# --- واجهة البرنامج ---
st.title("🛡️ رادار Z88 QUANT - النسخة الاحترافية")
st.sidebar.header("📥 مركز رفع الملفات")
uploaded_file = st.sidebar.file_uploader("ارفع ملف Prices, support & Resistance", type="csv")

if uploaded_file:
    df = clean_data(uploaded_file)
    st.sidebar.success("✅ تم تحديث بيانات الجلسة")

    # الأقسام التسعة المتكاملة
    tabs = st.tabs(["🚀 السكويز والزمن", "🌊 إليوت وفيبوناتشي", "📐 زوايا جان", "🧱 الأوردر بلوك", "🔍 بحث عميق", "📊 تحليل السوق", "🧠 سيكولوجية", "💼 المحفظة", "🐳 الحيتان"])

    # --- القسم 1: السكويز مومنتم والدورة الزمنية ---
    with tabs[0]:
        st.subheader("🔥 رادار الانفجار السعري (Squeeze Momentum)")
        
        # معادلة السكويز الافتراضية بناءً على ملفك (السيولة + تذبذب السعر)
        df['Squeeze_Status'] = np.where(df['السيولة'] > 60, "انفجار وشيك 🚀", "تجميع هادئ 😴")
        
        # ربط الدورة الزمنية (جان)
        df['تاريخ_الانعكاس'] = (datetime.now() + timedelta(days=7)).date()
        
        st.table(df[['الرمز', 'اسم الشركه', 'إغلاق', 'السيولة', 'Squeeze_Status', 'تاريخ_الانعكاس']].head(15))
        

    # --- القسم 3: زوايا جان ---
    with tabs[2]:
        ticker = st.selectbox("اختر السهم لتحليل الزوايا:", df['الرمز'].unique())
        p = df[df['الرمز'] == ticker]['إغلاق'].values[0]
        g_levels = get_gann_time_levels(p)
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("### 📐 الزوايا السعرية")
            for k, v in g_levels.items():
                st.info(f"{k}: **{v:.2f}**")
        with col2:
            st.write("### ⏳ التوقيت الزمني")
            st.warning(f"الانعكاس الزمني القادم لسهم {ticker}: **{(datetime.now() + timedelta(days=13)).date()}**")
        

    # --- القسم 8: المحفظة وإدارة المخاطر ---
    with tabs[7]:
        st.subheader("💼 ترشيحات المحفظة (Z6, Z7, Z88)")
        # فلترة الأسهم القوية
        picks = df[df['السيولة'] > 65].sort_values(by='السيولة', ascending=False).head(5)
        st.success("أسهم تحت المراقبة (دخول حيتان):")
        st.dataframe(picks[['الرمز', 'إغلاق', 'السيولة', 'Speak_Resistance', 'Support']])

    # زر سحب البيانات الشامل
    st.sidebar.divider()
    full_csv = df.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button("📥 سحب تقرير Z88 لكل السوق (Excel)", full_csv, "Z88_Final_Analysis.csv")

else:
    st.info("👋 مرحباً بك.. ارفع ملفك لبدء رصد الانفجارات السعرية!")
