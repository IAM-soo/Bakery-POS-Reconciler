const API_BASE = "http://localhost:8000";

const POS_METHODS = [
  "クレジットカード",
  "交通系IC",
  "JREポイント",
  "国内QR",
  "中国QR",
  "電子マネー",
];

const CAT_EMONEY_METHODS = ["楽天Edy", "iD", "QUICPay", "WAON", "nanaco"];
const CAT_JPQR_METHODS = [
  "d払い",
  "PayPay",
  "au PAY",
  "楽天ペイ",
  "J-Coin Pay",
];
const CAT_CHQR_METHODS = ["Alipay", "WeChatPay"];

const PAYMENT_GROUPS = {
  クレジットカード: ["クレジットカード"],
  交通系IC: ["交通系IC"],
  電子マネー: CAT_EMONEY_METHODS,
  中国QR: CAT_CHQR_METHODS,
  国内QR: CAT_JPQR_METHODS,
  JREポイント: ["JREポイント"],
};

function buildPosInputs() {
  const section = document.getElementById("pos_section");
  for (const method of POS_METHODS) {
    section.innerHTML += `<label>${method} 売上</label><input type="number" id="pos_${method}"><br>`;
  }
}

function buildCatInputs() {
    const section = document.getElementById("cat_section");
    for (const [group, methods] of Object.entries(PAYMENT_GROUPS)) {
        for (const method of methods) {
            section.innerHTML += `<label>${method} 売上</label><input type="number" id="cat_${method}_sales"><br>`;
        }
    }
}

buildPosInputs();
buildCatInputs();
