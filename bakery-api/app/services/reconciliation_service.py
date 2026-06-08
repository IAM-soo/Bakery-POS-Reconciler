from app.constants.payment_methods import PAYMENT_GROUPS, POS_METHODS

def calculate_selected_payment_total(payment_amounts, selected_methods):
    total = 0
    for method in selected_methods:
        total += payment_amounts.get(method + "_sales", 0) - payment_amounts.get(method + "_cancel", 0)
    return total


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


def compare_payment_amounts(pos_amounts, cat_amounts):
    comparison_results = []
    for method in POS_METHODS:
        pos_amount = pos_amounts.get(method, 0)
        cat_amount = cat_amounts.get(method, 0)
        difference, mode = calculate_difference(pos_amount, cat_amount)

        result = {"method": method, "pos_amount": pos_amount, "cat_amount": cat_amount, "difference": difference, "mode": mode}

        comparison_results.append(result)

    return comparison_results


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
        # If mode is not recognized, raise ValueError.
        raise ValueError(f"Invalid mode: {mode}")


def find_combinations(products, target_amount, max_items=8, max_results=3):
    if target_amount <= 0:
        return []

    # This function solves a variant of the subset-sum problem.
    #   In this project, the "numbers" are product prices and the target is the
    #   correction amount the operator needs to re-enter into the POS system.
    #
    # Algorithm: recursive backtracking
    #   Build a combination one product at a time.
    #   At each step, try adding each product to the current combination.
    #   If the running total exceeds target_amount, stop that path and backtrack.
    #   If the running total equals target_amount, save the combination.
    #
    # Items are tried in increasing count (1, then 2, then 3...) so that
    # simpler corrections — fewer items to re-enter at the POS — come first.
    #
    # products:
    #   List of products loaded from menu.json.

    # This list stores all valid combinations found by the search.
    results = []

    def search(start_index, remaining_amount, current_combination, item_limit):
        # This is a recursive helper function.
        # It tries to build one combination step by step.
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

        if remaining_amount == 0:
            # Only accept this combination if the number of selected products
            # is exactly equal to item_limit.
            if len(current_combination) == item_limit:
                results.append(current_combination)

            # Stop this search path because the amount already matched.
            return

        if remaining_amount < 0:
            return

        if len(current_combination) >= item_limit:
            return

        # Try each product from start_index to the end of products.
        #
        # range(start_index, len(products)) creates indexes like:
        # start_index, start_index + 1, start_index + 2, ...
        # range(start_index, ...) — not range(0, ...) — so once we move past
        # a product we never reconsider it from an earlier position,
        # avoiding duplicates like [salt bread, croissant] vs [croissant, salt bread].
        for i in range(start_index, len(products)):
            # Get one product from the products list by index.
            product = products[i]

            # Create a new combination by adding the selected product.
            #
            # This does not directly change current_combination.
            # It creates a new list instead.
            new_combination = current_combination + [product]
            # Continue searching after choosing this product.
            #
            # i (not i + 1): allows picking the same product again,
            #   Example: salt bread x 2
            search(i, remaining_amount - product["price"], new_combination, item_limit)

    for item_limit in range(1, max_items + 1):
        search(0, target_amount, [], item_limit)

        # If enough results are found, stop trying larger item counts.
        if len(results) >= max_results:
            break

    # Return all valid combinations found.
    return results


def format_combinations(combinations):
    formatted_combinations = []

    for combination_number, combination in enumerate(combinations, start=1):
        total = 0

        # item_counts is used to group the same products together.
        # It stores:
        # - salt bread 318 x 2
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

        formatted_combination = {"combination_number": combination_number, "items": list(item_counts.values()), "total": total}
        formatted_combinations.append(formatted_combination)
    return formatted_combinations
