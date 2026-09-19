import streamlit as st
import pandas as pd
import os
from PIL import Image
import google.generativeai as genai
import json

# --- КОНФИГУРАЦИЈА НА GOOGLE GEMINI ---
GEMINI_API_KEY = "AQ.Ab8RN6IED2bBzsP9jxgJJoc0VHNSfDt8gM7MBru5UxZIIm9Xnw"

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
else:
    st.error("ГРЕШКА: Не е внесен Google Gemini API клуч во app.py.")

# Име на Excel фајлот
EXCEL_FILE = "Evidencija_Ceni_Pazaranje-v18.xlsx"

# Листа на маркети
MARKETS = ["Пакет", "Јоцо Мес", "Рамстор", "КАМ", "Веро", "Тинекс", "Стокомак", "КИПЕР", "Друг"]

# --- ФУНКЦИИ ---

def load_data():
    """Ги вчитува податоците од Excel фајлот."""
    if os.path.exists(EXCEL_FILE):
        try:
            df = pd.read_excel(EXCEL_FILE)
            df['Датум'] = pd.to_datetime(df['Датум'], errors='coerce').dt.date
            return df
        except Exception as e:
            st.error(f"Грешка при читање на Excel фајлот: {e}")
            return pd.DataFrame(columns=["Категорија", "Производ и грамажа", "Најниска цена (ден.)", "Маркет", "Датум"])
    else:
        return pd.DataFrame(columns=["Категорија", "Производ и грамажа", "Најниска цена (ден.)", "Маркет", "Датум"])

def save_data(df):
    """Ги зачувува податоците назад во Excel фајлот."""
    try:
        df.to_excel(EXCEL_FILE, index=False)
        st.success("Податоците се успешно зачувани!")
    except Exception as e:
        st.error(f"Грешка при зачувување на Excel фајлот: {e}")

def analyze_receipt_with_gemini(image_file, market_name):
    """Ја испраќа сликата до Gemini за анализа."""
    try:
        img = Image.open(image_file)
        
        prompt = f"""
        Анализирај ја оваа фискална сметка од маркетот '{market_name}'.
        Твоја задача е да извлечеш листа на производи и нивните цени.
        
        Правила:
        1. Игнорирај го името на маркетот и даноците.
        2. Фокусирај се само на купените артикли.
        3. Извади го името на производот (и грамажата ако ја има) и цената во денари.
        4. Ако цената не е јасна, обиди се да ја процениш од контекст.
        5. Врати JSON листа со следниот формат: 
        [
          {{"Product": "Име на производ и грамажа", "Price": 99.50}},
          {{"Product": "Друг производ", "Price": 150.00}}
        ]
        6. Не враќај ништо друго освен чист JSON.
        """
        
        response = model.generate_content([prompt, img])
        clean_response = response.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_response)
        return data
        
    except Exception as e:
        st.error(f"Грешка при анализа на сметката со Gemini: {e}")
        return None

# --- ИЗГЛЕД НА АПЛИКАЦИЈАТА ---

st.set_page_config(page_title="Евиденција на Цени и Пазарење", layout="wide")

st.title("🛒 Евиденција на Цени и Пазарење")
st.write("Добредојдовте! Оваа е вашата лична база за најниски цени по производи.")

df = load_data()

# Табови за навигација
tab1, tab2, tab3 = st.tabs(["📋 Преглед на најниски цени", "➕ Додај производ рачно", "📸 Скенирај сметка (AI)"])

with tab1:
    st.header("Преглед на најниски цени")
    
    search_query = st.text_input("Пребарај производ или маркет:", "")
    categories = ["Сите"] + sorted(df['Категорија'].unique().tolist()) if not df.empty else ["Сите"]
    selected_category = st.selectbox("Филтрирај по категорија:", categories)
    
    filtered_df = df.copy()
    if search_query and not filtered_df.empty:
        filtered_df = filtered_df[filtered_df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)]
    if selected_category != "Сите" and not filtered_df.empty:
        filtered_df = filtered_df[filtered_df['Категорија'] == selected_category]
    
    st.dataframe(
        filtered_df,
        column_config={
            "Најниска цена (ден.)": st.column_config.NumberColumn(format="%.2f"),
            "Датум": st.column_config.DateColumn(format="DD.MM.YYYY"),
        },
        hide_index=True,
        use_container_width=True
    )

with tab2:
    st.header("Додај нов производ рачно")
    with st.form("add_product_form"):
        col1, col2 = st.columns(2)
        with col1:
            cat_list = categories[1:] if len(categories) > 1 else MARKETS
            new_category = st.selectbox("Категорија:", cat_list)
            new_product = st.text_input("Производ и грамажа (на пр. Млеко 1л):", "")
            new_date = st.date_input("Датум на купување:")
        with col2:
            new_price = st.number_input("Најниска цена (ден.):", min_value=0.0, format="%.2f")
            new_market = st.selectbox("Маркет:", MARKETS)
            
        submitted = st.form_submit_button("Зачувај во базата")
        if submitted:
            if new_product and new_price > 0:
                new_row = pd.DataFrame({
                    "Категорија": [new_category],
                    "Производ и грамажа": [new_product],
                    "Најниска цена (ден.)": [new_price],
                    "Маркет": [new_market],
                    "Датум": [new_date]
                })
                df = pd.concat([new_row, df], ignore_index=True)
                save_data(df)
                st.rerun()
            else:
                st.error("Ве молиме пополнете го името на производот и внесете цена.")

with tab3:
    st.header("📸 Скенирај фискална сметка (со вештачка интелигенција)")
    
    receipt_market = st.selectbox("Избери маркет од кој е сметката:", MARKETS, key="receipt_market_select")
    uploaded_file = st.file_uploader("Прикачи слика или сликај ја сметката:", type=['png', 'jpg', 'jpeg'])
    
    if uploaded_file is not None:
        st.image(uploaded_file, caption="Прикачена сметка", use_container_width=True)
        
        if st.button("Анализирај ја сметката со AI"):
            with st.spinner("Gemini ја анализира сметката..."):
                receipt_data = analyze_receipt_with_gemini(uploaded_file, receipt_market)
                
                if receipt_data:
                    st.success("Успешно извлечени податоци од сметката!")
                    editable_df = pd.DataFrame(receipt_data)
                    editable_df.rename(columns={"Product": "Производ и грамажа", "Price": "Најниска цена (ден.)"}, inplace=True)
                    
                    cat_list = categories[1:] if len(categories) > 1 else ["Друго"]
                    edited_data = st.data_editor(
                        editable_df,
                        column_config={
                            "Најниска цена (ден.)": st.column_config.NumberColumn(format="%.2f"),
                            "Категорија": st.column_config.SelectboxColumn(options=cat_list, default="Друго"),
                        },
                        use_container_width=True
                    )
                    
                    if st.button("Зачувај ги сите производи од сметката"):
                        receipt_entries_to_add = []
                        for index, row in edited_data.iterrows():
                            if row['Производ и грамажа'] and row['Најниска цена (ден.)'] > 0:
                                receipt_entries_to_add.append({
                                    "Категорија": row.get('Категорија', 'Друго'),
                                    "Производ и грамажа": row['Производ и грамажа'],
                                    "Најниска цена (ден.)": row['Најниска цена (ден.)'],
                                    "Маркет": receipt_market,
                                    "Датум": pd.Timestamp.today().date()
                                })
                                
                        if receipt_entries_to_add:
                            new_rows_df = pd.DataFrame(receipt_entries_to_add)
                            df = pd.concat([new_rows_df, df], ignore_index=True)
                            save_data(df)
                            st.rerun()
                        else:
                            st.warning("Нема валидни производи за зачувување.")
                else:
                    st.error("Не успеав да прочитам ништо корисно од сметката. Пробајте со појасна слика.")
