# ポモドーロタイマー - Phase 0 セットアップ完了

## 📦 プロジェクト構造

```
1.pomodoro/
├── app.py                          # Flask メインアプリケーション
├── requirements.txt                # Python 依存関係
├── package.json                    # Node.js 依存関係
├── pytest.ini                      # pytest 設定
├── jest.config.js                  # Jest 設定
├── jest.setup.js                   # Jest セットアップ
│
├── docs/
│   └── pomodoro.png               # UIモック画像
│
├── templates/
│   └── index.html                 # メイン HTML テンプレート
│
├── static/
│   ├── css/
│   │   └── style.css              # メイン スタイルシート
│   └── js/
│       ├── timer-core.js          # タイマー コア ロジック（テスト対象）
│       ├── storage-api.js         # LocalStorage ラッパー（テスト対象）
│       └── timer.js               # UI 制御層
│
├── tests/
│   ├── test_timer_logic.py        # Python ユニットテスト（Sprint 1予定）
│   ├── test_storage.py            # Python ストレージテスト（Sprint 3予定）
│   ├── test_timer_core.js         # JavaScript ユニットテスト（Sprint 2予定）
│   └── test_storage_api.js        # JavaScript ストレージテスト（Sprint 5予定）
│
├── features.md                     # 機能要件一覧
├── plan.md                         # 段階的実装計画
└── README.md                       # このファイル
```

---

## 🚀 セットアップ手順

### 1. Python 環境構築

```bash
# 1.pomodoro ディレクトリに移動
cd 1.pomodoro

# 仮想環境作成（推奨）
python3 -m venv venv

# 仮想環境有効化
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 依存関係インストール
pip install -r requirements.txt
```

### 2. Node.js 環境構築

```bash
# npm 依存関係をインストール
npm install
```

### 3. Flask アプリケーション起動

```bash
# Python 仮想環境を有効化
source venv/bin/activate  # または venv\Scripts\activate (Windows)

# Flask アプリケーション起動
python app.py

# ブラウザで以下にアクセス
# http://localhost:5000
```

ブラウザに以下が表示されたら成功です：
- タイトル: 「ポモドーロタイマー」
- ステータス: 「作業中」
- タイマー表示: 「25:00」
- ボタン: 「開始」「リセット」
- 統計エリア: 「完了」「集中時間」

---

## 🧪 テスト実行

### Python テスト（pytest）

```bash
# 全テスト実行
pytest tests/ -v

# カバレッジレポート付き実行
pytest tests/ --cov=. --cov-report=html
# HTML レポートを表示: open htmlcov/index.html
```

### JavaScript テスト（Jest）

```bash
# 全テスト実行
npm test

# Watch モード（ファイル変更時に自動実行）
npm run test:watch

# カバレッジレポート付き実行
npm run test:coverage
```

---

## ✅ Sprint 0 デリバリーチェックリスト

- [x] Flask アプリケーション初期化 (`app.py`)
- [x] `requirements.txt` 作成
- [x] 基本 HTML テンプレート (`templates/index.html`)
- [x] CSS スタイル (`static/css/style.css`)
- [x] JavaScript スケルトン:
  - [x] `timer-core.js` - タイマー コア ロジック
  - [x] `storage-api.js` - LocalStorage ラッパー
  - [x] `timer.js` - UI 制御層
- [x] テスト環境セットアップ:
  - [x] `pytest.ini`
  - [x] `jest.config.js`
  - [x] `jest.setup.js`
  - [x] `package.json`
- [x] ディレクトリ構造確立
- [x] UIモック移動 (`docs/pomodoro.png`)

---

## 📝 注意事項

### ブラウザでの確認

現在の実装状況：
- UI が表示される ✓
- スタイルが適用される ✓
- ボタンが配置される ✓
- ただし機能は未実装（Sprint 1-2で実装）

### デバッグ方法

```javascript
// ブラウザコンソール（F12）でグローバルオブジェクトアクセス可能
timerCore.formatTime()      // TimerCore インスタンス
storageAPI.loadStats()      // StorageAPI インスタンス
timerUI.updateDisplay()     // TimerUI インスタンス
```

---

## 🔗 関連ドキュメント

- [architecture.md](../architecture.md) - アーキテクチャ全体設計
- [features.md](features.md) - 機能要件一覧
- [plan.md](plan.md) - 段階的実装計画
- [UIモック](docs/pomodoro.png) - UI仕様書

---

## 🎯 次のステップ

**Sprint 1**: ビジネスロジック MVP
- `timer_logic.py` 実装（PomodoroSession, WorkSessionTracker）
- Python ユニットテスト実装
- テストカバレッジ >90% 達成

詳しくは [plan.md](plan.md) の Sprint 1 セクションをご覧ください。

---

**Sprint 0 完了日**: April 17, 2024
