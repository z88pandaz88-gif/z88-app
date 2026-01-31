import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 1. إعدادات الصفحة
st.set_page_config(page_title="Z88 Global Hub", layout="wide")

# 2. وظيفة معالجة الملف (لتفادي أخطاء الأسماء والمسافات)
def process_data(df):
    # مسح المسافات من أسماء الأعمدة فوراً
    df.columns = [c.strip() for c in df.columns]
    # تنظيف الرموز
    df['الرمز'] = df['الرمز'].astype(str).str.strip()
    return df

# 3. محرك زوايا جان (Square of 9)
def get_gann_levels(price):
    root = np.sqrt(price)
    return {
        "زاوية 90 (دعم/مقاومة)": (root + 0.5)**2,
        "زاوية 180 (انعكاس)": (root + 1.0)**2,
        "زاوية 270 (هدف)": (root + 1.5)**2,
        "زاوية 360 (دورة سعري)": (root + 2.0)**2
    }

# --- الواجهة البرمجية ---
st.title("🛡️ مركز قيادة Z88 QUANT PANDA")
st.markdown("### النظام المتكامل لتحليل السوق المصري")

# القائمة الجانبية لرفع الملف بنفس الفورمات
uploaded_file = st.sidebar.file_uploader("ارفع ملف Prices, support & Resistance", type="csv")

if uploaded_file:
    # قراءة الملف ومعالجته
    raw_df = pd.read_csv(uploaded_file)
    df = process_data(raw_df)
    st.sidebar.success("✅ تم التعرف على ملفك بنجاح")

    # إعداد الأقسام التسعة
    tabs = st.tabs([
        "🔍 البحث", "🌊 إليوت", "📐 زوايا جان", "🧱 أوردر بلوك", 
        "⏳ زمن وسكويز", "📊 تحليل السوق", "🧠 سيكولوجية", "💼 المحفظة", "🐳 حيتان"
    ])

    # --- القسم 1: البحث والتحليل اللحظي ---
    with tabs[0]:
        search_ticker = st.text_input("ادخل كود السهم (مثل COMI أو TMGH):").strip().upper()
        if search_ticker:
            stock_row = df[df['الرمز'] == search_ticker]
            if not stock_row.empty:
                row = stock_row.iloc[0]
                c1, c2, c3 = st.columns(3)
                c1.metric("آخر سعر", row['إغلاق'])
                c2.metric("السيولة الداخلة", f"{row['نسبة السيولة الداخلة الى السهم']}%")
                c3.metric("مستهدف إليوت Z88", round(row['إغلاق'] * 1.618, 2))
                st.write("**تفاصيل الدعم والمقاومة من ملفك:**")
                st.table(stock_row[['مقاومة 1', 'الارتكاز', 'دعم 1']])
            else:
                st.error("السهم غير موجود في الملف، تأكد من الكود.")

    # --- القسم 2: موجات إليوت ---
    with tabs[1]:
        st.subheader("تحليل الموجات بناءً على فيبوناتشي")
        df['Target_161'] = df['إغلاق'] * 1.618
        df['Target_261'] = df['إغلاق'] * 2.618
        st.dataframe(df[['الرمز', 'اسم الشركه', 'إغلاق', 'Target_161', 'Target_261']])

    # --- القسم 3: زوايا جان ---
    with tabs[2]:
        st.subheader("زوايا جان الرقمية (مربع التسعة)")
        sel_stock = st.selectbox("اختر سهمك:", df['الرمز'].unique())
        p_close = df[df['الرمز'] == sel_stock]['إغلاق'].values[0]
        g_levels = get_gann_levels(p_close)
        for k, v in g_levels.items():
            st.info(f"{k}: **{v:.2f}**")

    # --- القسم 5: الانعكاس الزمني ---
    with tabs[4]:
        st.subheader("الدورة الزمنية والسكويز")
        df['تاريخ_الانعكاس'] = (datetime.now() + timedelta(days=7)).date()
        st.write("الأسهم التي تقترب من انفجار سعري (Squeeze):")
        st.table(df[df['نسبة السيولة الداخلة الى السهم'] > 60][['الرمز', 'إغلاق', 'تاريخ_الانعكاس']].head(10))

    # --- زر سحب البيانات لكل السوق ---
    st.sidebar.divider()
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button("📥 سحب تحليل السوق كاملاً (Excel)", csv_data, "Z88_Full_Analysis.csv")

else:
    st.warning("⚠️ يرجى رفع ملفك المرفق (`Prices, support & Resistance.xlsx - Sheet1.csv`) لبدء العمل.")
