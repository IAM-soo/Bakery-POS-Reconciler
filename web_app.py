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
    comparison_results = []
    for method in POS_METHODS:
        pos_amount = pos_amounts.get(method, 0)
        cat_amount = cat_amounts.get(method, 0)
        difference, mode = calculate_difference(pos_amount, cat_amount)

        result = {"method":method, "pos_amount":pos_amount, "cat_amount":cat_amount, "difference":difference, "mode":mode}

        comparison_results.append(result)

    return comparison_results

   
def show_difference(comparison_results):
    for result in comparison_results:
        st.write(result["method"])
        st.write("POS:", result["pos_amount"])
        st.write("CAT:", result["cat_amount"])
        st.write("差額:", result["difference"])
        if result["mode"] == "POS_GT_CAT":
            st.write("POS側が多い")
        elif result["mode"] == "CAT_GT_POS":
            st.write("CAT側が多い")
        else:
            st.write("合ってます")
       

if __name__ == "__main__":
    cat_amounts_temp = cat_input()
    pos_amounts = pos_input()
    cat_amounts = reconcile_cat_amounts(cat_amounts_temp)
    comparison_results = compare_payment_amounts(pos_amounts, cat_amounts)
    show_difference(comparison_results)