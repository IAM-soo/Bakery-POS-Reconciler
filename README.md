# Bakery POS Reconciler (ベーカリー レジ締め支援ツール) 🍞

Bakery POS Reconciler は、パン屋のレジ締め作業における POS 金額と CAT 端末金額の差額確認、および差額修正候補の検索を支援する Web アプリです。

現在は FastAPI + Neon PostgreSQL のバックエンドと、Vercel にデプロイされたバニラ HTML/CSS/JS フロントエンドで動作しています（Streamlit 版は初期プロトタイプとして `web_app.py` に残しています）。

## Live Demo

- FastAPI + Vanilla JS 版（現行）: https://bakery-pos-reconciler.vercel.app/
- Streamlit 版（初期プロトタイプ）: https://bakery-pos-reconciler.streamlit.app/

## 1. 開発の背景 (Motivation)

現在アルバイトをしているパン屋では、POS 側の金額と CAT 端末側の決済金額をレジ締め時に確認する必要があります。

特に電子マネーや QR 決済では、POS 側では「電子マネー」「国内QR」「中国QR」のように分類合計で表示される一方、CAT 端末側では 楽天Edy、iD、QUICPay、PayPay、Alipay などの明細に分かれて表示されます。

そのため、手作業で集計・比較すると時間がかかり、入力ミスや確認漏れが発生しやすくなります。

本アプリは、POS 金額と CAT 端末金額を入力することで、支払い方法ごとの差額を確認し、必要に応じて POS 修正用の商品組み合わせ候補を提示することを目的としています。

## 2. 主な機能 (Features)

- [x] FastAPI バックエンド + Neon PostgreSQL（商品データ管理）
- [x] バニラ HTML/CSS/JS フロントエンド（Vercel にデプロイ、スマートフォンからアクセス可能）
- [x] POS 側の支払い分類金額を入力
- [x] CAT 端末側の決済明細金額を入力
- [x] CAT 明細を POS 分類に集計
- [x] POS 金額と CAT 金額の差額を自動計算
- [x] 差額がある支払い分類を抽出
- [x] 取消金額と差額から修正後の目標金額を計算
- [x] 商品データベースから修正候補の商品組み合わせを検索
- [ ] 差額修正フロー（差額のある支払い方法を選んで修正候補を確認）のフロントエンド実装（進行中）
- [ ] OCR 画像認識による POS / CAT 金額の自動読み取り

## 3. 使い方 (Usage)

1. Web アプリを開く
2. POS 金額を入力する
3. CAT 端末の各決済金額を入力する
4. 差額結果を確認する
5. 差額がある場合、修正する項目を選択する
6. 取消予定の POS 取引金額を入力する
7. 修正後の目標金額と商品組み合わせ候補を確認する

## 4. セットアップ (Local Installation)

### FastAPI 版（現行）

```bash
cd bakery-api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# .env に DATABASE_URL（Neon PostgreSQL の接続文字列）を設定
uvicorn app.main:app --reload
```

ブラウザで `http://localhost:8000/` を開くとフロントエンドが表示され、`http://localhost:8000/docs` で API（Swagger UI）を確認できます。

### Streamlit 版（初期プロトタイプ）

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run web_app.py
```

## 5. テスト (Tests)

```bash
pytest test_reconciler.py
```

コアロジック（`reconciler.py`）に対して 31 件のテストが含まれています。

## 6. プロジェクト構成 (Structure)

```text
Bakery-POS-Reconciler/
├── bakery-api/              # FastAPI バックエンド（現行、Vercel にデプロイ）
│   ├── app/
│   │   ├── main.py          # FastAPI エントリポイント、静的ファイル配信
│   │   ├── routers/         # /products, /reconcile エンドポイント
│   │   ├── services/        # 差額計算・商品組み合わせ検索のロジック
│   │   ├── schemas/         # Pydantic スキーマ
│   │   └── models/          # SQLAlchemy モデル（Neon PostgreSQL）
│   └── frontend/            # バニラ HTML/CSS/JS フロントエンド
│       ├── index.html
│       ├── style.css
│       └── app.js
├── web_app.py                # Streamlit Web UI（初期プロトタイプ）
├── reconciler.py              # Core calculation logic（Streamlit 版）
├── requirements.txt           # Python dependencies（Streamlit 版）
└── data/
    └── menu.json               # Product menu data（Streamlit 版）
```

## 7. 現在のステータス (Project Status)

現在は、FastAPI + Neon PostgreSQL バックエンドと、Vercel にデプロイされたバニラ HTML/CSS/JS フロントエンドが動作しています。Streamlit 版は初期プロトタイプとしてリポジトリに残しています。

完了済み：

- CLI prototype
- Streamlit Web app（初期プロトタイプ、Streamlit Cloud デプロイ済み）
- FastAPI バックエンドへの移行（商品 CRUD、差額計算、商品組み合わせ検索）
- バニラ HTML/CSS/JS フロントエンド（POS/CAT 金額入力、差額結果表示）
- Vercel + Neon PostgreSQL への本番デプロイ

進行中：

- 差額修正フロー（差額のある支払い方法を選択 → 修正候補を表示）のフロントエンド実装

今後の予定：

- スマートフォン UI の改善
- メニュー更新管理の改善
- OCR による POS / CAT 金額の自動読み取り