import json
import os


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

            # Return the cleaned product list to the caller.
            return active_products

    except FileNotFoundError:
        # This runs if menu.json cannot be found.
        print("ファイルが存在しません")
        return []

    except json.JSONDecodeError:
        # This runs if menu.json exists but the JSON format is broken.
        print("JSONファイル解析エラー")
        return []



#def sum_amounts(amount):
#   total = 0
#
#   for amount in amounts:
#       tatal += amount
#       
#   return total


def cat_emoney_input():
    cat_emoney = {"楽天Edy": 0, "ID":0, "QUICPay":0, "WAON":0, "nanaco":0}
    for emoney_name in cat_emoney:
        cat_emoney[emoney_name] = input_int(emoney_name + "の金額を入力してください＞")

    cat_emoney_total = sum(cat_emoney.values())
    return cat_emoney, cat_emoney_total
    
def cat_QR_input():
    cat_QR = {"楽天Pay": 0, "PayPay":0, "auPay":0, "d払い":0, "JCoinPay":0}
    for QR_name in cat_QR:
        cat_QR[QR_name] = input_int(QR_name + "の金額を入力してください＞")

    cat_QR_total = sum(cat_QR.values())
    return cat_QR, cat_QR_total



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


#Force user to input in number
def input_int(message):
    while True:
        user_input = input(message)

        try:
            return int(user_input)
        
        except ValueError:
            print("数字を入力してください")

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
    products = load_menu()

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
    emoney_input()
    #run_tools_select()




    

        
