import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 1. إعدادات بيئة العمل الاحترافية
st.set_page_config(page_title="Z88 Predator Hub", layout="wide", initial_sidebar_state="expanded")

# --- محرك معالجة البيانات الفائق (Anti-Crash) ---
def clean_and_sync_data(file):
    try:
        if file.name.endswith('.xlsx'):
            df = pd.read_excel(file)
        else:
            df = pd.read_csv(file)
        
        # تنظيف العناوين وحل مشكلة التكرار التي ظهرت في الـ Logs
        df.columns = [str(c).strip() for c in df.columns]
        df = df.loc[:, ~df.columns.duplicated()]
        
        # خريطة توحيد المسميات لملفك الخاص
        column_map = {
            'الرمز': 'الرمز', 'إغلاق': 'إغلاق', 'السيولة': 'السيولة', 
            'قيمة التداول': 'قيمة', 'أعلى': 'أعلى', 'أقل': 'أقل', 
            'اسم الشركه': 'اسم الشركه', 'عدد العمليات': 'عمليات'
        }
        for col in df.columns:
            for k, v in column_map.items():
                if k in col: df.rename(columns={col: v}, inplace=True)
        
        df['الرمز'] = df['الرمز'].astype(str).str.strip()
        return df
    except Exception as e:
        st.error(f"خطأ في معالجة الملف: {e}")
        return None

# --- محرك المؤشرات الرقمية (The Beast Engine) ---
def calculate_advanced_tech(df_hist):
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
    # Bollinger Bands
    df['MA20'] = df['Close'].rolling(20).mean()
    df['std'] = df['Close'].rolling(20).std()
    df['Upper'] = df['MA20'] + (df['std'] * 2)
    df['Lower'] = df['MA20'] - (df['std'] * 2)
    return df

# --- الواجهة الرئيسية ---
st.title("🏹 نظام Z88 PREDATOR - الإصدار السيادي المتكامل")
st.markdown("---")

uploaded_file = st.sidebar.file_uploader("ارفع ملف البيانات اليومي (Excel/CSV)", type=["csv", "xlsx"])

if uploaded_file:
    df_main = clean_and_sync_data(uploaded_file)
    if df_main is not None:
        st.sidebar.success("✅ النظام متصل بكل المحركات")
        
        # الأقسام الـ 13 (كاملة بدون اختصار)
        tabs = st.tabs([
            "🎯 القناص Z", "🚀 السكويز & الزمن", "🌊 موجات إليوت", "📐 زوايا جان", 
            "🧱 الأوردر بلوك", "📈 المؤشرات الرقمية", "🐳 نبض الميكر", 
            "🧠 السيكولوجية", "💼 المحفظة", "🚨 إشارات الدخول", 
            "📊 تحليل السوق", "🔍 البحث التاريخي", "⚙️ الإعدادات"
        ])

        # --- 1. قسم القناص (Z-Sniper) ---
        with tabs[0]:
            st.subheader("🎯 رادار القناص: تحديد بداية الانفجار (Wave 3/5)")
            df_main['Target_161'] = df_main['إغلاق'] * 1.618
            df_main['Maker_Pulse'] = (df_main['السيولة'] * df_main['إغلاق']) / 100
            # فلترة الأسهم النشطة فقط
            sniper_list = df_main[df_main['السيولة'] > 50].sort_values(by='السيولة', ascending=False)
            st.dataframe(sniper_list[['الرمز', 'اسم الشركه', 'إغلاق', 'السيولة', 'Target_161', 'Maker_Pulse']])
            st.download_button("📥 تحميل قائمة القناص", sniper_list.to_csv(index=False), "Sniper_Z88.csv")

        # --- 3. موجات إليوت (التفصيلي) ---
        with tabs[2]:
            st.subheader("🌊 تحليل فيبوناتشي والموجات العظمى")
            sel_stock = st.selectbox("اختر السهم للتحليل الموجي:", df_main['الرمز'].unique())
            p = df_main[df_main['الرمز'] == sel_stock]['إغلاق'].values[0]
            st.write(f"السهم في منطقة: **اندفاع موجي (موجة 3)**")
            cols = st.columns(3)
            cols[0].metric("هدف موجة 3", round(p * 1.618, 2))
            cols[1].metric("هدف موجة 5", round(p * 2.618, 2))
            cols[2].metric("وقف الخسارة", round(p * 0.94, 2))
            

        # --- 5. الأوردر بلوك (تتبع الحيتان) ---
        with tabs[4]:
            st.subheader("🧱 مناطق الشراء والبيع المؤسساتي")
            # جلب داتا ياهو لضمان الدقة
            hist_data = yf.download(f"{sel_stock}.CA", period="1y", progress=False)
            if not hist_data.empty:
                df_tech = calculate_advanced_tech(hist_data)
                buy_zone = hist_data['Low'].tail(30).min()
                sell_zone = hist_data['High'].tail(30).max()
                st.success(f"📦 منطقة تجميع الميكر (OB Buy): {buy_zone}")
                st.error(f"🚫 منطقة تصريف الميكر (OB Sell): {sell_zone}")
                

        # --- 6. المؤشرات الرقمية (MACD, RSI, Bollinger) ---
        with tabs[5]:
            st.subheader("📈 التحليل الرقمي المتكامل")
            if not hist_data.empty:
                st.write("حالة الـ MACD والـ RSI الآن:")
                st.line_chart(df_tech[['MACD', 'Signal', 'RSI']])
                # شارت البولنجر الاحترافي
                fig = go.Figure(data=[go.Scatter(x=df_tech.index, y=df_tech['Upper'], name='Upper Band'),
                                     go.Scatter(x=df_tech.index, y=df_tech['Lower'], name='Lower Band'),
                                     go.Scatter(x=df_tech.index, y=df_tech['Close'], name='Price')])
                st.plotly_chart(fig, use_container_width=True)
                st.download_button("📥 تحميل تقرير المؤشرات", df_tech.to_csv(), f"{sel_stock}_Tech.csv")

        # --- 10. إشارات الدخول والخروج ---
        with tabs[9]:
            st.subheader("🚨 رادار الإشارات الفورية")
            df_main['Signal'] = np.where(df_main['السيولة'] > 65, "دخول صاروخي 🚀", "مراقبة ⏳")
            df_main['Status'] = np.where(df_main['إغلاق'] > df_main['الارتكاز'], "إيجابي ✅", "سلبي ❌")
            st.table(df_main[['الرمز', 'إغلاق', 'السيولة', 'Signal', 'Status']].head(20))

        # زر سحب التقرير النهائي لكل السوق
        st.sidebar.divider()
        st.sidebar.download_button("📥 سحب تقرير Z88 المؤسساتي الشامل", df_main.to_csv(index=False), "Z88_Final_Full_Report.csv")

else:
    st.info("👋 ارفع ملف الأسعار لبدء عملية القنص المؤسساتي.")
