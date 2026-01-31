import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 1. إعدادات النظام السيادي
st.set_page_config(page_title="Z88 Predator Quant Hub", layout="wide")

# --- محرك معالجة البيانات (حل مشكلة التكرار والعربي) ---
def load_and_fix_data(file):
    try:
        # دعم الإكسيل و CSV مع ترميز العربي
        df = pd.read_excel(file) if file.name.endswith('.xlsx') else pd.read_csv(file, encoding='utf-8-sig')
        
        # تنظيف الأعمدة وحل مشكلة Duplicate Columns (من الـ Logs)
        df.columns = [str(c).strip() for c in df.columns]
        df = df.loc[:, ~df.columns.duplicated()]
        
        # خريطة توحيد المسميات لملف "Prices, support & Resistance"
        mapping = {
            'الرمز': 'الرمز', 'إغلاق': 'إغلاق', 'السيولة': 'السيولة', 
            'اسم الشركه': 'اسم الشركه', 'الارتكاز': 'الارتكاز'
        }
        for col in df.columns:
            for k, v in mapping.items():
                if k in col: df.rename(columns={col: v}, inplace=True)
        return df
    except Exception as e:
        st.error(f"خطأ في الملف: {e}")
        return None

# --- محرك الانعكاس الزمني وإليوت (The Quant Core) ---
def quant_wave_and_time_engine(ticker, p_now):
    try:
        # جلب داتا سنتين لتحليل الدورات الزمنية الكبرى
        hist = yf.download(f"{ticker}.CA", period="2y", interval="1d", progress=False)
        if isinstance(hist.columns, pd.MultiIndex): 
            hist.columns = hist.columns.get_level_values(0)
        
        if hist.empty: return None

        # [1] تحديد قاع الدورة العظمى (Major Low)
        grand_low_p = hist['Low'].min()
        grand_low_date = hist['Low'].idxmin()
        
        # [2] حساب الانعكاس الزمني (جان + فيبوناتشي)
        # دورة الانعكاس الصغرى (55 يوم)، الوسطى (90 يوم)، الكبرى (144 يوم)
        reversal_short = grand_low_date + timedelta(days=55)
        reversal_medium = grand_low_date + timedelta(days=90)
        reversal_major = grand_low_date + timedelta(days=144)
        
        # [3] تحليل إليوت (المستهدف السعري)
        # الموجة 3 المستهدفة = القاع + (طول الموجة 1 * 1.618)
        peak_p = hist['High'].max()
        wave_1_len = peak_p - grand_low_p
        target_3 = grand_low_p + (wave_1_len * 1.618)
        target_5 = grand_low_p + (wave_1_len * 2.618)

        # [4] الموجة الداخلية الحالية
        recent_low_p = hist['Low'].tail(40).min()
        recent_low_date = hist['Low'].tail(40).idxmin()

        return {
            "hist": hist,
            "grand_low_date": grand_low_date.date(),
            "grand_low_p": grand_low_p,
            "rev_short": reversal_short.date(),
            "rev_major": reversal_major.date(),
            "target_3": target_3,
            "target_5": target_5,
            "sub_low_date": recent_low_date.date(),
            "sub_low_p": recent_low_p
        }
    except: return None

# --- الواجهة الرئيسية ---
st.title("🛡️ محرك القناص Z88 - تحليل الكم (Quant Edition)")
st.markdown("---")

uploaded_file = st.sidebar.file_uploader("ارفع ملف البيانات اليومي", type=["csv", "xlsx"])

if uploaded_file:
    df_main = load_and_fix_data(uploaded_file)
    if df_main is not None:
        st.sidebar.success("✅ تم الاتصال بمصادر البيانات")
        
        # اختيار السهم (المحرك الرئيسي)
        sel_ticker = st.selectbox("🔍 اختر السهم لتحليله بالكامل:", df_main['الرمز'].unique())
        row_data = df_main[df_main['الرمز'] == sel_ticker].iloc[0]
        p_now = row_data['إغلاق']

        with st.spinner('جاري تشريح الموجات وحساب دورات الانعكاس الزمني...'):
            q_data = quant_wave_and_time_engine(sel_ticker, p_now)

        if q_data:
            # --- العرض العمودي المرتب ---
            
            # القسم 1: الانعكاس الزمني (Time Reversal)
            st.header("⏳ أولاً: خريطة الانعكاس الزمني (Time Cycles)")
            t1, t2, t3 = st.columns(3)
            t1.metric("تاريخ قاع الدورة", f"{q_data['grand_low_date']}")
            t2.info(f"📅 الانعكاس القادم (متوسط): {q_data['rev_short']}")
            t3.success(f"🎯 الانعكاس الأكبر (دورة 144): {q_data['rev_major']}")
            
            # القسم 2: إليوت التفصيلي (Elliott Waves)
            st.divider()
            st.header("🌊 ثانياً: تشريح موجات إليوت (سعر وزمن)")
            e1, e2 = st.columns(2)
            with e1:
                st.subheader("🏛️ الدورة العظمى")
                st.write(f"🔹 سعر بداية الاتجاه: **{q_data['grand_low_p']:.2f}**")
                st.success(f"🚀 مستهدف موجة 3: **{q_data['target_3']:.2f}**")
                st.error(f"🏁 مستهدف موجة 5 (نهائي): **{q_data['target_5']:.2f}**")
            with e2:
                st.subheader("📍 الموجة الداخلية الحالية")
                st.write(f"🔹 بدأت بتاريخ: **{q_data['sub_low_date']}**")
                st.write(f"🔹 سعر انطلاق الداخلية: **{q_data['sub_low_p']:.2f}**")
                st.write(f"🔸 حالة الموجة: **داخلية صاعدة (موجة 3 من 5)**")
            
            

            # القسم 3: رادار القناص والميكر
            st.divider()
            st.header("🎯 ثالثاً: رادار التنفيذ (القناص والميكر)")
            c1, c2, c3 = st.columns(3)
            c1.metric("أفضل سعر دخول", f"{((q_data['sub_low_p'] + p_now)/2):.2f}")
            c2.metric("دعم الحيتان (OB Buy)", f"{q_data['hist']['Low'].tail(20).min():.2f}")
            c3.metric("مقاومة الميكر (OB Sell)", f"{q_data['hist']['High'].tail(20).max():.2f}")

            # القسم 4: الشارت التفاعلي
            st.divider()
            fig = go.Figure(data=[go.Candlestick(x=q_data['hist'].index, open=q_data['hist']['Open'], 
                                                 high=q_data['hist']['High'], low=q_data['hist']['Low'], 
                                                 close=q_data['hist']['Close'], name='السعر')])
            fig.add_hline(y=q_data['target_3'], line_dash="dash", line_color="green", annotation_text="هدف إليوت")
            fig.update_layout(template="plotly_dark", height=600, title=f"المسار التاريخي والمستقبلي لسهم {sel_ticker}")
            st.plotly_chart(fig, use_container_width=True)

            # القسم 5: التقارير (عربي)
            st.divider()
            st.subheader("📥 مركز تحميل التقارير")
            full_report = q_data['hist'].to_csv(index=True, encoding='utf-8-sig').encode('utf-8-sig')
            st.download_button(f"📥 تحميل تقرير {sel_ticker} الكامل", full_report, f"Analysis_{sel_ticker}.csv")

else:
    st.info("👋 ارفع ملف الأسعار (Prices, support & Resistance) لتفعيل محرك Z88.")
