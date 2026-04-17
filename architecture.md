# ポモドーロタイマーWebアプリ - アーキテクチャ設計書

## 📋 プロジェクト概要

ポモドーロ・テクニックに基づくWebアプリケーション。25分の作業時間と5分の休憩時間を管理するタイマーです。
- **フレームワーク**: Flask + HTML/CSS/JavaScript
- **対象ユーザー**: 生産性向上を目指す個人ユーザー
- **主要機能**: タイマー管理、セッション統計、リアルタイム進捗表示

---

## 🏗️ プロジェクト構造

```
1.pomodoro/
├── app.py                          # Flaskアプリケーションメインファイル
├── timer_logic.py                  # タイマービジネスロジック（テスト対象）
├── storage.py                      # ストレージ層抽象化
│
├── static/
│   ├── css/
│   │   └── style.css               # グローバルスタイル
│   └── js/
│       ├── timer-core.js           # 純粋なタイマー計算ロジック
│       ├── storage-api.js          # LocalStorageラッパー
│       └── timer.js                # UI制御層（DOM操作）
│
├── templates/
│   └── index.html                  # メインHTMLテンプレート
│
├── tests/
│   ├── test_timer_logic.py         # Pythonロジックテスト
│   ├── test_storage.py             # ストレージ層テスト
│   └── test_timer_core.js          # JavaScriptコアロジックテスト
│
└── requirements.txt                # Pythonパッケージ依存関係
```

---

## 🔧 アーキテクチャの3層構成

### 層の役割分担

```
┌─────────────────────────────────────────────────┐
│          UI層（DOM操作）                         │
│     timer.js / index.html / style.css            │
│  ・ユーザーイベント処理                           │
│  ・UI更新（リアルタイム表示）                      │
│  ・SVG円形プログレス描画                          │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────┴──────────────────────────────┐
│      ビジネスロジック層（計算・判定）            │
│  timer-core.js / timer_logic.py                 │
│  ・タイマーのカウント管理                        │
│  ・セッション完了判定                           │
│  ・時間計算（副作用なし）                        │
│  👉 **テスト対象**: ユニットテスト              │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────┴──────────────────────────────┐
│        データ永続化層（ストレージ）              │
│  storage-api.js / storage.py                    │
│  ・LocalStorage（フロントエンド）               │
│  ・テーブル/ファイル（バックエンド）             │
│  ・インターフェース抽象化                        │
└─────────────────────────────────────────────────┘
```

---

## 💻 Python側の設計

### 1. **app.py** - Flask アプリケーション

```python
# 責務：
# - HTTPルーティング
# - テンプレート返却
# - APIエンドポイント提供

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """本日の統計情報を返す"""
    # storage.py を通じで取得
    return jsonify(storage.load_stats())

@app.route('/api/sessions', methods=['POST'])
def save_session():
    """完了したセッションを保存"""
    session_data = request.json
    storage.save_session(session_data)
    return jsonify({'status': 'ok'})
```

### 2. **timer_logic.py** - ビジネスロジック（テスト対象）

```python
class PomodoroSession:
    """ポモドーロセッションの状態と計算を管理"""
    
    def __init__(self, work_minutes=25, break_minutes=5):
        self.work_seconds = work_minutes * 60
        self.break_seconds = break_minutes * 60
        self.elapsed_seconds = 0
    
    # ✨ 純粋関数：副作用なし
    def get_remaining(self):
        """残り時間を秒で返す"""
        return max(0, self.work_seconds - self.elapsed_seconds)
    
    def is_complete(self):
        """セッションが完了したかを判定"""
        return self.elapsed_seconds >= self.work_seconds
    
    def get_progress_ratio(self):
        """進捗を0〜1の比率で返す"""
        return self.elapsed_seconds / self.work_seconds

class WorkSessionTracker:
    """本日のセッション統計を追跡"""
    
    def __init__(self):
        self.sessions_completed = 0
        self.total_minutes = 0
    
    def add_completed_session(self, minutes):
        """セッション完了を記録"""
        self.sessions_completed += 1
        self.total_minutes += minutes
    
    def get_stats_dict(self):
        """統計情報を辞書で返す"""
        return {
            'completed': self.sessions_completed,
            'total_minutes': self.total_minutes
        }
```

**テスト例：**
```python
# tests/test_timer_logic.py
import pytest
from timer_logic import PomodoroSession, WorkSessionTracker

def test_session_complete_after_work_time():
    session = PomodoroSession(work_minutes=1)
    session.elapsed_seconds = 60
    assert session.is_complete() is True

def test_progress_ratio():
    session = PomodoroSession(work_minutes=25)
    session.elapsed_seconds = 750  # 12分30秒
    assert session.get_progress_ratio() == 0.5

def test_session_tracker():
    tracker = WorkSessionTracker()
    tracker.add_completed_session(25)
    tracker.add_completed_session(25)
    assert tracker.sessions_completed == 2
    assert tracker.total_minutes == 50
```

### 3. **storage.py** - ストレージ抽象化（インターフェース設計）

```python
from abc import ABC, abstractmethod

class StorageInterface(ABC):
    """ストレージの統一インターフェース"""
    
    @abstractmethod
    def save_session(self, session_data): pass
    
    @abstractmethod
    def load_stats(self): pass

class FileStorage(StorageInterface):
    """ファイルベースの実装"""
    def save_session(self, session_data):
        # JSON形式でファイルに保存
        pass
    
    def load_stats(self):
        # ファイルから統計情報を読み込む
        pass

class MockStorage(StorageInterface):
    """テスト用モック実装"""
    def __init__(self):
        self.data = {}
    
    def save_session(self, session_data):
        self.data['last_session'] = session_data
    
    def load_stats(self):
        return self.data.get('stats', {})
```

---

## 🎨 JavaScript側の設計

### 1. **timer-core.js** - 純粋なタイマーロジック

```javascript
class TimerCore {
  /**
   * ビジネスロジック層：計算のみ、副作用なし
   *用途：テスト対象、別プロセスでも使用可能
   */
  
  constructor(workMinutes = 25, breakMinutes = 5) {
    this.workSeconds = workMinutes * 60;
    this.breakSeconds = breakMinutes * 60;
    this.elapsedSeconds = 0;
  }

  // 計算メソッド（副作用なし）
  getRemaining() {
    return Math.max(0, this.workSeconds - this.elapsedSeconds);
  }

  getProgressRatio() {
    return Math.min(1, this.elapsedSeconds / this.workSeconds);
  }

  isComplete() {
    return this.elapsedSeconds >= this.workSeconds;
  }

  tick() {
    this.elapsedSeconds++;
  }

  reset() {
    this.elapsedSeconds = 0;
  }

  formatTime() {
    const seconds = this.getRemaining();
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
  }
}
```

**テスト例（Jest）：**
```javascript
// tests/timer-core.test.js
describe('TimerCore', () => {
  let timer;

  beforeEach(() => {
    timer = new TimerCore(1); // 1分でテスト
  });

  test('tick should increment elapsed time', () => {
    timer.tick();
    expect(timer.elapsedSeconds).toBe(1);
  });

  test('isComplete should return true after work duration', () => {
    timer.elapsedSeconds = 60;
    expect(timer.isComplete()).toBe(true);
  });

  test('formatTime should display MM:SS format', () => {
    timer.elapsedSeconds = 30;
    expect(timer.formatTime()).toBe('00:30');
  });

  test('getProgressRatio should be 0-1', () => {
    timer.elapsedSeconds = 30;
    expect(timer.getProgressRatio()).toBe(0.5);
  });
});
```

### 2. **storage-api.js** - ストレージラッパー（依存性注入）

```javascript
class StorageAPI {
  /**
   * ストレージ操作の抽象化レイヤー
   * 実装はコンストラクタで注入可能
   */
  
  constructor(storageImpl = null) {
    this.storage = storageImpl || window.localStorage;
  }

  saveSession(sessionData) {
    this.storage.setItem('pomodoro_session', JSON.stringify(sessionData));
  }

  loadStats() {
    const data = this.storage.getItem('pomodoro_stats');
    return data ? JSON.parse(data) : { completed: 0, totalMinutes: 0 };
  }

  updateStats(increment) {
    const current = this.loadStats();
    current.completed += 1;
    current.totalMinutes += increment;
    this.storage.setItem('pomodoro_stats', JSON.stringify(current));
  }

  clearAll() {
    this.storage.removeItem('pomodoro_session');
    this.storage.removeItem('pomodoro_stats');
  }
}

// テスト用モック
class MockStorage {
  constructor() {
    this.data = {};
  }
  setItem(key, value) { this.data[key] = value; }
  getItem(key) { return this.data[key] || null; }
  removeItem(key) { delete this.data[key]; }
}
```

### 3. **timer.js** - UI制御層（DOM依存）

```javascript
class TimerUI {
  /**
   * UI層：DOM操作と表示ロジック
   * TimerCore と StorageAPI に依存
   */
  
  constructor(timerCore, storageAPI, domElements) {
    this.timer = timerCore;
    this.storage = storageAPI;
    this.dom = domElements; // { timeDisplay, startBtn, resetBtn, circle, ... }
    this.intervalId = null;
  }

  updateDisplay() {
    // 時間表示の更新
    this.dom.timeDisplay.textContent = this.timer.formatTime();
    
    // 円形プログレスの更新
    this.updateCircleProgress(this.timer.getProgressRatio());
  }

  updateCircleProgress(ratio) {
    const circumference = 2 * Math.PI * 150; // 半径150
    const offset = circumference * (1 - ratio);
    this.dom.circleArc.style.strokeDashoffset = offset;
  }

  onStartClick() {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
      this.dom.startBtn.textContent = '開始';
    } else {
      this.dom.startBtn.textContent = '一時停止';
      this.intervalId = setInterval(() => {
        this.timer.tick();
        this.updateDisplay();

        if (this.timer.isComplete()) {
          clearInterval(this.intervalId);
          this.intervalId = null;
          this.onSessionComplete();
        }
      }, 1000);
    }
  }

  onResetClick() {
    clearInterval(this.intervalId);
    this.intervalId = null;
    this.timer.reset();
    this.updateDisplay();
    this.dom.startBtn.textContent = '開始';
  }

  onSessionComplete() {
    this.storage.updateStats(25);
    this.showNotification('セッション完了！25分間、お疲れさまでした。');
    // UI更新...
  }
}
```

---

## 📊 データフロー図

```
【ユーザー操作】
    │
    ├─→「開始」ボタン
    │        │
    │        ↓
    │   timer.js (UI層)
    │        │
    │        ├─→ timer.tick()  [timer-core.js]
    │        │
    │        ├─→ getRemaining()  [計算、副作用なし]
    │        │
    │        ├─→ updateDisplay()  [DOM更新]
    │        │
    │        └─→ 画面リアルタイム表示
    │
    ├─→「リセット」ボタン
    │        │
    │        ↓
    │   timer.reset()  [timer-core.js]
    │        │
    │        └─→ 画面リセット
    │
    └─→セッション完了時
            │
            ↓
       storage.updateStats()  [storage-api.js]
            │
            ↓
       LocalStorage に統計保存
            │
            ↓
       ページロード時に復元
```

---

## 🧪 テスト戦略

### テスト層別ガイドライン

| レイヤー | テスト種別 | 難度 | ツール | カバレッジ目標 |
|---------|----------|------|--------|--------------|
| **ビジネスロジック** | ユニットテスト | 簡単 ✅ | pytest / Jest | **>90%** |
| **ストレージ層** | ユニット + Mock | 中程度 | pytest / Jest | **>85%** |
| **UI層** | 統合/E2E | 難しい | Selenium / Playwright | **>60%** |
| **Flask API** | ユニット + Mock | 中程度 | pytest | **>80%** |

### 実行コマンド

```bash
# Python テスト
pytest tests/ -v --cov=. --cov-report=html

# JavaScript テスト
npm test -- --coverage
```

---

## 🎯 主な設計パターン

### 1. **依存性注入（Dependency Injection）**
- StorageAPI、TimerUIはコンストラクタで実装を受け取る
- テスト時にモックを注入可能

```javascript
// 本番
const storage = new StorageAPI(window.localStorage);
const ui = new TimerUI(timer, storage, domElements);

// テスト
const mockStorage = new MockStorage();
const ui = new TimerUI(timer, mockStorage, domElements);
```

### 2. **責務の分離（Separation of Concerns）**
- **TimerCore**: 計算のみ
- **StorageAPI**: I/O操作のみ
- **TimerUI**: 表示処理のみ

### 3. **純粋関数の活用**
- ビジネスロジックは副作用なし
- 同じ入力に対して常に同じ出力
- テスト容易、並列実行可能

### 4. **インターフェース抽象化**
- StorageInterface が実装を隠蔽
- 将来の変更（DB連携など）に強い

---

## 🚀 実装ロードマップ

### Phase 1: 基盤構築
- [ ] Flask アプリケーション基本設定
- [ ] HTML/CSS テンプレート
- [ ] プロジェクト構造作成

### Phase 2: コアロジック実装
- [ ] `timer-core.js` 実装
- [ ] `timer_logic.py` 実装
- [ ] ユニットテスト作成

### Phase 3: ストレージ層
- [ ] `storage-api.js` 実装
- [ ] `storage.py` 実装
- [ ] MockStorage を使用したテスト

### Phase 4: UI統合
- [ ] `timer.js` 実装
- [ ] DOM操作とイベント処理
- [ ] SVG円形プログレス表示

### Phase 5: テスト完全化
- [ ] カバレッジ>80%達成
- [ ] E2E テスト追加
- [ ] バグ修正

---

## ✨ このアーキテクチャのメリット

| メリット | 説明 |
|---------|------|
| **テスト性** | ビジネスロジックが純粋で独立、テスト容易 |
| **保守性** | 各層が責務を明確に分け、変更の影響が局所的 |
| **拡張性** | インターフェース抽象化により新機能追加が容易 |
| **再利用性** | TimerCore は別プロジェクトでも利用可能 |
| **デバッグ性** | 層別に動作確認でき、問題箇所を特定しやすい |
| **パフォーマンス** | フロントエンド中心でサーバー負荷が少ない |

---

## 📝 補足

### 今後の拡張案
- **クラウド同期**: セッション履歴をサーバー保存
- **通知機能**: セッション完了時のポップアップ/音声
- **複数タイマー**: 異なるセッション並行管理
- **統計ダッシュボード**: 週間・月間グラフ表示
- **REST API**: モバイルアプリから利用可能にする

### 参考資料
- Pomodoro Technique: https://en.wikipedia.org/wiki/Pomodoro_Technique
- SOLID原則: 単一責任の原則、インターフェース分離原則
- テスト駆動開発(TDD)
