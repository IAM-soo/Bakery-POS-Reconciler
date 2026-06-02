from reconciler import (
    calculate_difference,
    reconcile_cat_amounts,
    compare_payment_amounts,
    filter_mismatches,
    calculate_target_amount,
    find_combinations,
    find_result_by_method,
    format_combinations,
)


# =========================
# Helpers
# =========================

def make_cat_amounts_temp(overrides={}):
    # Build a cat_amounts_temp dict with all brands set to 0 by default.
    # Use overrides to set specific values.
    #
    # Example:
    # make_cat_amounts_temp({"楽天Edy_sales": 3000})
    # returns a dict where 楽天Edy_sales = 3000 and everything else = 0
    all_brands = [
        "クレジットカード", "交通系IC", "金券",
        "楽天Edy", "iD", "QUICPay", "WAON", "nanaco",
        "d払い", "PayPay", "au PAY", "楽天ペイ", "J-Coin Pay",
        "Alipay", "WeChatPay",
    ]
    result = {}
    for brand in all_brands:
        result[brand + "_sales"] = overrides.get(brand + "_sales", 0)
        result[brand + "_cancel"] = overrides.get(brand + "_cancel", 0)
    return result


def make_pos_amounts(overrides={}):
    # Build a pos_amounts dict with all POS categories set to 0 by default.
    categories = ["クレジットカード", "交通系IC", "金券", "国内QR", "中国QR", "電子マネー"]
    result = {c: 0 for c in categories}
    result.update(overrides)
    return result


# =========================
# calculate_difference
# =========================

def test_calculate_difference_pos_greater():
    difference, mode = calculate_difference(10000, 9790)
    assert difference == 210
    assert mode == "POS_GT_CAT"


def test_calculate_difference_cat_greater():
    difference, mode = calculate_difference(7600, 7800)
    assert difference == 200
    assert mode == "CAT_GT_POS"


def test_calculate_difference_match():
    difference, mode = calculate_difference(5000, 5000)
    assert difference == 0
    assert mode == "MATCH"


def test_calculate_difference_both_zero():
    difference, mode = calculate_difference(0, 0)
    assert difference == 0
    assert mode == "MATCH"


# =========================
# reconcile_cat_amounts
# =========================

def test_reconcile_cat_amounts_single_brand():
    # 楽天Edy 3000 belongs to 電子マネー
    cat_temp = make_cat_amounts_temp({"楽天Edy_sales": 3000})
    result = reconcile_cat_amounts(cat_temp)
    assert result["電子マネー"] == 3000


def test_reconcile_cat_amounts_with_cancel():
    # Net = sales - cancel
    cat_temp = make_cat_amounts_temp({"楽天Edy_sales": 3000, "楽天Edy_cancel": 500})
    result = reconcile_cat_amounts(cat_temp)
    assert result["電子マネー"] == 2500


def test_reconcile_cat_amounts_multiple_brands_same_group():
    # 楽天Edy + iD both belong to 電子マネー
    cat_temp = make_cat_amounts_temp({"楽天Edy_sales": 3000, "iD_sales": 2000})
    result = reconcile_cat_amounts(cat_temp)
    assert result["電子マネー"] == 5000


def test_reconcile_cat_amounts_different_groups():
    # PayPay belongs to 国内QR, Alipay belongs to 中国QR
    cat_temp = make_cat_amounts_temp({"PayPay_sales": 4000, "Alipay_sales": 1000})
    result = reconcile_cat_amounts(cat_temp)
    assert result["国内QR"] == 4000
    assert result["中国QR"] == 1000


def test_reconcile_cat_amounts_all_zero():
    cat_temp = make_cat_amounts_temp()
    result = reconcile_cat_amounts(cat_temp)
    for value in result.values():
        assert value == 0


# =========================
# compare_payment_amounts
# =========================

def test_compare_payment_amounts_all_match():
    amounts = make_pos_amounts({"電子マネー": 5000, "国内QR": 3000})
    results = compare_payment_amounts(amounts, amounts)
    for result in results:
        assert result["mode"] == "MATCH"
        assert result["difference"] == 0


def test_compare_payment_amounts_one_mismatch():
    pos = make_pos_amounts({"電子マネー": 10000})
    cat = make_pos_amounts({"電子マネー": 9790})
    results = compare_payment_amounts(pos, cat)
    emoney = next(r for r in results if r["method"] == "電子マネー")
    assert emoney["difference"] == 210
    assert emoney["mode"] == "POS_GT_CAT"


def test_compare_payment_amounts_returns_all_six_methods():
    pos = make_pos_amounts()
    cat = make_pos_amounts()
    results = compare_payment_amounts(pos, cat)
    assert len(results) == 6


# =========================
# filter_mismatches
# =========================

def test_filter_mismatches_no_mismatches():
    comparison_results = [
        {"method": "電子マネー", "mode": "MATCH"},
        {"method": "国内QR", "mode": "MATCH"},
    ]
    assert filter_mismatches(comparison_results) == []


def test_filter_mismatches_one_mismatch():
    comparison_results = [
        {"method": "電子マネー", "mode": "POS_GT_CAT"},
        {"method": "国内QR", "mode": "MATCH"},
    ]
    result = filter_mismatches(comparison_results)
    assert len(result) == 1
    assert result[0]["method"] == "電子マネー"


def test_filter_mismatches_all_mismatches():
    comparison_results = [
        {"method": "電子マネー", "mode": "POS_GT_CAT"},
        {"method": "国内QR", "mode": "CAT_GT_POS"},
    ]
    result = filter_mismatches(comparison_results)
    assert len(result) == 2


# =========================
# calculate_target_amount
# =========================

def test_calculate_target_amount_pos_gt_cat():
    # POS is greater: target = cancelled - difference
    assert calculate_target_amount(1400, 210, "POS_GT_CAT") == 1190


def test_calculate_target_amount_cat_gt_pos():
    # CAT is greater: target = cancelled + difference
    assert calculate_target_amount(1000, 200, "CAT_GT_POS") == 1200


def test_calculate_target_amount_difference_equals_cancelled():
    # Edge case: result is zero
    assert calculate_target_amount(500, 500, "POS_GT_CAT") == 0


def test_calculate_target_amount_invalid_mode():
    # Unknown mode should return None
    assert calculate_target_amount(1000, 200, "INVALID") is None


# =========================
# find_combinations
# =========================

def make_product(id, price):
    return {"id": id, "item_name": f"item_{id}", "price": price, "category": "test", "is_active": True}


def test_find_combinations_single_product_exact_match():
    products = [make_product("A", 500)]
    result = find_combinations(products, 500)
    assert len(result) == 1
    assert result[0] == [products[0]]


def test_find_combinations_two_different_products():
    products = [make_product("A", 300), make_product("B", 200)]
    result = find_combinations(products, 500)
    assert any(len(combo) == 2 for combo in result)


def test_find_combinations_repeated_product():
    # Same product used twice: 250 + 250 = 500
    products = [make_product("A", 250)]
    result = find_combinations(products, 500)
    assert len(result) == 1
    assert len(result[0]) == 2


def test_find_combinations_no_match():
    products = [make_product("A", 300), make_product("B", 200)]
    result = find_combinations(products, 999)
    assert result == []


def test_find_combinations_zero_target():
    products = [make_product("A", 300)]
    assert find_combinations(products, 0) == []


def test_find_combinations_negative_target():
    products = [make_product("A", 300)]
    assert find_combinations(products, -100) == []


def test_find_combinations_max_results():
    # Many possible combinations — should return at most 3
    products = [make_product(str(i), i * 10) for i in range(1, 10)]
    result = find_combinations(products, 30)
    assert len(result) <= 3


# =========================
# find_result_by_method
# =========================

def test_find_result_by_method_found():
    mismatch_results = [
        {"method": "電子マネー", "difference": 210, "mode": "POS_GT_CAT"},
        {"method": "国内QR", "difference": 100, "mode": "CAT_GT_POS"},
    ]
    result = find_result_by_method(mismatch_results, "電子マネー")
    assert result["difference"] == 210
    assert result["mode"] == "POS_GT_CAT"


def test_find_result_by_method_not_found():
    mismatch_results = [
        {"method": "電子マネー", "difference": 210, "mode": "POS_GT_CAT"},
    ]
    result = find_result_by_method(mismatch_results, "国内QR")
    assert result is None


# =========================
# format_combinations
# =========================

def test_format_combinations_groups_duplicate_products():
    # Same product twice should appear as quantity 2
    product = make_product("A", 300)
    combinations = [[product, product]]
    result = format_combinations(combinations)
    assert result[0]["items"][0]["quantity"] == 2
    assert result[0]["total"] == 600


def test_format_combinations_two_different_products():
    a = make_product("A", 300)
    b = make_product("B", 200)
    combinations = [[a, b]]
    result = format_combinations(combinations)
    assert len(result[0]["items"]) == 2
    assert result[0]["total"] == 500


def test_format_combinations_combination_number():
    product = make_product("A", 300)
    combinations = [[product], [product]]
    result = format_combinations(combinations)
    assert result[0]["combination_number"] == 1
    assert result[1]["combination_number"] == 2
