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

function toggleCancelInput(method) {
  const row = document.getElementById(`cat_${method}_cancel_row`);
  row.classList.toggle("hidden");
}

function buildCatInputs() {
  const section = document.getElementById("cat_section");
  for (const [group, methods] of Object.entries(PAYMENT_GROUPS)) {
    for (const method of methods) {
      section.innerHTML += `<label>${method} 売上</label><br>
          <input type="number" id="cat_${method}_sales"><br>
          <input type="checkbox" id="cat_${method}_checkbox" onchange="toggleCancelInput('${method}')"> 取消あり<br>
          <div id="cat_${method}_cancel_row" class="hidden">
            <label>${method} 取消</label>
            <input type="number" id="cat_${method}_cancel">
          </div><br>`;
    }
  }
}

function getPosAmounts() {
  const pos_amounts = {};
  for (const pos_method of POS_METHODS) {
    pos_amounts[pos_method] = Number(
      document.getElementById(`pos_${pos_method}`).value,
    );
  }
  return pos_amounts;
}

function getCatAmountsTemp() {
  const cat_amounts_temp = {};
  for (const [group, cat_methods] of Object.entries(PAYMENT_GROUPS)) {
    for (const cat_method of cat_methods) {
      cat_amounts_temp[`${cat_method}_sales`] = Number(
        document.getElementById(`cat_${cat_method}_sales`).value,
      );
      cat_amounts_temp[`${cat_method}_cancel`] = Number(
        document.getElementById(`cat_${cat_method}_cancel`).value,
      );
    }
  }
  return cat_amounts_temp;
}

async function handleReconcile() {
  const requestBody = {
    pos_amounts: getPosAmounts(),
    cat_amounts_temp: getCatAmountsTemp(),
  };
  const response = await fetch(API_BASE + "/reconcile/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(requestBody),
  });
  const result = await response.json();
  console.log(result);
  showReconcileResults(result);
}

function handleReset(){
  for (const pos_method of POS_METHODS) {
    document.getElementById(`pos_${pos_method}`).value = "";
  }
  for (const [group, cat_methods] of Object.entries(PAYMENT_GROUPS)) {
    for (const cat_method of cat_methods) {
      document.getElementById(`cat_${cat_method}_sales`).value = "";
      document.getElementById(`cat_${cat_method}_cancel`).value = "";
      document.getElementById(`cat_${cat_method}_checkbox`).checked = false;

      document.getElementById(`cat_${cat_method}_cancel_row`).classList.add("hidden");
      
    }
  }
  document.getElementById("result_section").classList.add("hidden");
}


function showReconcileResults(result) {
  const resultList = document.getElementById("result_list");
  resultList.innerHTML = "";

  for (const item of result) {
    let className;
    if (item["mode"] == "MATCH") {
      className = "status-ok";
    } else {
      className = "status-mismatch";
    }
    resultList.innerHTML += `<p class="${className}">${item["method"]}: POS ${item["pos_amount"]} / CAT ${item["cat_amount"]}（差額 ${item["difference"]}）</p>`;
  }

  document.getElementById("result_section").classList.remove("hidden");
}
buildPosInputs();
buildCatInputs();
