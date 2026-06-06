POS_METHODS = [
    "クレジットカード",
    "交通系IC",
    "金券",
    "国内QR",
    "中国QR",
    "電子マネー",
]

CAT_EMONEY_METHODS = ["楽天Edy", "iD", "QUICPay", "WAON", "nanaco"]
CAT_JPQR_METHODS = ["d払い", "PayPay", "au PAY", "楽天ペイ", "J-Coin Pay"]
CAT_CHQR_METHODS = ["Alipay", "WeChatPay"]

PAYMENT_GROUPS = {
    "クレジットカード": ["クレジットカード"],
    "交通系IC": ["交通系IC"],
    "電子マネー": CAT_EMONEY_METHODS,
    "中国QR": CAT_CHQR_METHODS,
    "国内QR": CAT_JPQR_METHODS,
    "金券": ["金券"],
}
