import streamlit as st
import pandas as pd
import os

# Име на твојот CSV фајл
CSV_FILE = "Evidencija_Ceni_Pazaranje_Online.csv"

# Листа на маркети за dropdown менито
MARKETS = ["Пакет", "Јоцо Мес", "Рамстор", "КАМ", "Веро", "Тинекс", "Стокомак", "КИПЕР", "Друг"]

st.set_page_config(page_title="Евиденција на Цени и Пазарење", layout="wide")

st.title("🛒 Евиденција на Цени и Пазарење")
st.write("Добредојдовте! Вашата лична база за најниски цени.")

# Вчитување на податоци од CSV
if os.path.exists(CSV_FILE):
    try:
        df = pd.read_csv(CSV_FILE)
        df['Датум'] = pd.to_datetime(df['Датум'], errors='coerce').dt.date
    except Exception as e:
        st.error(f"Грешка при читање на CSV фајлот: {e}")
        df = pd.DataFrame(columns=["Категорија", "Производ и грамажа", "Најниска цена (ден.)", "Маркет", "Датум"])
else:
    df = pd.DataFrame(columns=["Категорија", "Производ и грамажа", "Најниска цена (ден.)", "Маркет", "Датум"])

def save_data(dataframe):
    """Ги зачувува податоците назад во CSV фајлот."""
    try:
        dataframe.to_csv(CSV_FILE, index=False)
        st.success("Податоците се успешно зачувани!")
    except Exception as e:
        st.error(f"Грешка при зачувување: {e}")

# Табови за навигација
tab1, tab2 = st.tabs(["📋 Преглед на најниски цени", "➕ Додај производ рачно"])

with tab1:
    st.header("Преглед на најниски цени")
    
    search_query = st.text_input("Пребарај производ или маркет:", "")
    categories = ["Сите"] + sorted(df['Категорија'].dropna().unique().tolist()) if not df.empty else ["Сите"]
    selected_category = st.selectbox("Филтрирај по категорија:", categories)
    
    filtered_df = df.copy()
    if search_query and not filtered_df.empty:
        filtered_df = filtered_df[filtered_df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)]
    if selected_category != "Сите" and not filtered_df.empty:
        filtered_df = filtered_df[filtered_df['Категорија'] == selected_category]
    
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)

with tab2:
    st.header("Додај нов производ рачно")
    with st.form("add_product_form"):
        col1, col2 = st.columns(2)
        with col1:
            cat_list = categories[1:] if len(categories) > 1 else ["Општо"]
            new_category = st.selectbox("Категорија:", cat_list)
            new_product = st.text_input("Производ и грамажа (на пр. Млеко 1л):", "")
            new_date = st.date_input("Датум на купување:")
        with col2:
            new_price = st.number_input("Најниска цена (ден.):", min_value=0.0, format="%.2f")
            new_market = st.selectbox("Избери маркет:", MARKETS)
            
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
