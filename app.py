import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 1. إعدادات النظام السيادي
st.set_page_config(page_title="Z88 Sniper Elite Pro", layout="wide")

# --- محرك معالجة البيانات واللغة العربية ---
def load_data(file):
    try:
        df = pd.read_excel(file) if file.name.endswith('.xlsx') else pd.read_csv(file, encoding='utf-8-sig')
        df.columns = [str(c).strip() for c in df.columns]
        df = df.loc[:, ~df.columns.duplicated()]
        mapping = {'الرمز': 'الرمز', 'إغلاق': 'إغلاق', 'السيولة': 'السيولة', 'اسم الشركه': 'اسم الشركه', 'الارتكاز': 'الارتكاز'}
        for col in df.columns:
            for k, v in mapping.items():
                if k in col: df.rename(columns={col: v}, inplace=True)
        return df
    except: return None

# --- محرك إليوت التفصيلي (السعر + الزمن + الموجات) ---
def elliott_wave_engine(ticker, current_price):
    try:
        # سحب داتا سنة للبحث عن بداية الموجة
        hist = yf.download(f"{ticker}.CA", period="1y", progress=False)
        if isinstance(hist.columns, pd.MultiIndex): hist.columns = hist.columns.get_level_values(0)
        
        # تحديد أدنى قاع خلال السنة (بداية الموجة العظمى 1)
        low_price = hist['Low'].min()
        low_date = hist['Low'].idxmin()
        
        # تحديد أعلى قمة (نهاية الموجة 1 أو 3)
        high_price = hist['High'].max()
        high_date = hist['High'].idxmax()

        # حسابات مستهدفات فيبوناتشي الزمنية والسعرية
        # الموجة 3 عادة تكون 1.618 من الموجة 1
        wave_1_size = high_price - low_price
        target_3_price = low_price + (wave_1_size * 1.618)
        
        # الحساب الزمني (دورة 55 يوم أو 144 يوم فيبوناتشي)
        expected_date = low_date + timedelta(days=144)
        
        # تحديد الحالة الحالية
        if current_price < target_3_price:
            current_wave = "الموجة 3 (الاندفاعية العظمى)"
            status = "صعود مستمر"
        else:
            current_wave = "الموجة 5 (الأخيرة)"
            status = "تخفيف مراكز"

        return {
            "start_price": low_price,
            "start_date": low_date.date(),
            "target_price": target_3_price,
            "target_date": expected_date.date(),
            "wave_name": current_wave,
            "status": status,
            "hist": hist
        }
    except: return None

# --- الواجهة الرئيسية ---
st.title("🏹 رادار القناص Z88 - التحليل الموجي والزمني التفصيلي")

uploaded_file = st.sidebar.file_uploader("ارفع ملف البيانات اليومي", type=["csv", "xlsx"])

if uploaded_file:
    df = load_data(uploaded_file)
    if df is not None:
        st.sidebar.success("✅ المحرك يعمل بأقصى طاقة")
        
        tabs = st.tabs(["🎯 القناص (إليوت التفصيلي)", "📐 زوايا جان والزمن", "📈 المؤشرات الرقمية", "🐳 الحيتان", "📥 التقارير"])

        with tabs[0]:
            selected_ticker = st.selectbox("اختر السهم لتحليله بالكامل:", df['الرمز'].unique())
            row = df[df['الرمز'] == selected_ticker].iloc[0]
            
            st.write(f"### 📊 التقرير التفصيلي لسهم: {row['اسم الشركه']}")
            
            with st.spinner('جاري تحليل الدورات الزمنية وموجات إليوت...'):
                analysis = elliott_wave_engine(selected_ticker, row['إغلاق'])
            
            if analysis:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                    **🏛️ هيكل الموجة العظمى:**
                    * **بداية الدورة:** {analysis['start_date']}
                    * **سعر الانطلاق:** {analysis['start_price']:.2f}
                    * **الموجة الحالية:** {analysis['wave_name']}
                    * **الحالة الفنية:** {analysis['status']}
                    """)
                
                with col2:
                    st.markdown(f"""
                    **🎯 المستهدفات القادمة (زمن + سعر):**
                    * **السعر المستهدف:** {analysis['target_price']:.2f}
                    * **التاريخ المتوقع للوصول:** {analysis['target_date']}
                    * **أفضل سعر دخول الآن:** {((analysis['start_price'] + row['إغلاق'])/2):.2f}
                    """)
                
                

                # رسم الشارت مع توضيح المستهدف
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=analysis['hist'].index, y=analysis['hist']['Close'], name='السعر التاريخي'))
                fig.add_hline(y=analysis['target_price'], line_dash="dash", line_color="green", annotation_text="المستهدف الموجي")
                fig.update_layout(title=f"المسار المتوقع لسهم {selected_ticker}", template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)

        with tabs[4]:
            st.subheader("📥 مركز تحميل التقارير")
            # دمج التحليل في جدول واحد لكل الأسهم
            df['الموجة'] = analysis['wave_name'] if analysis else "تحت التحليل"
            df['المستهدف'] = analysis['target_price'] if analysis else 0
            
            csv_data = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
            st.download_button("📥 تحميل تقرير السوق الكامل (عربي)", csv_data, "Z88_Full_Analysis.csv")

else:
    st.info("👋 ارفع ملف الأسعار لفتح 12 قسماً من القوة الضاربة!")
