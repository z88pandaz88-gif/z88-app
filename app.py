import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# إعدادات الصفحة الاحترافية
st.set_page_config(page_title="Z88 Global Hub", layout="wide")

# --- محرك حسابات زوايا جان ---
def gann_analysis(price):
    root = np.sqrt(price)
    return {
        "زاوية 90 (دعم)": (root + 0.5)**2,
        "زاوية 180 (انعكاس)": (root + 1.0)**2,
        "زاوية 270 (هدف)": (root + 1.5)**2,
        "زاوية 360 (دورة)": (root + 2.0)**2
    }

# --- الواجهة ---
st.title("🛡️ مركز قيادة Z88 QUANT PANDA")

# رفع الملف (هذا هو مصدر الداتا اليومي)
uploaded_file = st.sidebar.file_uploader("ارفع ملف الأسعار اليومي (CSV)", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df.columns = [c.strip() for c in df.columns] # تنظيف المسافات
    
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
        "🔍 البحث", "🌊 إليوت", "📐 جان", "🧱 OB", "⏳ زمن", "📊 السوق", "🧠 سيكولوجية", "💼 محفظة", "🐳 حيتان"
    ])

    # 1. البحث
    with tab1:
        ticker = st.text_input("ادخل الرمز (مثل COMI):").upper()
        if ticker:
            res = df[df['الرمز'] == ticker]
            if not res.empty:
                st.write(res.iloc[0])

    # 2. إليوت
    with tab2:
        df['Target_Z88'] = df['إغلاق'] * 1.618
        st.dataframe(df[['الرمز', 'إغلاق', 'Target_Z88']])

    # 3. زوايا جان
    with tab3:
        sel = st.selectbox("اختر سهم لزوايا جان:", df['الرمز'].unique())
        p = df[df['الرمز'] == sel]['إغلاق'].values[0]
        st.write(f"حسابات جان للسعر {p}:", gann_analysis(p))

    # 5. الانعكاس الزمني والسيولة
    with tab5:
        st.subheader("تحليل السكويز والانعكاس")
        df['انعكاس_قادم'] = (datetime.now() + timedelta(days=7)).date()
        st.table(df[['الرمز', 'إغلاق', 'نسبة السيولة الداخلة الى السهم', 'انعكاس_قادم']].head(10))

    # سحب داتا كاملة
    st.sidebar.download_button("📥 سحب التحليل كاملاً (Excel)", df.to_csv(index=False), "Z88_Report.csv")

else:
    st.info("💡 يرجى رفع ملف الـ CSV من القائمة الجانبية لتشغيل المحرك.")