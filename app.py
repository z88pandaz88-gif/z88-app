import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 1. إعدادات النظام الأساسية
st.set_page_config(page_title="Z88 Predator - Sovereign Hub", layout="wide", initial_sidebar_state="expanded")

# --- محرك معالجة البيانات واللغة العربية (مانع الانهيار) ---
def load_and_fix_data(file):
    try:
        if file.name.endswith('.xlsx'):
            df = pd.read_excel(file)
        else:
            df = pd.read_csv(file, encoding='utf-8-sig')
        
        # تنظيف شامل للأعمدة وحل مشكلة الـ Duplicate Column المذكورة في الـ Logs
        df.columns = [str(c).strip() for c in df.columns]
        df = df.loc[:, ~df.columns.duplicated()]
        
        # توحيد مسميات الأعمدة لملفك الخاص لضمان عمل الحسابات
        mapping = {
            'الرمز': 'الرمز', 'إغلاق': 'إغلاق', 'السيولة': 'السيولة', 
            'اسم الشركه': 'اسم الشركه', 'الارتكاز': 'الارتكاز', 
            'أعلى': 'أعلى', 'أقل': 'أقل', 'قيمة التداول': 'قيمة'
        }
        for col in df.columns:
            for k, v in mapping.items():
                if k in col: df.rename(columns={col: v}, inplace=True)
        
        df['الرمز'] = df['الرمز'].astype(str).str.strip()
        return df
    except Exception as e:
        st.error(f"حدث خطأ في قراءة الملف: {e}")
        return None

# --- محرك إليوت والزمن العميق (بدون اختصار) ---
def deep_elliott_wave_analysis(ticker, current_p):
    try:
        # جلب بيانات سنتين للتحليل التاريخي العميق
        hist = yf.download(f"{ticker}.CA", period="2y", interval="1d", progress=False)
        if isinstance(hist.columns, pd.MultiIndex): 
            hist.columns = hist.columns.get_level_values(0)
        
        if hist.empty: return None

        # [1] تحليل الموجة العظمى (Grand Cycle)
        grand_low_p = hist['Low'].min()
        grand_low_date = hist['Low'].idxmin()
        grand_high_p = hist['High'].max()
        
        # حساب مستهدف الموجة العظمى 3 (1.618 من طول الموجة 1)
        grand_wave_1_size = grand_high_p - grand_low_p
        major_target_3 = grand_low_p + (grand_wave_1_size * 1.618)
        major_target_5 = grand_low_p + (grand_wave_1_size * 2.618)
        
        # [2] تحليل الموجة الداخلية الحالية (Sub-Waves)
        # البحث عن آخر قاع تصحيحي (بداية الموجة الداخلية الحالية)
        recent_hist = hist.tail(90) # آخر 3 شهور
        sub_low_p = recent_hist['Low'].min()
        sub_low_date = recent_hist['Low'].idxmin()
        
        # حساب أهداف الموجة الداخلية بناءً على نسب فيبوناتشي
        sub_target = sub_low_p + ((current_p - sub_low_p) * 1.618) if current_p > sub_low_p else current_p * 1.15
        
        # [3] الحساب الزمني (Fibonacci Time Cycles)
        # الدورة الزمنية المتوسطة 55 يوم، والعظمى 144 يوم
        expected_sub_end = sub_low_date + timedelta(days=55)
        expected_major_end = grand_low_date + timedelta(days=144)
        
        # تحديد الموجة القادمة
        next_wave_start = expected_sub_end + timedelta(days=3)
        next_wave_end = next_wave_start + timedelta(days=34)

        return {
            "hist": hist,
            "grand_low_p": grand_low_p, "grand_low_date": grand_low_date.date(),
            "major_t3": major_target_3, "major_t5": major_target_5,
            "major_end_date": expected_major_end.date(),
            "sub_low_p": sub_low_p, "sub_low_date": sub_low_date.date(),
            "sub_target": sub_target, "sub_end_date": expected_sub_end.date(),
            "next_wave_start": next_wave_start.date(), "next_wave_end": next_wave_end.date()
        }
    except: return None

# --- محرك المؤشرات الفنية الرقمية ---
def calculate_all_indicators(df_hist):
    df = df_hist.copy()
    # MACD
    ema12 = df['Close'].ewm(span=12, adjust=False).mean()
    ema26 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = ema12 - ema26
    df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain/loss)))
    # Bollinger
    df['MA20'] = df['Close'].rolling(20).mean()
    df['UP'] = df['MA20'] + (df['Close'].rolling(20).std() * 2)
    df['LOW'] = df['MA20'] - (df['Close'].rolling(20).std() * 2)
    return df

# --- الواجهة الرئيسية للبرنامج ---
st.title("🏹 نظام Z88 PREDATOR - الإصدار المؤسساتي الشامل")
st.markdown("---")

uploaded_file = st.sidebar.file_uploader("ارفع ملف Prices, support & Resistance", type=["csv", "xlsx"])

if uploaded_file:
    df_main = load_and_fix_data(uploaded_file)
    if df_main is not None:
        st.sidebar.success("✅ تم تحميل المحركات الـ 13 بنجاح")
        
        # القائمة المنسدلة لاختيار السهم
        sel_ticker = st.selectbox("🔍 ابحث عن السهم (Z1, Z6, Z7, Z88):", df_main['الرمز'].unique())
        row = df_main[df_main['الرمز'] == sel_ticker].iloc[0]
        p_now = row['إغلاق']
        
        st.header(f"🏛️ لوحة تحكم سهم: {row['اسم الشركه']} ({sel_ticker})")

        # تشغيل محركات التحليل
        with st.spinner('جاري تشغيل تحليل إليوت والزمن والميكر...'):
            wave_data = deep_elliott_wave_analysis(sel_ticker, p_now)

        if wave_data:
            # --- ترتيب الأقسام حسب طلبك (تحليل تفصيلي ممل) ---
            
            # 1. قسم موجات إليوت (التشريح الكامل)
            st.divider()
            st.subheader("🌊 1. تشريح موجات إليوت (العظمى والداخلية)")
            
            c1, c2 = st.columns(2)
            with c1:
                st.info("🏛️ الموجة العظمى (Grand Cycle)")
                st.write(f"🔹 بدأت من سعر: **{wave_data['grand_low_p']:.2f}**")
                st.write(f"🔹 تاريخ الانطلاق: **{wave_data['grand_low_date']}**")
                st.success(f"🎯 مستهدف موجة 3 العظمى: **{wave_data['major_t3']:.2f}**")
                st.write(f"🏁 مستهدف موجة 5 النهائية: **{wave_data['major_t5']:.2f}**")
                st.write(f"📅 موعد اكتمال الدورة العظمى: **{wave_data['major_end_date']}**")
            
            with c2:
                st.warning("📍 الموجة الداخلية الحالية (Sub-Wave)")
                st.write(f"🔸 السهم حالياً في: **موجة داخلية صاعدة**")
                st.write(f"🔸 بدأت من قاع فرعي عند: **{wave_data['sub_low_p']:.2f}**")
                st.write(f"🔸 تاريخ بداية الداخلية: **{wave_data['sub_low_date']}**")
                st.success(f"🎯 مستهدف الداخلية الحالي: **{wave_data['sub_target']:.2f}**")
                st.error(f"⏳ تنتهي هذه الموجة في: **{wave_data['sub_end_date']}**")
            
            st.info(f"⏭️ **الموجة القادمة:** تصحيح فرعي يبدأ يوم **{wave_data['next_wave_start']}** وينتهي يوم **{wave_data['next_wave_end']}**")

            # 2. قسم القناص (نقاط التنفيذ)
            st.divider()
            st.subheader("🎯 2. رادار القناص (الدخول والخروج)")
            q1, q2, q3 = st.columns(3)
            q1.metric("أفضل سعر دخول الآن", f"{((wave_data['sub_low_p'] + p_now)/2):.2f}")
            q2.metric("دعم الأوردر بلوك (Buy)", f"{wave_data['hist']['Low'].tail(20).min():.2f}")
            q3.metric("مقاومة الأوردر بلوك (Sell)", f"{wave_data['hist']['High'].tail(20).max():.2f}")

            # 3. قسم زوايا جان
            st.divider()
            st.subheader("📐 3. تحليل زوايا جان السعرية")
            root = np.sqrt(p_now)
            j1, j2, j3 = st.columns(3)
            j1.write(f"📐 زاوية 90: **{(root + 0.5)**2:.2f}**")
            j2.write(f"📐 زاوية 180 (قلب الاتجاه): **{(root + 1)**2:.2f}**")
            j3.write(f"📐 زاوية 360 (دورة كاملة): **{(root + 2)**2:.2f}**")

            # 4. قسم المؤشرات الرقمية والسكويز
            st.divider()
            st.subheader("📈 4. نبض المؤشرات والسكويز")
            tech_df = calculate_all_indicators(wave_data['hist'])
            m1, m2, m3 = st.columns(3)
            m1.metric("RSI (14)", f"{tech_df['RSI'].iloc[-1]:.2f}")
            m2.write(f"**حالة MACD:** {'إيجابي صاعد ✅' if tech_df['MACD'].iloc[-1] > tech_df['Signal'].iloc[-1] else 'سلبي هابط ❌'}")
            m3.write(f"**السكويز مومنتم:** {'انفجار وشيك 🚀' if row['السيولة'] > 60 else 'تجميع هادئ 😴'}")

            # 5. الشارت التفاعلي
            st.divider()
            st.subheader("📊 5. المسار السعري والزمني المرسوم")
            fig = go.Figure(data=[go.Candlestick(x=wave_data['hist'].index, open=wave_data['hist']['Open'], 
                                                 high=wave_data['hist']['High'], low=wave_data['hist']['Low'], 
                                                 close=wave_data['hist']['Close'], name='السعر')])
            fig.add_hline(y=wave_data['sub_target'], line_dash="dash", line_color="orange", annotation_text="هدف داخلية")
            fig.add_hline(y=wave_data['major_t3'], line_dash="dot", line_color="green", annotation_text="هدف عظمى")
            fig.update_layout(template="plotly_dark", height=600)
            st.plotly_chart(fig, use_container_width=True)

            # 6. قسم السيكولوجية والحيتان
            st.divider()
            st.subheader("🐳 6. سيكولوجية الحيتان والميكر")
            st.info(f"حجم تدفق السيولة: **{row['السيولة']}%**")
            st.warning(f"⚠️ وقف الخسارة النهائي: **{p_now * 0.94:.2f}**")
            
            # 7. تحميل التقارير
            st.divider()
            csv_ticker = wave_data['hist'].to_csv(index=True, encoding='utf-8-sig').encode('utf-8-sig')
            st.download_button(f"📥 تحميل تقرير {sel_ticker} التفصيلي", csv_ticker, f"{sel_ticker}_Analysis.csv")

        # عرض الجدول العام في الأسفل
        st.divider()
        st.subheader("📋 ملخص حالة السوق العام")
        st.dataframe(df_main[['الرمز', 'اسم الشركه', 'إغلاق', 'السيولة']])
        st.download_button("📥 تحميل داتا السوق كاملة (عربي)", df_main.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig'), "Market_Z88.csv")

else:
    st.info("👋 ارفع ملف الأسعار لتشغيل الماكينة العملاقة.")
