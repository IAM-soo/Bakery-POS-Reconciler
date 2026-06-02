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
    format_combinations,
    get_mismatch_methods,
    find_result_by_method
)

# =========================
# UI helper function
# =========================

# Purpose:
# Create POS amount input fields
#
# Input:
#   reset_count
#
# Output:
#   pos_amounts
#
# Data shape:
#   {
#       "クレジットカード": 12000,
#       "電子マネー": 10000,
#       "国内QR": 7600
#   }
#
# Note:
#   POS amounts are already grouped by POS categories
#   If input is blank, assume as 0
#   reset_count is used to reset Streamlit widget keys

def pos_input(reset_count):
    pos_amounts ={}
    
    for pos_method in POS_METHODS:
        pos_amounts[pos_method] = st.number_input(pos_method, min_value=0, value=None, step=1, key="pos_" + pos_method + "_" + str(reset_count))
        if pos_amounts[pos_method] == None:
            pos_amounts[pos_method] = 0
    return pos_amounts


# Purpose:
# Create CAT amount input fields
#
# Input:
#   rest_count
#
# Output:
#   cat_amounts_temp
#
# Data shape:
#   {
#       "クレジットカード_sales": 3000,
#       "クレジットカード_cancel": 200,
#       "iD_sales": 2000, 
#       "iD_cancel": 0,
#   }
#
# Note:
#   Sales input always shown
#   Cancel input only shown when checkbox is checked
#   If input is blank, assume as 0
#   rest_count is used to reset Streamlit widget keys

def cat_input(reset_count):
    cat_amounts_temp= {}

    for payment_group in PAYMENT_GROUPS:
        cat_methods = PAYMENT_GROUPS[payment_group]

        for cat_method in cat_methods:
            cat_amounts_temp[cat_method + "_sales"] = st.number_input(cat_method + " 売上", min_value=0, value=None, step=1, key="cat_" + cat_method + "_" + str(reset_count))
            if cat_amounts_temp[cat_method + "_sales"] == None:
                cat_amounts_temp[cat_method + "_sales"] = 0
            
            cat_method_cancel = st.checkbox("取消あり", key="cat_" + cat_method + "_cancel" + "_key_" + str(reset_count))
            if cat_method_cancel:
                cat_amounts_temp[cat_method + "_cancel"] = st.number_input(cat_method + " 取消", min_value=0, value=None, step=1, key="cat_" + cat_method + "_cancel" + "_" + str(reset_count))
                if cat_amounts_temp[cat_method + "_cancel"] == None:
                    cat_amounts_temp[cat_method + "_cancel"] = 0
                elif cat_amounts_temp[cat_method + "_cancel"] > cat_amounts_temp[cat_method + "_sales"]:
                    st.warning("取消金額が売上金額より大きいです。入力内容を確認してください。")
            else:
                cat_amounts_temp[cat_method + "_cancel"] = 0

        st.divider()

    return cat_amounts_temp


# Purpose:
#   Display comparison results in Streamlit app
#
# Input:
#   comparison_results
#
# Output:
#   None
#
# Data shape:
#   [
#       {
#           "method": "電子マネー",
#           "pos_amount": 10000,
#           "cat_amount": 9790,
#           "difference": 210,
#           "mode": "POS_GT_CAT"
#       }
#   ]
#
# Note:
#   MATCH results show shortly as OK
#   Mismatched result show detail of each amount, difference and mode

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
        st.divider()


# Purpose:
#   Display possible combination which reach the target amount
#
# Input:
#   formatted_combinations
#
# Output:
#   None
#
# Data shape:
#   [
#       {
#           "combination_number": 1,
#           "items": [
#               {
#                   "item_name": "トリュフ塩パン",
#                   "price": 318,
#                   "quantity": 2
#               }
#           ],
#           "total": 636
#       }
#   ]
#
# Note:
#   This function only display data
#   Product grouping is already done by format_combinations()

def show_combination_results(formatted_combinations):
    for formatted_combination in formatted_combinations:
        combination_number = formatted_combination["combination_number"]
        items = formatted_combination["items"]
        st.write("組合", combination_number)
        for item in items:
            st.write("-", item["item_name"], item["price"], "x", item["quantity"])
        
        st.write("総額:", formatted_combination["total"])
        st.divider()
        


# =========================
# main app flow
# =========================

if __name__ == "__main__":

    st.title("Bakery POS Reconciler")

    st.write("Version: v1.1.0")

    products, menu_last_update = load_menu()
    st.write("メニュー更新日:", menu_last_update)
    st.write("商品数:", len(products))

    with st.expander("使い方・注意事項", expanded=False):
        st.write("""
        1. POS金額を入力してください。
        2. CAT端末の各決済金額を入力してください。
        3. CAT端末の取消ありの場合、取消あり」にチェックを入れて、取消金額を入力してください。
        4. 差額結果を確認してください。
        5. 差額がある場合は、差額修正ツールで修正する項目を選択してください。
        6. POSで取消希望の取引金額を入力してください。
        7. CAT端末が多い場合は、POS側で差額分を追加できる可能性があります。
        8. 目標金額と商品組み合わせ候補を確認してください。
                 
        注意：
        - まだテスト版です。
        - 実際に修正する前に、必ずPOS画面とCAT端末の金額を再確認してください。
        - 候補が出ない場合は、別の取消金額を試してください。
        """)

    if "reset_count" not in st.session_state:
        st.session_state["reset_count"] = 0

    if st.button("入力をリセット"):
        st.session_state["reset_count"] += 1
        st.rerun()

    reset_count = st.session_state["reset_count"]

    st.header("差額チェック")

    with st.expander("POS金額"):
        pos_amounts = pos_input(reset_count)
    
    with st.expander("CAT金額"):
        cat_amounts_temp = cat_input(reset_count)
    
    st.divider()

    cat_amounts = reconcile_cat_amounts(cat_amounts_temp)
    comparison_results = compare_payment_amounts(pos_amounts, cat_amounts)
    
    st.subheader("差額結果")
    show_difference_summary(comparison_results)
    
    mismatch_results = filter_mismatches(comparison_results)

    if len(mismatch_results) > 0:
        st.divider()

        st.subheader("差額修正ツール")
        mismatch_methods = get_mismatch_methods(mismatch_results)

        selected_method = st.selectbox("修正する項目", mismatch_methods)
        selected_result = find_result_by_method(mismatch_results, selected_method)

        st.write("差額:", selected_result["difference"])

        if selected_result["mode"] == "POS_GT_CAT":
            st.write("POS側が多いです。")
            st.write("POSの注文履歴から取消する取引を1つ選び、その金額を入力してください。")
        elif selected_result["mode"] == "CAT_GT_POS":
            st.write("CAT側が多いです。")
            st.write("POS側に差額分を追加できる可能性があります。")
            st.write("合う候補がない場合は、POSで取消する取引金額を入力してください。")

        cancelled_amount = st.number_input("取消金額", min_value=0, value=0, step=1, key="cancelled_amount_" + str(reset_count))

        target_amount = calculate_target_amount(cancelled_amount, selected_result["difference"], selected_result["mode"])

        if target_amount <= 0:
            st.write("取消金額が差額より小さいため修正できません")
        else:
            st.write("目標金額", target_amount)
            st.divider()
            combinations = find_combinations(products, target_amount, max_items=8, max_results=3)
            if len(combinations) > 0:
                formatted_combinations = format_combinations(combinations)
                show_combination_results(formatted_combinations)
            else:
                st.write("候補なし")
    
    

    
    
    