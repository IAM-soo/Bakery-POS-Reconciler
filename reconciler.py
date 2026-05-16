import json
import os

def load_menu():
    # Get the directory path of this Python file
    base_path = os.path.dirname(__file__)
    menu_path = os.path.join(base_path, 'data', 'menu.json')

    try:
        # Open menu.json in read-only mode using UTF-8 encoding
        with open(menu_path, 'r', encoding='utf-8') as f:
            # Convert JSON file content into Python data
            data = json.load(f)

            # Convert price values from string to integer
            active_products = [p for p in data['item'] if p.get('is_active', True)]

            for p in active_products:
                p['price'] = int(p['price'])

            return active_products
        
        
    except FileNotFoundError:
        print('ファイルが存在しません')
        return []
    
    except json.JSONDecodeError:
        print('JSONファイル解析エラー')
        return []

def calculate_target_amount(cancelled_amount, difference, mode):
    if mode == 'POS_GT_CAT':
        target_amount = cancelled_amount - difference
        return target_amount

    elif mode == 'CAT_GT_POS':
        target_amount = cancelled_amount + difference
        return target_amount

    else:
        print("Invalid mode")
        return None
    
def find_combinations(products, target_amount, max_items=8, max_results=20):
    results = []

    def search(start_index, remaining_amount, current_combination, item_limit):
        if len(results) >= max_results:
            return
        if remaining_amount == 0:
            if len(current_combination) == item_limit:
                results.append(current_combination)
            return
        if remaining_amount < 0:
            return
        if len(current_combination) >= item_limit:
            return
        
        for i in range(start_index, len(products)):
            product = products[i]
            new_combination = current_combination + [product]
            search(i, remaining_amount - product["price"], new_combination, item_limit)

    for item_limit in range(1, max_items + 1):
        search(0, target_amount, [], item_limit)
        if len(results) >= max_results:
            break

    return results


def print_combinations(combinations):
    for combination_number, combination in enumerate(combinations, start=1):
        print()
        print("combination", combination_number)

        total = 0
        item_counts = {}

        for product in combination:
            product_id = product["id"]
            total += product["price"]

            if product_id not in item_counts:
                item_counts[product_id] = {
                    "item_name": product["item_name"],
                    "price": product["price"],
                    "quantity": 0
                }

            item_counts[product_id]["quantity"] += 1

        for item in item_counts.values():
            print("-", item["item_name"], item["price"], "x", item["quantity"])

        print("total:", total)


#Test section

if __name__ == "__main__":
    products = load_menu()

    print("product count:", len(products))
    print(products[:3])

    target = calculate_target_amount(1400, 210, 'POS_GT_CAT')
    combinations = find_combinations(products, target, max_items=8, max_results=20)
    print("target", target)
    print("found", len(combinations))
    print_combinations(combinations[:3])

