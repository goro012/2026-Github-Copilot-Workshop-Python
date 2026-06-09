# フロントエンドモジュール仕様

`1.pomodoro/static/js/` および `1.pomodoro/templates/index.html` のフロントエンド実装。

---

## JavaScript モジュール

### PomodoroTimer（`timer.js`）

カウントダウンとフェーズ管理を担うクラス。ブラウザ API（DOM）に非依存で、コールバック経由で外部に通知する。

#### コンストラクタ

````javascript
new PomodoroTimer({ onTick, onPhaseChange, onComplete })
````

| コールバック    | シグネチャ                                           | 呼び出しタイミング                     |
|-------------|--------------------------------------------------|-------------------------------------|
| `onTick`    | `(secondsLeft: number, totalSeconds: number, phase: string) => void` | 毎秒（1秒ごと）             |
| `onPhaseChange` | `(newPhase: string) => void`                 | フェーズ切り替え時                     |
| `onComplete`| `(durationMinutes: number) => void`              | 作業フェーズ完了時のみ                  |

#### フェーズ設定

| フェーズ名      | 時間      |
|--------------|---------|
| `work`       | 25分（1500秒）|
| `short_break`| 5分（300秒）  |
| `long_break` | 15分（900秒） |

4ポモドーロ（作業フェーズ）ごとに `long_break` へ遷移する。それ以外は `short_break` へ遷移する。

#### 公開プロパティ（読み取り専用）

| プロパティ        | 型      | 説明                |
|----------------|--------|---------------------|
| `phase`         | string | 現在のフェーズ名       |
| `secondsLeft`   | number | 残り秒数             |
| `totalSeconds`  | number | 現フェーズの総秒数     |
| `isRunning`     | boolean| タイマー動作中かどうか  |
| `pomodoroCount` | number | 完了した作業フェーズ数  |

#### 公開メソッド

| メソッド    | 説明                                    |
|----------|---------------------------------------|
| `start()` | タイマー開始。実行中の場合は何もしない。      |
| `pause()` | タイマー一時停止。停止中の場合は何もしない。   |
| `reset()` | 全状態をリセット。作業フェーズの先頭に戻る。  |

---

### CircleRenderer（`renderer.js`）

SVG 円形プログレスバーの描画、タイマー表示更新、フェーズラベル表示、波紋エフェクトを担うクラス。

#### コンストラクタ

````javascript
new CircleRenderer(ringId, displayId, labelId)
````

| 引数         | 型     | 説明                              |
|------------|------|----------------------------------|
| `ringId`   | string | SVG `<circle>` 要素の id（`ring-progress`）|
| `displayId`| string | タイマー数字表示要素の id（`timer-display`）|
| `labelId`  | string | フェーズラベル要素の id（`phase-label`）   |

#### メソッド

**`update(secondsLeft, totalSeconds)`**

- SVG `stroke-dashoffset` を更新して進捗を描画する（半径 80, 周長 = 2πr）
- リングの色を残り時間に応じて変化させる（青 → 黄 → 赤）
  - progress 1.0（100%残り）: `hsl(220, 80%, 55%)` （青）
  - progress 0.5（50%残り）: `hsl(48, 80%, 55%)` （黄）
  - progress 0.0（0%残り）: `hsl(4, 80%, 55%)` （赤）
- タイマー表示を `MM:SS` 形式で更新する

**`setPhaseLabel(phase)`**

| phase         | 表示ラベル  | 波紋エフェクト |
|--------------|----------|------------|
| `work`       | 作業中     | 表示（開始） |
| `short_break`| 短い休憩   | 非表示（停止）|
| `long_break` | 長い休憩   | 非表示（停止）|

波紋エフェクトは SVG 内に `<circle class="ripple">` を3つ生成し、`animationDelay` を 0.8s ずつずらして表示する。

---

### ApiClient（`api.js`）

Flask API と非同期通信するクラス。すべてのメソッドは `async` で `Promise` を返す。エラー時は `Error` をスローする。

| メソッド                  | HTTPメソッド | パス                  | 戻り値の型                                              |
|------------------------|-----------|----------------------|-------------------------------------------------------|
| `postSession(duration)` | POST      | `/api/sessions`      | `{ id: number, duration: number }`                    |
| `getTodayStats()`       | GET       | `/api/sessions/today`| `{ completed: number, total_minutes: number }`        |
| `getGamification()`     | GET       | `/api/gamification`  | ゲーミフィケーション統計オブジェクト（`api-reference.md` 参照）|
| `getWeeklyStats()`      | GET       | `/api/stats/weekly`  | 週間統計オブジェクト（`api-reference.md` 参照）           |
| `getMonthlyStats()`     | GET       | `/api/stats/monthly` | 月間統計オブジェクト（`api-reference.md` 参照）           |

---

## HTML テンプレート（`templates/index.html`）

シングルページアプリケーション。`static/js/` の3クラスを読み込み、インライン `<script>` で初期化・イベント処理を行う。

### 主要 DOM 要素

| id                | 種別     | 役割                          |
|------------------|--------|------------------------------|
| `phase-label`     | `<p>`   | 現在フェーズ名（作業中 など）     |
| `ring-progress`   | SVG `<circle>` | プログレスリング（CircleRenderer が操作）|
| `timer-display`   | `<div>` | タイマー残り時間（MM:SS）         |
| `btn-start`       | `<button>` | 開始 / 一時停止 ボタン          |
| `btn-reset`       | `<button>` | リセットボタン                  |
| `stat-completed`  | `<span>` | 今日の完了数                   |
| `stat-minutes`    | `<span>` | 今日の集中時間                  |
| `stat-streak`     | `<span>` | 連続達成日数                   |
| `level-badge`     | `<span>` | 現在レベル（例: `Lv.1`）        |
| `xp-bar-fill`     | `<div>` | XP バーの塗り幅（`width` %スタイル）|
| `xp-label`        | `<span>` | XP 表示（例: `300 / 500 XP`）  |
| `badges-list`     | `<div>` | 獲得バッジ一覧                  |
| `btn-stats-toggle`| `<button>` | 統計パネルの表示/非表示トグル    |
| `stats-panel`     | `<div>` | 統計パネル（初期状態: `display:none`）|
| `stats-chart-area`| `<div>` | 棒グラフ描画エリア               |
| `stats-summary`   | `<div>` | 統計サマリーテキスト              |

### インライン JS の役割

- `refreshStats()` — `ApiClient.getTodayStats()` を呼び出し、完了数・集中時間を表示する
- `refreshGamification()` — `ApiClient.getGamification()` を呼び出し、レベル・XP・バッジを表示する
- `formatMinutes(total)` — 分を `X時間Y分` または `Y分` 形式に変換するユーティリティ
- `renderBarChart(days)` — 日別データを棒グラフ HTML に変換する
- `loadStats(tab)` — 週間/月間タブに応じて統計データを取得・描画する
- ページ読み込み時に `refreshStats()` と `refreshGamification()` を即時実行する
- 作業フェーズ完了時（`onComplete`）に `postSession → refreshStats → refreshGamification` の順で実行する

---

## CSS（`static/css/style.css`）

紫系グラデーションテーマ（`#7c6fe3` → `#9b8eef` → `#b3a8f5`）を使用。カード幅 340px の固定レイアウト。

### 主なクラス

| クラス               | 説明                                             |
|--------------------|------------------------------------------------|
| `.app-bg`           | 全画面背景（紫グラデーション）                         |
| `.app-bg.working`   | 集中時間中に追加されるクラス。放射グローアニメーションを有効化 |
| `.card`             | メインカード（白背景、角丸 20px）                     |
| `.timer-ring-wrapper`| SVG リングとタイマー表示をまとめるラッパー             |
| `.ripple`           | 波紋エフェクト用 SVG circle（CSS アニメーション適用）   |
| `.xp-bar-fill`      | XP バーの塗り部分（`width` を % で動的変更）          |
| `.badge-item`       | バッジ1件の表示要素                                 |
| `.stats-tab.active` | アクティブな統計タブのスタイル                         |
| `.chart-bar`        | 統計棒グラフの棒（高さを % で動的変更）                |
