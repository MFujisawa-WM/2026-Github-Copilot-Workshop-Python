# ポモドーロタイマー - 段階的実装計画

## 📋 実装の原則

```
1. テスト駆動開発（TDD）: テスト→実装
2. 依存性逆転: ビジネスロジック→ストレージ→UI
3. MVP段階: 各スプリント終了時に動作デモ可能
4. 疎結合: 各層が独立して動作・テスト可能
```

---

## 📊 実装スプリント概要

```
【フェーズ1: 基盤構築】
├─ Sprint 0: 環境・プロジェクト構造
├─ Sprint 1: ビジネスロジック MVP
└─ Sprint 2: バックエンド基盤

【フェーズ2: UI 統合】
├─ Sprint 3: フロントエンド基盤
├─ Sprint 4: タイマー核制御
├─ Sprint 5: 円形プログレス
└─ Sprint 6: ストレージ連携

【フェーズ3: 完成・最適化】
├─ Sprint 7: UX 機能（通知等）
├─ Sprint 8: テスト完全化
└─ Sprint 9: デプロイ準備
```

---

## 🚀 詳細実装計画

### **Sprint 0: 環境・プロジェクト構造確立** 📦
**所要時間**: 30 分  
**目標**: プロジェクトの骨組み完成

#### 実装内容

| タスク | 内容 | ファイル |
|--------|------|--------|
| 0-1 | Flask アプリケーション初期化 | `app.py` |
| 0-2 | requirements.txt 作成 | `requirements.txt` |
| 0-3 | 基本 HTML テンプレート | `templates/index.html` |
| 0-4 | 空の CSS | `static/css/style.css` |
| 0-5 | 空の JS（スケルトン） | `static/js/timer.js`, `timer-core.js`, `storage-api.js` |
| 0-6 | テスト環境セットアップ | pytest 設定、Jest 設定 |

#### デリバリー
```bash
# 起動確認
python app.py
# http://localhost:5000 でページが表示される（スタイルなし）
```

#### 成果物 Checklist
- [ ] Flaskアプリが起動、ブラウザからアクセス可能
- [ ] ファイル構造確立

---

### **Sprint 1: ビジネスロジック MVP** 🧮
**所要時間**: 2-3 時間  
**目標**: タイマー計算ロジックが完全にテストされた状態

#### 実装内容

| # | タスク | 詳細 | テスト対象 |
|---|--------|------|----------|
| 1-1 | `timer_logic.py` - PomodoroSession | 時間計算ロジック | `test_timer_logic.py` |
| 1-2 | `timer_logic.py` - WorkSessionTracker | 統計追跡ロジック | `test_timer_logic.py` |
| 1-3 | テスト実装 | 全テストケース | pytest |
| 1-4 | テストカバレッジ検証 | >90% 達成 | coverage |

#### 実装の詳細

```python
# timer_logic.py: 実装する関数
class PomodoroSession:
    __init__(work_minutes=25, break_minutes=5)
    tick()                          # 1秒加算
    get_remaining()                 # 残り時間
    is_complete()                   # 完了判定
    get_progress_ratio()            # 進捗率（0-1）
    reset()                         # リセット
    format_time(seconds)            # MM:SS形式

class WorkSessionTracker:
    add_completed_session(minutes)  # セッション記録
    get_stats_dict()                # 統計辞書
    reset_if_new_day()              # 日付判定リセット
```

#### テストケース例（pytest）
```python
def test_session_tick():
    session = PomodoroSession(1)
    session.tick()
    assert session.elapsedSeconds == 1

def test_session_complete():
    session = PomodoroSession(1)
    session.elapsedSeconds = 60
    assert session.is_complete() is True

def test_progress_ratio():
    session = PomodoroSession(25)
    session.elapsedSeconds = 750  # 12分30秒
    assert session.get_progress_ratio() == 0.5

def test_workflow_tracker():
    tracker = WorkSessionTracker()
    tracker.add_completed_session(25)
    assert tracker.get_stats_dict()['completed'] == 1
```

#### デリバリー
```bash
# テスト実行
pytest tests/test_timer_logic.py -v --cov

# 出力例
test_session_tick PASSED
test_session_complete PASSED
test_progress_ratio PASSED
test_workflow_tracker PASSED
======================== 4 passed ========================
```

#### 成果物 Checklist
- [ ] `timer_logic.py` 完成・テスト>90%
- [ ] `test_timer_logic.py` 作成・全パス

---

### **Sprint 2: JavaScript ビジネスロジック** 🔧
**所要時間**: 1.5-2 時間  
**目標**: JavaScript版 TimerCore がテストされた状態

#### 実装内容

| # | タスク | 詳細 | テスト対象 |
|---|--------|------|----------|
| 2-1 | `timer-core.js` - TimerCore クラス | JS版タイマー | `test_timer_core.js` |
| 2-2 | テスト実装（Jest） | 全テストケース | Jest |
| 2-3 | テストカバレッジ検証 | >90% 達成 | coverage |

#### 実装の詳細

```javascript
// timer-core.js
class TimerCore {
  constructor(workMinutes = 25, breakMinutes = 5) {
    this.workSeconds = workMinutes * 60;
    this.breakSeconds = breakMinutes * 60;
    this.elapsedSeconds = 0;
  }

  tick() { this.elapsedSeconds++; }
  getRemaining() { return Math.max(0, this.workSeconds - this.elapsedSeconds); }
  isComplete() { return this.elapsedSeconds >= this.workSeconds; }
  getProgressRatio() { return this.elapsedSeconds / this.workSeconds; }
  reset() { this.elapsedSeconds = 0; }
  formatTime() { /* MM:SS 形式 */ }
}
```

#### テストケース例（Jest）
```javascript
describe('TimerCore', () => {
  test('tick increments elapsed seconds', () => {
    const timer = new TimerCore(1);
    timer.tick();
    expect(timer.elapsedSeconds).toBe(1);
  });

  test('formatTime returns MM:SS', () => {
    const timer = new TimerCore(25);
    timer.elapsedSeconds = 600 // 10分
    expect(timer.formatTime()).toBe('15:00');
  });
});
```

#### デリバリー
```bash
npm test -- timer-core.test.js

# 出力例
PASS tests/timer-core.test.js
  TimerCore
    ✓ tick increments elapsed seconds
    ✓ formatTime returns MM:SS
  ======================== 2 passed ========================
```

#### 成果物 Checklist
- [ ] `timer-core.js` 完成・テスト>90%
- [ ] `test_timer_core.js` 作成・全パス

---

### **Sprint 3: Flask バックエンド基盤** 🔌
**所要時間**: 1-1.5 時間  
**目標**: Flask API が動作、テストされた状態

#### 実装内容

| # | タスク | 詳細 | エンドポイント |
|---|--------|------|---------------|
| 3-1 | Flask アプリ骨組み | ルーティング定義 | GET /, POST /api/sessions |
| 3-2 | ダミー API 実装 | JSON 返却 | GET /api/stats/today |
| 3-3 | 静的ファイル配信 | CSS/JS | `/static/` |
| 3-4 | テスト実装 | API エンドポイント | `test_api.py` |

#### 実装の詳細

```python
# app.py
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stats/today')
def get_stats():
    """本日の統計"""
    return jsonify({
        'completed': 0,
        'totalMinutes': 0
    })

@app.route('/api/sessions', methods=['POST'])
def save_session():
    """セッション保存"""
    data = request.json
    return jsonify({'status': 'success', 'id': 1})

if __name__ == '__main__':
    app.run(debug=True)
```

#### テストケース例（pytest）
```python
def test_get_index():
    response = client.get('/')
    assert response.status_code == 200

def test_get_stats():
    response = client.get('/api/stats/today')
    assert response.json['completed'] == 0
```

#### デリバリー
```bash
python app.py
# http://localhost:5000 にアクセス可能
# /api/stats/today で JSON が返却される
```

#### 成果物 Checklist
- [ ] Flask API 基本実装完成
- [ ] `test_api.py` 作成・テスト実行確認

---

### **Sprint 4: HTML/CSS 基本テンプレート** 🎨
**所要時間**: 1-1.5 時間  
**目標**: UIモック通りのレイアウト完成（機能なし）

#### 実装内容

| # | タスク | 詳細 | ファイル |
|---|--------|------|--------|
| 4-1 | HTML 構造 | タイマー表示、ボタン、統計エリア | `templates/index.html` |
| 4-2 | CSS レイアウト | グリッド、フレックス、レスポンシブ | `static/css/style.css` |
| 4-3 | SVG 円形基盤 | SVG 構造（色なし） | `templates/index.html` |
| 4-4 | フォント・配色 | ブルー/パープル配色 | CSS |

#### HTML 骨組み

```html
<!-- templates/index.html -->
<div class="container">
  <div class="card">
    <h1>ポモドーロタイマー</h1>
    
    <div class="status">作業中</div>
    
    <div class="timer-display">
      <svg class="progress-circle">
        <!-- 円形プログレス SVG -->
      </svg>
      <div class="time">25:00</div>
    </div>
    
    <div class="controls">
      <button class="btn-start">開始</button>
      <button class="btn-reset">リセット</button>
    </div>
    
    <div class="stats">
      <div class="stat-item">
        <span class="stat-label">完了</span>
        <span class="stat-value">4</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">集中時間</span>
        <span class="stat-value">1時間40分</span>
      </div>
    </div>
  </div>
</div>
```

#### CSS ポイント

```css
/* スタイリング指針 */
- Card: 中央配置、シャドウ
- Colors: メイン青（#4F46E5）、サブパープル（#7C3AED）
- Typography: 日本語フォント（Segoe UI）
- Responsive: モバイル対応（320px〜）
- プログレス円: SVG ベース（実装は Sprint 5）
```

#### デリバリー
```
ブラウザで以下が確認できる：
✓ UIモック通りのレイアウト
✓ 「25:00」テキスト表示
✓ 開始・リセットボタン配置
✓ 統計エリアの配置
```

#### 成果物 Checklist
- [ ] `templates/index.html` 完成
- [ ] `static/css/style.css` 完成
- [ ] ブラウザで視認確認

---

### **Sprint 5: タイマー表示・制御の実装** ⏱️
**所要時間**: 2-3 時間  
**目標**: タイマーが動作する基本フロー完成

#### 実装内容

| # | タスク | 詳細 | 関連機能ID |
|---|--------|------|----------|
| 5-1 | UI 初期化 | DOM 要素取得、イベントリスナー | F-1.1〜1.4 |
| 5-2 | `storage-api.js` 実装 | LocalStorage ラッパー | S-2.1〜2.5 |
| 5-3 | `timer.js` 実装（Stage 1） | UI 更新ロジック | F-1.1, F-1.2, F-1.3 |
| 5-4 | タイマー制御フロー | 開始→更新→停止 | F-1.2, F-1.4 |
| 5-5 | テスト実装 | StorageAPI, UI 統合 | Jest |

#### 実装の詳細

```javascript
// storage-api.js
class StorageAPI {
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

  updateStats(minutes) {
    const current = this.loadStats();
    current.completed += 1;
    current.totalMinutes += minutes;
    this.storage.setItem('pomodoro_stats', JSON.stringify(current));
  }
}

// timer.js - UI層
class TimerUI {
  constructor(timerCore, storageAPI) {
    this.timer = timerCore;
    this.storage = storageAPI;
    this.dom = {
      timeDisplay: document.querySelector('.time'),
      startBtn: document.querySelector('.btn-start'),
      resetBtn: document.querySelector('.btn-reset'),
      status: document.querySelector('.status')
    };
    this.intervalId = null;
    this.setupListeners();
  }

  setupListeners() {
    this.dom.startBtn.addEventListener('click', () => this.onStartClick());
    this.dom.resetBtn.addEventListener('click', () => this.onResetClick());
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

  updateDisplay() {
    this.dom.timeDisplay.textContent = this.timer.formatTime(this.timer.getRemaining());
  }

  onSessionComplete() {
    this.storage.updateStats(25);
    alert('セッション完了！');
    this.timer.reset();
    this.updateDisplay();
  }
}
```

#### 初期化コード

```javascript
// ページロード時の初期化
document.addEventListener('DOMContentLoaded', () => {
  const timerCore = new TimerCore(25, 5);
  const storageAPI = new StorageAPI();
  const timerUI = new TimerUI(timerCore, storageAPI);
  
  // タイマー表示初期化
  timerUI.updateDisplay();
});
```

#### デリバリー
```
ブラウザで以下が動作：
✓ 「開始」ボタンをクリック → タイマーカウント開始
✓ リアルタイムで時間が減少（25:00 → 24:59 → ...）
✓ 「一時停止」ボタンで停止
✓ 「リセット」で 25:00 に戻る
✓ 25分経過後、自動停止・通知
```

#### 成果物 Checklist
- [ ] `storage-api.js` 完成・テスト
- [ ] `timer.js` (Stage 1) 完成
- [ ] ブラウザで動作確認

---

### **Sprint 6: 円形プログレス実装** 🔵
**所要時間**: 2-2.5 時間  
**目標**: SVG 円形プログレスがリアルタイム更新

#### 実装内容

| # | タスク | 詳細 | 関連機能ID |
|---|--------|------|----------|
| 6-1 | SVG 構造改善 | 背景円 + プログレス円 | F-3.1 |
| 6-2 | プログレス計算 | `getProgressRatio()` を活用 | F-3.1, F-3.2 |
| 6-3 | SVG アニメーション | stroke-dashoffset 更新 | F-3.2 |
| 6-4 | 色グラデーション設定 | 青→オレンジ（オプション） | F-3.3 |
| 6-5 | レスポンシブ対応 | ViewBox スケーリング | U-2.1 |

#### SVG 実装例

```html
<!-- index.html -->
<svg class="progress-circle" viewBox="0 0 350 350">
  <!-- 背景円（グレー） -->
  <circle cx="175" cy="175" r="150" class="progress-bg" />
  
  <!-- プログレス円（青） -->
  <circle cx="175" cy="175" r="150" class="progress-arc" />
</svg>
```

```css
/* CSS */
.progress-circle {
  width: 300px;
  height: 300px;
  transform: rotate(-90deg);
  margin: 0 auto;
}

.progress-bg {
  fill: none;
  stroke: #e5e7eb;
  stroke-width: 30;
}

.progress-arc {
  fill: none;
  stroke: #4f46e5;
  stroke-width: 30;
  stroke-linecap: round;
  stroke-dasharray: 942; /* 円周 */
  stroke-dashoffset: 942; /* 初期値（0%） */
  transition: stroke-dashoffset 0.5s ease;
}
```

```javascript
// timer.js に追加
updateCircleProgress() {
  const ratio = this.timer.getProgressRatio();
  const circumference = 2 * Math.PI * 150; // 半径150
  const offset = circumference * (1 - ratio);
  document.querySelector('.progress-arc').style.strokeDashoffset = offset;
}

// updateDisplay() 内で呼び出し
updateDisplay() {
  this.dom.timeDisplay.textContent = this.timer.formatTime(this.timer.getRemaining());
  this.updateCircleProgress(); // ← 追加
}
```

#### デリバリー
```
ブラウザで以下が確認：
✓ SVG 円形が表示
✓ 開始ボタンで進捗がリアルタイム更新
✓ グレー背景 + 青いアーク
✓ 進捗に応じて円が埋まる
```

#### 成果物 Checklist
- [ ] SVG 円形プログレス完成
- [ ] `timer.js` (Stage 2) 更新
- [ ] ブラウザで動作確認

---

### **Sprint 7: LocalStorage 統計連携** 💾
**所要時間**: 1.5-2 時間  
**目標**: セッション完了後、統計がブラウザに保存・復元

#### 実装内容

| # | タスク | 詳細 | 関連機能ID |
|---|--------|------|----------|
| 7-1 | 統計表示のDOM 更新 | 完了数・累計時間の表示 | F-4.1 |
| 7-2 | LocalStorage への保存 | セッション完了時 | F-4.1, F-4.3 |
| 7-3 | ページロード時の復元 | 統計の読み込み | F-4.2, F-4.4 |
| 7-4 | 日付判定ロジック | 日をまたいだらリセット | F-4.4 |
| 7-5 | テスト実装 | StorageAPI テスト | Jest |

#### 実装の詳細

```javascript
// timer.js に追加
class TimerUI {
  constructor(timerCore, storageAPI) {
    // ... 既存コード ...
    this.dom.completeCount = document.querySelector('.stat-complete');
    this.dom.totalMinutes = document.querySelector('.stat-minutes');
    this.loadStatsDisplay();
  }

  loadStatsDisplay() {
    const stats = this.storage.loadStats();
    this.dom.completeCount.textContent = stats.completed;
    this.dom.totalMinutes.textContent = this.formatMinutesToHM(stats.totalMinutes);
  }

  formatMinutesToHM(minutes) {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours}時間${mins}分`;
  }

  onSessionComplete() {
    this.storage.updateStats(25); // ← LocalStorage 更新
    alert('セッション完了！');
    this.loadStatsDisplay(); // ← 表示更新
    this.timer.reset();
    this.updateDisplay();
  }
}
```

```javascript
// storage-api.js に機能追加
class StorageAPI {
  loadStats() {
    const today = new Date().toISOString().split('T')[0];
    const data = this.storage.getItem('pomodoro_stats');
    
    if (!data) {
      return { completed: 0, totalMinutes: 0, date: today };
    }
    
    const stats = JSON.parse(data);
    
    // 日付が変わっていたらリセット
    if (stats.date !== today) {
      this.storage.removeItem('pomodoro_stats');
      return { completed: 0, totalMinutes: 0, date: today };
    }
    
    return stats;
  }

  updateStats(minutes) {
    const today = new Date().toISOString().split('T')[0];
    const current = this.loadStats();
    current.completed += 1;
    current.totalMinutes += minutes;
    current.date = today;
    this.storage.setItem('pomodoro_stats', JSON.stringify(current));
  }
}
```

#### HTML 更新

```html
<div class="stats">
  <div class="stat-item">
    <span class="stat-label">完了</span>
    <span class="stat-complete">0</span>
  </div>
  <div class="stat-item">
    <span class="stat-label">集中時間</span>
    <span class="stat-minutes">0時間0分</span>
  </div>
</div>
```

#### デリバリー
```
ブラウザで以下が動作：
✓ セッション完了時に統計が更新
✓ 統計が LocalStorage に保存
✓ ページリロード後も統計が表示
✓ 翌日になるとリセット
✓ 複数セッション完了で累積
```

#### 成果物 Checklist
- [ ] `storage-api.js` 日付判定機能追加
- [ ] `timer.js` 統計表示機能追加
- [ ] ブラウザ DevTools で LocalStorage 確認可能
- [ ] テスト実装・確認

---

### **Sprint 8: ユーザーフィードバック機能** 🔔
**所要時間**: 1.5-2 時間  
**目標**: セッション完了時の通知・フィードバック実装

#### 実装内容

| # | タスク | 詳細 | 関連機能ID |
|---|--------|------|----------|
| 8-1 | トースト通知 | セッション完了時表示 | F-5.1 |
| 8-2 | 完了音声 | ビープ音再生 | F-5.2 |
| 8-3 | タイトルバー更新 | `document.title` 更新 | F-5.4 |
| 8-4 | ボタン UI 改善 | ホバー・活性状態 | F-2.3 |
| 8-5 | エラーハンドリング | try-catch, ユーザー通知 | F-5.5 |

#### 実装例

```javascript
// timer.js に追加
onSessionComplete() {
  try {
    this.storage.updateStats(25);
    this.playCompleteSound();
    this.showToastNotification('セッション完了！お疲れさまでした。');
    this.loadStatsDisplay();
    this.timer.reset();
    this.updateDisplay();
  } catch (error) {
    console.error('セッション完了処理エラー:', error);
    this.showErrorNotification('エラーが発生しました');
  }
}

showToastNotification(message) {
  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.textContent = message;
  document.body.appendChild(toast);
  
  // 3秒後に削除
  setTimeout(() => toast.remove(), 3000);
}

playCompleteSound() {
  const audioContext = new (window.AudioContext || window.webkitAudioContext)();
  const oscillator = audioContext.createOscillator();
  const gain = audioContext.createGain();
  
  oscillator.connect(gain);
  gain.connect(audioContext.destination);
  
  oscillator.frequency.value = 1000;
  oscillator.type = 'sine';
  
  gain.gain.setValueAtTime(0.3, audioContext.currentTime);
  gain.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
  
  oscillator.start();
  oscillator.stop(audioContext.currentTime + 0.5);
}

updateTitleBar() {
  const remaining = this.timer.getRemaining();
  const formattedTime = this.timer.formatTime(remaining);
  document.title = `${formattedTime} - ポモドーロタイマー`;
}
```

#### CSS トースト

```css
.toast {
  position: fixed;
  bottom: 20px;
  right: 20px;
  background: #10b981;
  color: white;
  padding: 16px 24px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  animation: slideIn 0.3s ease;
  z-index: 1000;
}

@keyframes slideIn {
  from {
    transform: translateX(400px);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.btn-start:hover {
  transform: scale(1.05);
  box-shadow: 0 6px 20px rgba(79, 70, 229, 0.3);
}

.btn-start:active {
  transform: scale(0.98);
}
```

#### デリバリー
```
ブラウザで以下が確認：
✓ 完了時にトースト通知が表示
✓ ビープ音が再生
✓ タイトルバーに時間が表示
✓ ボタンホバー時に視覚効果
✓ エラー時に通知表示
```

#### 成果物 Checklist
- [ ] `timer.js` UX 機能追加
- [ ] `static/css/style.css` トースト・ホバー効果追加
- [ ] ブラウザで動作確認

---

### **Sprint 9: テスト・品質保証 & API 実装** 🧪
**所要時間**: 2-3 時間  
**目標**: テストカバレッジ >90%、Flask API 実装

#### 実装内容

| # | タスク | 詳細 | 対象ファイル |
|---|--------|------|----------|
| 9-1 | Python テストカバレッジ | 不足部分カバレッジ追加 | `pytest --cov` |
| 9-2 | JavaScript テストカバレッジ | 不足部分カバレッジ追加 | `jest --coverage` |
| 9-3 | Flask API テスト完全化 | エンドポイント全テスト | `test_api.py` |
| 9-4 | Flask API 実装 | セッション保存 DB連携 | `app.py` |
| 9-5 | Integration テスト | 全層統合テスト | `test_integration.py` |
| 9-6 | ドキュメント完成 | API 仕様書、ユーザーガイド | `.md` ファイル |

#### テスト実装例

```python
# test_api.py
def test_save_session(client):
    response = client.post('/api/sessions', json={
        'completed_at': '2024-01-01T10:00:00',
        'duration': 25
    })
    assert response.status_code == 201
    assert response.json['status'] == 'success'

def test_get_stats(client):
    response = client.get('/api/stats/today')
    assert response.status_code == 200
    assert 'completed' in response.json
```

#### Flask API 実装

```python
# app.py 更新
from datetime import datetime
from storage import FileStorage

storage = FileStorage()

@app.route('/api/sessions', methods=['POST'])
def save_session():
    """セッション保存 API"""
    try:
        data = request.json
        session_id = storage.save_session({
            'completed_at': datetime.now().isoformat(),
            'duration': data.get('duration', 25)
        })
        return jsonify({'status': 'success', 'id': session_id}), 201
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/stats/today')
def get_stats():
    """本日の統計取得 API"""
    try:
        stats = storage.load_stats()
        today_stats = {
            'completed': stats.get('completed', 0),
            'totalMinutes': stats.get('totalMinutes', 0)
        }
        return jsonify(today_stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

#### テスト実行コマンド

```bash
# Python テストカバレッジ
pytest tests/ --cov=. --cov-report=html
# 出力: htmlcov/index.html

# JavaScript テストカバレッジ
npm test -- --coverage
# 出力: coverage/ ディレクトリ

# 統合テスト
pytest tests/test_integration.py -v
```

#### デリバリー
- [ ] テストカバレッジ Python >90%
- [ ] テストカバレッジ JavaScript >90%
- [ ] Flask API 全エンドポイント実装・テスト
- [ ] ドキュメント（README.md、API仕様書）完成
- [ ] 本番デプロイ準備完了

#### 成果物 Checklist
- [ ] `test_api.py` 完成
- [ ] Flask API 完全実装
- [ ] `storage.py` ファイル永続化実装
- [ ] テストカバレッジレポート

---

## 📈 実装進捗サマリー

```
【Sprint 0-2: 基盤構築】 3-4 時間
├─ ビジネスロジック完成 ✓
├─ Flask 基本 API ✓
└─ テスト環境準備 ✓

【Sprint 3-6: UI 統合】 7-9 時間
├─ HTML/CSS 完成 ✓
├─ タイマー制御 ✓
├─ 円形プログレス ✓
└─ LocalStorage ✓

【Sprint 7-9: 完成・最適化】 4-5 時間
├─ UX 機能完成 ✓
├─ テスト完全化 ✓
├─ API 実装 ✓
└─ ドキュメント ✓

合計: 14-18 時間 (開発規模: 中程度)
```

---

## 🎯 各スプリント間での動作確認ポイント

| Sprint | 動作確認項目 | 検証方法 |
|--------|----------|--------|
| 0 | ページ表示 | ブラウザアクセス |
| 1-2 | TestPass | pytest, npm test |
| 3-4 | 時間表示・ボタン動作 | ブラウザ F12 Console |
| 5-6 | 円形プログレス更新 | ブラウザ DevTools |
| 7 | LocalStorage 保存 | ブラウザ DevTools → Application |
| 8 | トースト・音声 | ブラウザ実行 |
| 9 | API 連携・テスト | pytest --cov, npm test --coverage |

---

## ⚙️ 依存性グラフ

```
【独立】
├── timer_logic.py (Sprint 1)
└── timer-core.js (Sprint 2)
    ↓
【依存（ビジネスロジック）】
├── storage.py (Sprint 3)
├── storage-api.js (Sprint 5)
    ↓
【依存（ストレージ）】
├── app.py (Flask API)
├── timer.js (UI層)
├── index.html
├── style.css
    ↓
【最終統合】
└── 完全なアプリケーション (Sprint 9)
```

---

## 📝 実装開始時のチェックリスト

実装を開始する前に以下をご確認ください。

- [ ] Python 環境が構築されている（Python 3.8+）
- [ ] Flask がインストールされている
- [ ] pytest がインストールされている
- [ ] Node.js + npm がインストールされている
- [ ] Jest がインストールされている
- [ ] テスト用ブラウザコンソール分析ツール（F12）が使用可能

---

## 🔗 関連ドキュメント

- [architecture.md](../architecture.md) - アーキテクチャ全体設計
- [features.md](features.md) - 機能要件一覧
- [UIモック](pomodoro.png) - UI仕様書

---

**最終更新**: 2024年

このplan.mdをセプリント実装の参考にしてください！
