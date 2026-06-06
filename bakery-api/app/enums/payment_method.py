from enum import Enum


class PaymentMethod(str, Enum):
    CASH = "cash"
    CREDIT_CARD = "credit_card"
    IC_CARD = "ic_card"
    QR_CODE = "qr_code"
    GIFT_VOUCHER = "gift_voucher"
    OTHER = "other"


class ReconciliationMode(str, Enum):
    POS_GT_CAT = "POS_GT_CAT"
    CAT_GT_POS = "CAT_GT_POS"
    MATCHED = "MATCHED"
