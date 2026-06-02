import json
import os


# =========================
# Data loading
# =========================

def load_menu():
    # __file__ means the path of this Python file.
    # os.path.dirname(__file__) gets the folder that contains this file.
    base_path = os.path.dirname(__file__)

    # Create the path to data/menu.json.
    # Example:
    # base_path = ".../Bakery-POS-Reconciler"
    # menu_path = ".../Bakery-POS-Reconciler/data/menu.json"
    menu_path = os.path.join(base_path, "data", "menu.json")

    try:
        # Open menu.json in read-only mode.
        # encoding="utf-8" is needed because the menu contains Japanese text.
        with open(menu_path, "r", encoding="utf-8") as f:
            # json.load(f) reads the JSON file and converts it into Python data.
            # After this line, data becomes a Python dictionary.
            data = json.load(f)

            # Keep only active products.
            # p.get("is_active", True) means:
            # - If the product has is_active, use that value.
            # - If the product does not have is_active, treat it as True.
            active_products = [p for p in data["item"] if p.get("is_active", True)]

            # Convert each product price into an integer.
            # This is necessary because JSON data may store price as text.
            for p in active_products:
                p["price"] = int(p["price"])

            menu_last_update = data["last_updated"]

            # Return the cleaned product list to the caller.
            return active_products, menu_last_update

    except FileNotFoundError:
        # This runs if menu.json cannot be found.
        print("ファイルが存在しません")
        return [], "不明"

    except json.JSONDecodeError:
        # This runs if menu.json exists but the JSON format is broken.
        print("JSONファイル解析エラー")
        return [], "不明"


# =========================
# Payment method definitions
# =========================

# POS side payment categories.
# These are the final categories shown on the POS system.
# pos_amounts will use these names as dictionary keys.
#
# Example:
# pos_amounts = {
#     "クレジットカード": 12000,
#     "電子マネー": 10000,
#     "国内QR": 7600
# }
POS_METHODS = [
    "クレジットカード",
    "交通系IC",
    "金券",
    "国内QR",
    "中国QR",
    "電子マネー",
]


# CAT-side payment detail method definitions.
#
# These lists define the payment methods shown separately on the CAT terminal.
# They do not store amounts.
#
# Example:
# cat_amounts_temp = {
#     "楽天Edy": 3000,
#     "iD": 2000,
#     "PayPay": 4000
# }
#
# These method lists are used by PAYMENT_GROUPS to map CAT details
# back into POS-style payment categories.

CAT_EMONEY_METHODS = ["楽天Edy", "iD", "QUICPay", "WAON", "nanaco"]
CAT_JPQR_METHODS = ["d払い", "PayPay", "au PAY", "楽天ペイ", "J-Coin Pay"]
CAT_CHQR_METHODS = ["Alipay", "WeChatPay"]


# Mapping between POS categories and CAT detail methods.
#
# POS groups some payment methods together.
# CAT may show them separately.
#
# Example:
# POS "電子マネー"
# = CAT "楽天Edy" + "iD" + "QUICPay" + "WAON" + "nanaco"
#
# This mapping is used by reconcile_cat_amounts()
# to convert CAT detail amounts into POS-style category amounts.
PAYMENT_GROUPS = {
    "クレジットカード": ["クレジットカード"],
    "交通系IC": ["交通系IC"],
    "電子マネー": CAT_EMONEY_METHODS,
    "中国QR": CAT_CHQR_METHODS,
    "国内QR": CAT_JPQR_METHODS,
    "金券": ["金券"],
}

# =========================
# Core logic
# Web app can reuse these functions
# =========================

def calculate_payment_total(payment_amounts):
    return sum(payment_amounts.values())


# Purpose:
#   Calculate the net total for selected CAT payment methods.
#
# Input:
#   payment_amounts
#   selected_methods
#
# Output:
#   total
#
# Data shape:
#   payment_amounts = {
#       "楽天Edy_sales": 3000,
#       "楽天Edy_cancel": 500,
#       "iD_sales": 2000,
#       "iD_cancel": 0
#   }

# Note:
#   Net amount is calculated as sales - cancel.

def calculate_selected_payment_total(payment_amounts, selected_methods):
    total = 0
    for method in selected_methods:
        total += payment_amounts.get(method + "_sales", 0) - payment_amounts.get(method + "_cancel", 0) 
    return total


# Purpose:
#   Convert CAT detail amounts into POS-style category totals.
#
# Input:
#   cat_amounts_temp
#
# Output:
#   cat_amounts
#
# Data shape:
#   cat_amounts_temp = {
#       "楽天Edy_sales": 3000,
#       "楽天Edy_cancel": 500,
#       "iD_sales": 2000,
#       "iD_cancel": 0
#   }
#
#   cat_amounts = {
#       "電子マネー": 4500,
#       "国内QR": 7600
#   }
#
# Note:
#   The output keys match POS_METHODS, so compare_payment_amounts() can compare POS and CAT directly.

def reconcile_cat_amounts(cat_amounts_temp):
    cat_amounts = {}
    for payment_method in POS_METHODS:
        selected_methods = PAYMENT_GROUPS[payment_method]
        cat_amounts[payment_method] = calculate_selected_payment_total(cat_amounts_temp, selected_methods)

    return cat_amounts


def calculate_difference(pos_amount, cat_amount):
    if pos_amount > cat_amount:
        difference = pos_amount - cat_amount
        mode = "POS_GT_CAT"
        return (difference, mode)
    elif cat_amount > pos_amount:
        difference = cat_amount - pos_amount
        mode = "CAT_GT_POS"
        return (difference, mode)
    else:
        difference = 0
        mode = "MATCH"
        return (difference, mode)


# Compare POS category amounts with reconciled CAT category amounts.
#
# Input:
# pos_amounts:
# {
#     "電子マネー": 10000,
#     "国内QR": 7600
# }
#
# cat_amounts:
# {
#     "電子マネー": 9790,
#     "国内QR": 7600
# }
#
# Output:
# comparison_results is a list of dictionaries.
#
# Example:
# comparison_results = [
#     {
#         "method": "電子マネー",
#         "pos_amount": 10000,
#         "cat_amount": 9790,
#         "difference": 210,
#         "mode": "POS_GT_CAT"
#     }
# ]

def compare_payment_amounts(pos_amounts, cat_amounts):
    comparison_results = []
    for method in POS_METHODS:
        pos_amount = pos_amounts.get(method, 0)
        cat_amount = cat_amounts.get(method, 0)
        difference, mode = calculate_difference(pos_amount, cat_amount)

        result = {"method":method, "pos_amount":pos_amount, "cat_amount":cat_amount, "difference":difference, "mode":mode}

        comparison_results.append(result)

    return comparison_results


# Extract only mismatched payment results.
#
# Input:
# comparison_results
#
# Output:
# mismatch_results
#
# mismatch_results keeps only results where mode is not "MATCH".
#
# Example:
# comparison_results = [
#     {"method": "クレジットカード", "mode": "MATCH"},
#     {"method": "電子マネー", "mode": "POS_GT_CAT"}
# ]
#
# mismatch_results = [
#     {"method": "電子マネー", "mode": "POS_GT_CAT"}
# ]

def filter_mismatches(comparison_results):
    mismatch_result = []

    for result in comparison_results:
        if result["mode"] != "MATCH":
            mismatch_result.append(result)
    
    return mismatch_result


def calculate_target_amount(cancelled_amount, difference, mode):
    # This function calculates the corrected target amount.
    #
    # cancelled_amount:
    #   The original POS transaction amount that needs to be cancelled.
    #
    # difference:
    #   The difference between POS and CAT.
    #
    # mode:
    #   POS_GT_CAT means POS amount is greater than CAT amount.
    #   CAT_GT_POS means CAT amount is greater than POS amount.

    if mode == "POS_GT_CAT":
        # If POS is greater than CAT,
        # the corrected POS amount should be smaller.
        #
        # Example:
        # cancelled_amount = 1400
        # difference = 210
        # target_amount = 1400 - 210 = 1190
        target_amount = cancelled_amount - difference
        return target_amount

    elif mode == "CAT_GT_POS":
        # If CAT is greater than POS,
        # the corrected POS amount should be larger.
        #
        # Example:
        # cancelled_amount = 1000
        # difference = 200
        # target_amount = 1000 + 200 = 1200
        target_amount = cancelled_amount + difference
        return target_amount

    else:
        # If mode is not recognized, return None.
        print("Invalid mode")
        return None


def find_combinations(products, target_amount, max_items=8, max_results=3):
    # This function searches for product combinations
    # whose total price is exactly equal to target_amount.
    #
    # products:
    #   List of products loaded from menu.json.
    #
    # target_amount:
    #   The amount we want to match.
    #
    # max_items:
    #   Maximum number of products allowed in one combination.
    #
    # max_results:
    #   Maximum number of combinations to save.

    # This list stores all valid combinations found by the search.
    results = []

    def search(start_index, remaining_amount, current_combination, item_limit):
        # This is a recursive helper function.
        # It tries to build one combination step by step.
        #
        # start_index:
        #   The index in products where this search starts.
        #   This prevents duplicated order patterns like A+B and B+A.
        #
        # remaining_amount:
        #   The amount that still needs to be matched.
        #   Example:
        #   target_amount = 1190
        #   choose 318 yen product
        #   remaining_amount becomes 1190 - 318 = 872
        #
        # current_combination:
        #   The products already selected in the current search path.
        #
        # item_limit:
        #   The exact number of items allowed in this round.
        #   It comes from:
        #   for item_limit in range(1, max_items + 1)

        # Stop searching if we already found enough results.
        if len(results) >= max_results:
            return

        # If remaining_amount becomes 0,
        # the selected products match the target amount.
        if remaining_amount == 0:

            # Only accept this combination if the number of selected products
            # is exactly equal to item_limit.
            if len(current_combination) == item_limit:
                results.append(current_combination)

            # Stop this search path because the amount already matched.
            return

        # If remaining_amount is negative,
        # the selected products are too expensive.
        # Example:
        # target = 1190
        # selected total = 1300
        # remaining_amount = -110
        if remaining_amount < 0:
            return

        # If the current combination already has item_limit products,
        # but remaining_amount is not 0,
        # this path failed.
        #
        # Example:
        # item_limit = 3
        # current_combination already has 3 products
        # remaining_amount is still 200
        # We cannot add a 4th product, so stop.
        if len(current_combination) >= item_limit:
            return

        # Try each product from start_index to the end of products.
        #
        # range(start_index, len(products)) creates indexes like:
        # start_index, start_index + 1, start_index + 2, ...
        for i in range(start_index, len(products)):

            # Get one product from the products list by index.
            product = products[i]

            # Create a new combination by adding the selected product.
            #
            # This does not directly change current_combination.
            # It creates a new list instead.
            #
            # Example:
            # current_combination = [A, B]
            # product = C
            # new_combination = [A, B, C]
            new_combination = current_combination + [product]

            # Continue searching after choosing this product.
            #
            # i:
            #   Start from the same index again.
            #   This allows the same product to be selected multiple times.
            #   Example: salt bread x 2
            #
            # remaining_amount - product["price"]:
            #   Subtract the selected product price from the remaining amount.
            #
            # new_combination:
            #   Pass the updated product combination to the next search.
            #
            # item_limit:
            #   Keep the same item count limit in this round.
            search(i, remaining_amount - product["price"], new_combination, item_limit)

    # Try combinations with 1 item, then 2 items, then 3 items...
    #
    # If max_items = 8:
    # range(1, max_items + 1) becomes range(1, 9)
    # The actual item_limit values are:
    # 1, 2, 3, 4, 5, 6, 7, 8
    for item_limit in range(1, max_items + 1):

        # Start searching with:
        # start_index = 0          -> start from the first product
        # remaining_amount = target_amount
        # current_combination = [] -> no product selected yet
        # item_limit = current item limit, such as 1, 2, 3...
        search(0, target_amount, [], item_limit)

        # If enough results are found, stop trying larger item counts.
        if len(results) >= max_results:
            break

    # Return all valid combinations found.
    return results


# =========================
# Output formatting
# =========================

# Convert raw product combinations into display-friendly data.
#
# Input:
# combinations
# [
#     [product, product, product],
#     [product, product]
# ]
#
# Output:
# formatted_combinations
#
# formatted_combinations is a list of dictionaries.
# Each dictionary represents one possible product combination.
#
# Example:
# formatted_combinations = [
#     {
#         "combination_number": 1,
#         "items": [
#             {
#                 "item_name": "トリュフ塩パン",
#                 "price": 318,
#                 "quantity": 2
#             }
#         ],
#         "total": 636
#     }
# ]
#
# item_counts is used internally to merge the same product
# into one row with quantity.

def format_combinations(combinations):
    # enumerate(combinations, start=1) gives:
    # combination_number = 1, combination = first combination
    # combination_number = 2, combination = second combination
    formatted_combinations = []

    for combination_number, combination in enumerate(combinations, start=1):

        # Store the total price of this combination.
        total = 0
        item_counts = {}
        for product in combination:
            product_id = product["id"]

            # Add this product price to the total.
            total += product["price"]

            # If this product id appears for the first time,
            # create a new record in item_counts.
            if product_id not in item_counts:
                item_counts[product_id] = {
                    "item_name": product["item_name"],
                    "price": product["price"],
                    "quantity": 0
                }

            # Increase the quantity of this product by 1.
            item_counts[product_id]["quantity"] += 1

        formatted_combination = {"combination_number":combination_number, "items":list(item_counts.values()), "total":total}
        formatted_combinations.append(formatted_combination)
    
    return formatted_combinations


# Purpose:
#   Extract payment method names from mismatch_results for Streamlit selectbox.
#
# Input:
#   mismatch_results
#
# Output:
#   mismatch_methods
#
# Data shape:
#   mismatch_methods = ["電子マネー", "国内QR"]

def get_mismatch_methods(mismatch_results):
    mismatch_methods = []
    for result in mismatch_results:
        mismatch_methods.append(result["method"])
    
    return mismatch_methods


# Purpose:
#   Find the full mismatch result dictionary by selected payment method.
#
# Input:
#   mismatch_results
#   selected_method
#
# Output:
#   selected_result
#
# Note:
#   selected_method comes from mismatch_methods, so it should normally exist in mismatch_results.

def find_result_by_method(mismatch_results, selected_method):
    selected_result = None
    for result in mismatch_results:
        if result["method"] == selected_method:
            selected_result = result

    return selected_result

        
def print_combinations(combinations):
    # Print each valid combination.
    #
    # enumerate(combinations, start=1) gives:
    # combination_number = 1, combination = first combination
    # combination_number = 2, combination = second combination
    # ...
    for combination_number, combination in enumerate(combinations, start=1):
        print()
        print("組合", combination_number)

        # Store the total price of this combination.
        total = 0

        # item_counts is used to group the same products together.
        #
        # Example:
        # Instead of printing:
        # - salt bread
        # - salt bread
        #
        # It can print:
        # - salt bread 318 x 2
        item_counts = {}

        # Check each product in this combination.
        for product in combination:
            product_id = product["id"]

            # Add this product price to the total.
            total += product["price"]

            # If this product id appears for the first time,
            # create a new record in item_counts.
            if product_id not in item_counts:
                item_counts[product_id] = {
                    "item_name": product["item_name"],
                    "price": product["price"],
                    "quantity": 0
                }

            # Increase the quantity of this product by 1.
            item_counts[product_id]["quantity"] += 1

        # Print grouped product information.
        #
        # item_counts.values() gives only the stored product information,
        # not the product ids.
        for item in item_counts.values():
            print("-", item["item_name"], item["price"], "x", item["quantity"])

        # Print the total price of this combination.
        print("総額:", total)


# =========================
# CLI input helpers
# Terminal only
# =========================

def cat_emoney_input():
    cat_emoney = {}
    for emoney_name in CAT_EMONEY_METHODS:
        cat_emoney[emoney_name] = input_int(emoney_name + "の金額を入力してください＞")

    cat_emoney_total = calculate_payment_total(cat_emoney)
    return cat_emoney, cat_emoney_total
    
def cat_jpqr_input():
    cat_jpqr = {}
    for jpqr_name in CAT_JPQR_METHODS:
        cat_jpqr[jpqr_name] = input_int(jpqr_name + "の金額を入力してください＞")

    cat_jpqr_total = calculate_payment_total(cat_jpqr)
    return cat_jpqr, cat_jpqr_total

def cat_chqr_input():
    cat_chqr = {}
    for chqr_name in CAT_CHQR_METHODS:
        cat_chqr[chqr_name] = input_int(chqr_name + "の金額を入力してください＞")

    cat_chqr_total = calculate_payment_total(cat_chqr)
    return cat_chqr, cat_chqr_total


#Force user to input in number
def input_int(message):
    while True:
        user_input = input(message)

        try:
            return int(user_input)
        
        except ValueError:
            print("数字を入力してください")


# =========================
# CLI workflows
# Terminal only
# =========================

#Difference checker
def run_difference_checker():
    pos_amount = input_int("POS金額を入力してください＞")
    cat_amount = input_int("CAT金額を入力してください＞")

    difference, mode = calculate_difference(pos_amount, cat_amount)

    if mode == "POS_GT_CAT":
        print("POSの方が多いです")
    elif mode == "CAT_GT_POS":
        print("CATの方が多いです")
    elif mode == "MATCH":
        print("両方一致しています")
    
    print("差額", difference)
    print(mode)


#Correction helper
def run_correction_helper():
    products, _ = load_menu()

    input_cancelled_amount = input_int("取消金額を入力してください＞")
    
    input_difference = input_int("差額を入力してください＞")
    
    input_mode = input_int("どちらが多いを入力してください？（POS:1 CAT:2）＞")

    if input_mode == 1:
        mode = "POS_GT_CAT"    
        
    elif input_mode == 2:
        mode = "CAT_GT_POS"

    else:
        print("入力間違いを確認してください")
        return
    
    target = calculate_target_amount(input_cancelled_amount,input_difference, mode)
    combinations = find_combinations(products, target)
    
    print("目標金額", target)
    print("found", len(combinations))
    if len(combinations) == 0:
        print("この取消金額で該当する商品組み合わせが見つかりませんでした。")
    else:
        print_combinations(combinations)

#Tools selector
def run_tools_select():
    tools = input_int("ツールを選択してください＞(Checker: 1 Correction: 2)")
    if tools == 1:
        run_difference_checker()
        return
    elif tools == 2:
        run_correction_helper()
        return
    else:
        print("入力間違いを確認してください")
        return


if __name__ == "__main__":
    run_tools_select()




    

        
