import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 1. إعدادات النظام وتنسيق الواجهة
st.set_page_config(page_title="Z88 Predator Hub", layout="wide")

# --- محرك معالجة البيانات (منع التكرار وحل مشكلة العربي) ---
def load_and_fix_data(file):
    try:
        df = pd.read_excel(file) if file.name.endswith('.xlsx') else pd.read_csv(file, encoding='utf-8-sig')
        # حل مشكلة ValueError: Duplicate column names found المذكورة في الـ Logs
        df.columns = [str(c).strip() for c in df.columns]
        df = df.loc[:, ~df.columns.duplicated()] 
        
        mapping = {'الرمز': 'الرمز', 'إغلاق': 'إغلاق', 'السيولة': 'السيولة', 'اسم الشركه': 'اسم الشركه'}
        for col in df.columns:
            for k, v in mapping.items():
                if k in col: df.rename(columns={col: v}, inplace=True)
        return df
    except: return None

# --- محرك إليوت والزمن المصحح (المنطق الواقعي) ---
def get_detailed_wave_logic(ticker, p_now):
    try:
        # جلب البيانات التاريخية ومعالجة الـ Multi-index
        hist = yf.download(f"{ticker}.CA", period="2y", progress=False)
        if isinstance(hist.columns, pd.MultiIndex): hist.columns = hist.columns.get_level_values(0)
        
        if hist.empty: return None

        # حساب المتوسطات لتحديد "هوية" الموجة
        ma50 = hist['Close'].rolling(50).mean().iloc[-1]
        ma200 = hist['Close'].rolling(200).mean().iloc[-1]
        high_y = hist['High'].max()
        low_y = hist['Low'].min()
        low_d = hist['Low'].idxmin()

        # [1] تشريح الموجة الحالية (المنطق)
        if p_now > ma50 and p_now > ma200:
            if p_now < high_y:
                wave, desc = "الموجة 3 (اندفاعية) 🚀", "السهم في مرحلة الانفجار السعري"
                target = low_y + (high_y - low_y) * 1.618
                cycle = 144
            else:
                wave, desc = "الموجة 5 (نهاية الاتجاه) 🏁", "صعود أخير، احذر من التصحيح"
                target = p_now * 1.07
                cycle = 21
        elif p_now < ma50 and p_now > ma200:
            wave, desc = "الموجة 4 (تصحيحية) ⚠️", "تجميع وجني أرباح مؤقت"
            target = high_y
            cycle = 34
        else:
            wave, desc = "مرحلة تجميع / موجة 2 💤", "السهم يبحث عن قاع لبدء رحلة جديدة"
            target = ma50
            cycle = 55

        # [2] حساب الانعكاس الزمني (دورة زمنية في المستقبل)
        rev_date = low_d + timedelta(days=cycle)
        while rev_date.date() < datetime.now().date():
            rev_date += timedelta(days=cycle)

        # [3] الموجة الداخلية القادمة
        next_start = rev_date.date()
        next_end = next_start + timedelta(days=21)

        return {
            "hist": hist, "wave": wave, "desc": desc,
            "start_p": low_y, "start_d": low_d.date(),
            "target": target, "rev_date": rev_date.date(),
            "next_start": next_start, "next_end": next_end
        }
    except: return None

# --- الواجهة الرئيسية ---
st.title("🏹 رادار Z88 - نظام التحليل الموجي والزمني الكامل")
st.markdown("---")

uploaded_file = st.sidebar.file_uploader("ارفع ملف Prices, support & Resistance", type=["csv", "xlsx"])

if uploaded_file:
    df_main = load_and_fix_data(uploaded_file)
    if df_main is not None:
        st.sidebar.success("✅ المحرك جاهز")
        sel_ticker = st.selectbox("🔍 اختر السهم لبدء التشريح:", df_main['الرمز'].unique())
        p_now = df_main[df_main['الرمز'] == sel_ticker].iloc[0]['إغلاق']
        
        with st.spinner('جاري تشغيل الـ 13 محرك تحليل...'):
            data = get_detailed_wave_logic(sel_ticker, p_now)

        if data:
            # 1. تشريح إليوت والزمن
            st.header("🌊 أولاً: خريطة إليوت والزمن (السعر المستهدف)")
            c1, c2 = st.columns(2)
            with c1:
                st.info(f"📍 الحالة: {data['wave']}")
                st.write(f"📝 الوصف: {data['desc']}")
                st.write(f"🔹 بدأت الدورة من سعر: **{data['start_p']:.2f}**")
                st.write(f"📅 تاريخ قاع البداية: **{data['start_d']}**")
            with c2:
                st.success(f"🎯 المستهدف القادم: **{data['target']:.2f}**")
                st.warning(f"⏳ موعد الانعكاس الزمني: **{data['rev_date']}**")
                st.write(f"⏭️ الموجة القادمة تبدأ: **{data['next_start']}**")

            # 2. القناص والميكر
            st.divider()
            st.header("🎯 ثانياً: رادار القناص (الدخول والخروج)")
            q1, q2, q3 = st.columns(3)
            q1.metric("أفضل سعر دخول", f"{((data['start_p'] + p_now)/2):.2f}")
            q2.metric("دعم الأوردر بلوك (Buy)", f"{data['hist']['Low'].tail(20).min():.2f}")
            q3.metric("مقاومة الأوردر بلوك (Sell)", f"{data['hist']['High'].tail(20).max():.2f}")

            # 3. الشارت الفني
            st.divider()
            fig = go.Figure(data=[go.Candlestick(x=data['hist'].index, open=data['hist']['Open'], 
                                                 high=data['hist']['High'], low=data['hist']['Low'], 
                                                 close=data['hist']['Close'], name='السعر')])
            fig.add_hline(y=data['target'], line_dash="dash", line_color="green", annotation_text="المستهدف")
            fig.update_layout(template="plotly_dark", height=600)
            st.plotly_chart(fig, use_container_width=True)

            # 4. التقارير
            st.divider()
            csv_data = df_main.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
            st.download_button("📥 تحميل تقرير السوق (عربي)", csv_data, "Z88_Full_Report.csv")

else:
    st.info("👋 ارفع ملفك لتشغيل النظام بالكامل.")
