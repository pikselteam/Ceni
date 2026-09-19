Python
import streamlit as st
import pandas as pd
import os

EXCEL_FILE = "Evidencija_Ceni_Pazaranje-v18.xlsx"
MARKETS = ["Пакет", "Јоцо Мес", "Рамстор", "КАМ", "Веро", "Тинекс", "Стокомак", "КИПЕР", "Друг"]

st.set_page_config(page_title="Евиденција на Цени и Пазарење", layout="wide")

st.title("🛒 Евиденција на Цени и Пазарење")
st.write("Добредојдовте! Вашата лична база за најниски цени.")

if os.path.exists(EXCEL_FILE):
    df = pd.read_excel(EXCEL_FILE)
    df['Датум'] = pd.to_datetime(df['Датум'], errors='coerce').dt.date
else:
    df = pd.DataFrame(columns=["Категорија", "Производ и грамажа", "Најниска цена (ден.)", "Маркет", "Датум"])

search_query = st.text_input("Пребарај производ или маркет:", "")
categories = ["Сите"] + sorted(df['Категорија'].unique().tolist()) if not df.empty else ["Сите"]
selected_category = st.selectbox("Филтрирај по категорија:", categories)

filtered_df = df.copy()
if search_query and not filtered_df.empty:
    filtered_df = filtered_df[filtered_df.apply(lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)]
if selected_category != "Сите" and not filtered_df.empty:
    filtered_df = filtered_df[filtered_df['Категорија'] == selected_category]

st.dataframe(filtered_df, use_container_width=True, hide_index=True)
