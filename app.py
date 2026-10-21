import os
import csv
from datetime import datetime
import streamlit as st

# Тука го ставаме точното име на твојот фајл
PRICES_FILE = "Evidencija_Ceni_Pazaranje_Online.csv"
RECIPES_FILE = "recipes_db.csv"

# Иницијализација на фајлови
def init_files():
    if not os.path.exists(PRICES_FILE):
        with open(PRICES_FILE, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Категорија", "Производ и грамажа", "Најниска цена (ден.)", "Маркет", "Датум", "Забелешка"])
            
    if not os.path.exists(RECIPES_FILE):
        with open(RECIPES_FILE, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Категорија", "Назив на рецепт", "Состојки", "Подготовка", "Датум", "Забелешка"])

init_files()

st.set_page_config(page_title="Евиденција на Цени и Рецепти", page_icon="🛒", layout="wide")

st.title("🛒 Евиденција на Цени и Рецепти")
st.write("Добредојдовте! Вашата лична база за најниски цени и омилени рецепти.")

# Мени / Табови
tab1, tab2, tab3, tab4 = st.tabs(["📊 Преглед на најниски цени", "➕ Додај производ", "📖 Преглед на рецепти", "🍳 Додај нов рецепт"])

# 1. ТАБ: ПРЕГЛЕД НА ЦЕНИ
with tab1:
    st.header("Преглед на најниски цени")
    
    prices_data = []
    if os.path.exists(PRICES_FILE):
        with open(PRICES_FILE, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                prices_data.append(row)
                
    if prices_data:
        prices_data = sorted(prices_data, key=lambda x: (x.get("Категорија", ""), x.get("Производ и грамажа", "")))

        search_query = st.text_input("Пребарај производ:", key="price_search")
        
        categories = ["Сите"] + sorted(list(set(row.get("Категорија", "") for row in prices_data if row.get("Категорија"))))
        markets = ["Сите"] + sorted(list(set(row.get("Маркет", "") for row in prices_data if row.get("Маркет"))))
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            selected_cat = st.selectbox("Филтрирај по категорија:", categories, key="price_cat")
        with col_f2:
            selected_mkt = st.selectbox("Филтрирај по маркет:", markets, key="price_mkt")
            
        filtered_prices = prices_data
        if search_query:
            filtered_prices = [r for r in filtered_prices if search_query.lower() in r.get("Производ и грамажа", "").lower()]
        if selected_cat != "Сите":
            filtered_prices = [r for r in filtered_prices if r.get("Категорија") == selected_cat]
        if selected_mkt != "Сите":
            filtered_prices = [r for r in filtered_prices if r.get("Маркет") == selected_mkt]
            
        st.dataframe(filtered_prices, use_container_width=True)
    else:
        st.info("Нема внесено производи во базата.")

# 2. ТАБ: ДОДАЈ ПРОИЗВОД
with tab2:
    st.header("Додај производ рачно")
    with st.form("add_price_form"):
        p_cat = st.selectbox("Категорија", ["Деликатес & Паштети", "Замрзнато & Риба", "Здрава храна", "Кафе & Чај", "Леб & Печива", "Млечни производи", "Пијалоци", "Слатки & Грицки", "Хигиена за дом", "Останато"])
        p_name = st.text_input("Производ и грамажа (на пр. Путер од кикирики 500гр)")
        p_price = st.number_input("Цена (ден.)", min_value=0.0, format="%.2f")
        p_market = st.text_input("Маркет (на пр. Ramstore)")
        p_date = st.date_input("Датум", value=datetime.today())
        p_notes = st.text_input("Забелешка (опционално)")
        
        submit_price = st.form_submit_button("Зачувај производ")
        
        if submit_price and p_name and p_market:
            rows = []
            updated = False
            date_str = p_date.strftime("%d.%m.%Y")
            
            with open(PRICES_FILE, mode="r", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader, None)
                for row in reader:
                    if len(row) >= 6:
                        cat, prod, pr, mkt, dt, nts = row
                        if prod.strip().lower() == p_name.strip().lower():
                            updated = True
                            try:
                                existing_price = float(pr)
                                if p_price < existing_price:
                                    rows.append([p_cat, p_name, str(p_price), p_market, date_str, f"Намалено од {existing_price} ден."])
                                    st.success(f"Ажурирано! Нова пониска цена за {p_name}: {p_price} ден.")
                                else:
                                    rows.append(row)
                                    st.info(f"Постоечката пониска цена ({existing_price} ден.) останува за {p_name}.")
                            except ValueError:
                                rows.append(row)
                        else:
                            rows.append(row)
                            
            if not updated:
                rows.append([p_cat, p_name, str(p_price), p_market, date_str, p_notes])
                st.success(f"Успешно додаден нов производ: {p_name} по цена од {p_price} ден.")
                
            with open(PRICES_FILE, mode="w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Категорија", "Производ и грамажа", "Најниска цена (ден.)", "Маркет", "Датум", "Забелешка"])
                writer.writerows(sorted(rows, key=lambda x: (x[0], x[1])))

# 3. ТАБ: ПРЕГЛЕД НА РЕЦЕПТИ (КАРТИЧКИ)
with tab3:
    st.header("📖 Преглед на Рецепти")
    
    recipes_data = []
    if os.path.exists(RECIPES_FILE):
        with open(RECIPES_FILE, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                recipes_data.append(row)
                
    if recipes_data:
        # Креираме колони за пребарувачот и филтерот за категорија
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            rec_search = st.text_input("Пребарај рецепт по назив или состојка:", key="recipe_search")
        
        with col_r2:
            # Ги земаме сите уникатни категории од базата на рецепти
            recipe_categories = ["Сите"] + sorted(list(set(row.get("Категорија", "") for row in recipes_data if row.get("Категорија"))))
            rec_cat_filter = st.selectbox("Филтрирај по категорија:", recipe_categories, key="recipe_cat_filter")
        
        filtered_recipes = recipes_data
        
        # Филтрирање по пребарување (назив/состојки)
        if rec_search:
            filtered_recipes = [r for r in filtered_recipes if rec_search.lower() in r.get("Назив на рецепт", "").lower() or rec_search.lower() in r.get("Состојки", "").lower()]
            
        # Филтрирање по категорија
        if rec_cat_filter != "Сите":
            filtered_recipes = [r for r in filtered_recipes if r.get("Категорија") == rec_cat_filter]
            
        # Приказ на филтрираните рецепти
        for r in filtered_recipes:
            with st.container():
                st.markdown(f"### 🥗 {r.get('Назив на рецепт', '')}")
                st.write(f"**Категорија:** {r.get('Категорија', '')} | **Датум:** {r.get('Датум', '')}")
                if r.get('Забелешка'):
                    st.caption(f"Забелешка: {r.get('Забелешка')}")
                
                st.markdown("**Состојки:**")
                st.info(r.get('Состојки', ''))
                
                st.markdown("**Подготовка:**")
                st.write(r.get('Подготовка', ''))
                st.divider()
    else:
        st.info("Нема зачувани рецепти во базата.")

# 4. ТАБ: ДОДАЈ НОВ РЕЦЕПТ
with tab4:
    st.header("🍳 Додај нов рецепт")
    with st.form("add_recipe_form"):
        r_cat = st.selectbox("Категорија на рецепт", ["Зимница", "Главно јадење", "Десерти", "Појадок & Брзи оброци", "Салати", "Супи и чорби"])
        r_name = st.text_input("Назив на рецепт (на пр. Домашен пинџур)")
        r_ingredients = st.text_area("Состојки (на пр. 1 кг црвени пиперки, 500 г домати...)")
        r_prep = st.text_area("Подготовка / Опис на постапката")
        r_date = st.date_input("Датум на внес", value=datetime.today(), key="rec_date")
        r_notes = st.text_input("Забелешка (опционално, на пр. Се служи со топол леб)")
        
        submit_recipe = st.form_submit_button("Зачувај рецепт")
        
        if submit_recipe and r_name and r_ingredients and r_prep:
            # Проверка за дупликат
            recipe_exists = False
            if os.path.exists(RECIPES_FILE):
                with open(RECIPES_FILE, mode="r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row.get("Назив на рецепт", "").strip().lower() == r_name.strip().lower():
                            recipe_exists = True
                            break
            
            if recipe_exists:
                st.warning(f"⚠️ Рецептот со назив '{r_name}' веќе постои во вашиот готвач! Проверете во прегледот или користете друго име.")
            else:
                date_str = r_date.strftime("%d.%m.%Y")
                with open(RECIPES_FILE, mode="a", encoding="utf-8", newline="") as f:
                    writer = csv.writer(f)
                    if os.stat(RECIPES_FILE).st_size == 0:
                         writer.writerow(["Категорија", "Назив на рецепт", "Состојки", "Подготовка", "Датум", "Забелешка"])
                    writer.writerow([r_cat, r_name, r_ingredients, r_prep, date_str, r_notes])
                st.success(f"Рецептот '{r_name}' е успешно зачуван и додаден во вашиот готвач!")
