import streamlit as st

from reconciler import(
    load_menu,
    POS_METHODS,
    PAYMENT_GROUPS,
    reconcile_cat_amounts,
    compare_payment_amounts,
    filter_mismatches,
    calculate_target_amount,
    find_combinations,
    format_combinations
)

st.title("Bakery POS Reconciler")

products = load_menu()
st.write("商品数:", len(products))


# =========================
# Diffrence Checker
# 差額計算ツール
# =========================

st.header("差額チェック")

# Create CAT input fields in the web app.
#
# Output:
# cat_amounts_temp
#
# cat_amounts_temp is the raw CAT-side detail dictionary.
# Its keys are CAT detail methods, not POS categories.
#
# Example:
# cat_amounts_temp = {
#     "楽天Edy": 3000,
#     "iD": 2000,
#     "PayPay": 4000,
#     "Alipay": 1000
# }
#
# This data cannot be directly compared with pos_amounts yet.
# It must be converted by reconcile_cat_amounts().

def cat_input():
    cat_amounts_temp= {}

    for payment_group in PAYMENT_GROUPS:
        cat_methods = PAYMENT_GROUPS[payment_group]

        for cat_method in cat_methods:
            cat_amounts_temp[cat_method] = st.number_input(cat_method, min_value=0, step=1, key="cat_" + cat_method)

    return cat_amounts_temp


# Create POS input fields in the web app.
#
# Output:
# pos_amounts
#
# pos_amounts is already grouped by POS categories.
#
# Example:
# pos_amounts = {
#     "クレジットカード": 12000,
#     "交通系IC": 3500,
#     "電子マネー": 10000,
#     "国内QR": 7600
# }

def pos_input():
    pos_amounts ={}
    
    for pos_method in POS_METHODS:
        pos_amounts[pos_method] = st.number_input(pos_method, min_value=0, step=1, key="pos_" + pos_method)

    return pos_amounts


# def show_difference(comparison_results):
#     for result in comparison_results:
#         st.write(result["method"])
#         st.write("POS:", result["pos_amount"])
#         st.write("CAT:", result["cat_amount"])
#         st.write("差額:", result["difference"])
#         if result["mode"] == "POS_GT_CAT":
#             st.write("POS側が多い")
#         elif result["mode"] == "CAT_GT_POS":
#             st.write("CAT側が多い")
#         else:
#             st.write("合ってます")


def show_difference_summary(comparison_results):
    for result in comparison_results:
        if result["mode"] == "MATCH":
            st.write(result["method"], ": OK!")
        else:
            st.write(result["method"], " :")
            st.write("POS:", result["pos_amount"])
            st.write("CAT:", result["cat_amount"])
            st.write("差額:", result["difference"])
            if result["mode"] == "POS_GT_CAT":
                st.write("POS側が多い")
            elif result["mode"] == "CAT_GT_POS":
                st.write("CAT側が多い")
        
# Display the correction helper UI.
#
# This function uses mismatch_results from the difference checker.
# The user does not need to input difference or mode again.
#
# Flow:
# 1. Select one mismatched payment method
# 2. Input cancelled POS transaction amount
# 3. Calculate target amount
# 4. Search product combinations
# 5. Display candidate combinations

def show_correction_helper(mismatch_results, products):
    if len(mismatch_results) != 0:
        mismatch_methods = []
        for result in mismatch_results:
            mismatch_methods.append(result["method"])
        
        selected_method = st.selectbox("修正する項目", mismatch_methods)
        for result in mismatch_results:
            if result["method"] == selected_method:
                st.write("差額:", result["difference"])
                cancelled_amount = st.number_input("取消金額", min_value=0, step=1)
                if cancelled_amount > 0:
                    target_amount = calculate_target_amount(cancelled_amount, result["difference"], result["mode"])
                    if target_amount <= 0:
                        st.write("取消金額が差額より小さいため修正できません")
                    else:
                        st.write("目標金額", target_amount)
                        combinations = find_combinations(products, target_amount, max_items=8, max_results=3)
                        if len(combinations) > 0:
                            formatted_combinations = format_combinations(combinations)
                            for formatted_combination in formatted_combinations:
                                combination_number = formatted_combination["combination_number"]
                                items = formatted_combination["items"]
                                st.write("組合", combination_number)
                                for item in items:
                                    st.write("-", item["item_name"], item["price"], "x", item["quantity"])
                        
                                st.write("総額:", formatted_combination["total"])
                        else:
                            st.write("候補なし")
    else:
        st.write("全部合ってます")


# =========================
# Correction Helper
# 差額修正ツール
# =========================

if __name__ == "__main__":
    with st.expander("POS金額"):
        pos_amounts = pos_input()
    

    with st.expander("CAT金額"):
        cat_amounts_temp = cat_input()
    

    st.divider()

    cat_amounts = reconcile_cat_amounts(cat_amounts_temp)
    comparison_results = compare_payment_amounts(pos_amounts, cat_amounts)
    
    st.subheader("差額結果")
    show_difference_summary(comparison_results)
    
    mismatch_results = filter_mismatches(comparison_results)

    st.divider()
    if len(mismatch_results) > 0:
        st.subheader("差額修正ツール")
        show_correction_helper(mismatch_results, products)

    
    

    
    
    