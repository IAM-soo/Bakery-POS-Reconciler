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


def cat_input():
    cat_amounts_temp= {}

    for payment_group in PAYMENT_GROUPS:
        cat_methods = PAYMENT_GROUPS[payment_group]

        for cat_method in cat_methods:
            cat_amounts_temp[cat_method] = st.number_input(cat_method, min_value=0, step=1, key="cat_" + cat_method)

    return cat_amounts_temp


def calculate_selected_payment_total(payment_amounts, selected_methods):
    total = 0
    for method in selected_methods:
        total += payment_amounts.get(method, 0)
    return total
    
def reconcile_cat_amounts(cat_amounts_temp):
    cat_amounts = {}

    for payment_method in POS_METHODS:
        selected_methods = PAYMENT_GROUPS[payment_method]
        cat_amounts[payment_method] = calculate_selected_payment_total(cat_amounts_temp, selected_methods)

    return cat_amounts


def pos_input():
    pos_amounts ={}
    
    for pos_method in POS_METHODS:
        pos_amounts[pos_method] = st.number_input(pos_method, min_value=0, step=1, key="pos_" + pos_method)

    return pos_amounts

def compare_payment_amounts(pos_amounts, cat_amounts):
    for method in POS_METHODS:
        pos_amount = pos_amounts.get(method, 0)
        cat_amount = cat_amounts.get(method, 0)
        
        difference, mode = calculate_difference(pos_amount, cat_amount)

        st.write(method)
        st.write("POS:", pos_amount)
        st.write("CAT:", cat_amount)
        st.write("差額:", difference)
        st.write("mode:", mode)
       


# def cat_credit_input():
#     cat_credit = st.number_input("CATクレジット", min_value=0, step=1)
#     return cat_credit


# def cat_suica_input():
#     cat_suica = st.number_input("CAT交通系IC", min_value=0, step=1)
#     return cat_suica


# def cat_emoney_input():
#     cat_emoney = {}
#     for emoney_name in CAT_EMONEY_METHODS:
#         cat_emoney[emoney_name] = st.number_input(emoney_name, min_value=0, step=1)

#     emoney_total = calculate_payment_total(cat_emoney)
#     st.write("CAT電子マネー総額:", emoney_total)


# def cat_jpqr_input():
#     cat_jpqr = {}
#     for jpqr_name in CAT_JPQR_METHODS:
#         cat_jpqr[jpqr_name] = st.number_input(jpqr_name, min_value=0, step=1)

#     jpqr_total = calculate_payment_total(cat_jpqr)
#     st.write("CAT国内QR総額:", jpqr_total)


# def cat_chqr_input():
#     cat_chqr = {}
#     for chqr_name in CAT_CHQR_METHODS:
#         cat_chqr[chqr_name] = st.number_input(chqr_name, min_value=0, step=1)

#     chqr_total = calculate_payment_total(cat_chqr)
#     st.write("CAT中国QR総額:", chqr_total)


if __name__ == "__main__":
    cat_amounts_temp = cat_input()
    pos_amounts = pos_input()
    cat_amounts = reconcile_cat_amounts(cat_amounts_temp)
    compare_payment_amounts(pos_amounts, cat_amounts)