import streamlit as st

from reconciler import(
    load_menu,
    calculate_payment_total,
    calculate_difference,
    calculate_target_amount,
    find_combinations,
)

st.title("Bakery POS Reconciler")

products = load_menu()
st.write("商品数:", len(products))

st.header("差額チェック")
pos_amount = st.number_input("POS金額", min_value=0, step=1)

cat_emoney = {"楽天Edy": 0, "ID":0, "QUICPay":0, "WAON":0, "nanaco":0}
for emoney_name in cat_emoney:
    cat_emoney[emoney_name] = st.number_input(emoney_name, min_value=0, step=1)

emoney_total = calculate_payment_total(cat_emoney)
st.write("CAT電子マネー総額:", emoney_total)