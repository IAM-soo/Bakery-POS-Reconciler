import streamlit as st

from reconciler import(
    load_menu,
    POS_METHODS,
    PAYMENT_GROUPS,
    CAT_EMONEY_METHODS,
    CAT_CHQR_METHODS,
    CAT_JPQR_METHODS,
    calculate_payment_total,
    calculate_difference,
    calculate_target_amount,
    find_combinations,
)

st.title("Bakery POS Reconciler")

products = load_menu()
st.write("商品数:", len(products))

st.header("差額チェック")



def POS_input():
    cat_emoney = {}
    for emoney_name in CAT_EMONEY_METHODS:
        cat_emoney[emoney_name] = st.number_input(emoney_name, min_value=0, step=1)


def cat_credit_input():
    cat_credit = st.number_input("CATクレジット", min_value=0, step=1)
    return cat_credit


def cat_suica_input():
    cat_suica = st.number_input("CAT交通系IC", min_value=0, step=1)
    return cat_suica


def cat_emoney_input():
    cat_emoney = {}
    for emoney_name in CAT_EMONEY_METHODS:
        cat_emoney[emoney_name] = st.number_input(emoney_name, min_value=0, step=1)

    emoney_total = calculate_payment_total(cat_emoney)
    st.write("CAT電子マネー総額:", emoney_total)


def cat_jpqr_input():
    cat_jpqr = {}
    for jpqr_name in CAT_JPQR_METHODS:
        cat_jpqr[jpqr_name] = st.number_input(jpqr_name, min_value=0, step=1)

    jpqr_total = calculate_payment_total(cat_jpqr)
    st.write("CAT国内QR総額:", jpqr_total)


def cat_chqr_input():
    cat_chqr = {}
    for chqr_name in CAT_CHQR_METHODS:
        cat_chqr[chqr_name] = st.number_input(chqr_name, min_value=0, step=1)

    chqr_total = calculate_payment_total(cat_chqr)
    st.write("CAT中国QR総額:", chqr_total)


if __name__ == "__main__":
    cat_credit = cat_credit_input()
    cat_suica = cat_suica_input()
    cat_emoney_input()
    cat_chqr_input()
    cat_jpqr_input()