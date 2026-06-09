# フロントエンド仕様

ポモドーロタイマーアプリケーションのフロントエンドモジュールを記述する。

---

## モジュール構成

| ファイル | クラス | 責務 |
|---|---|---|
| `static/js/timer.js` | `PomodoroTimer` | カウントダウン処理・フェーズ管理 |
| `static/js/renderer.js` | `CircleRenderer` | SVG 円形プログレスバーの描画 |
| `static/js/api.js` | `ApiClient` | Flask API との通信 |
| `templates/index.html` | — | HTML 構造・JS の初期化・イベントバインディング |
| `static/css/style.css` | — | 紫系カラーテーマのスタイル定義 |

---

## PomodoroTimer (`timer.js`)

ブラウザ API（DOM）に依存しないタイマーロジッククラス。  
コールバック経由で外部（`index.html` の初期化スクリプト）に状態変化を通知する。

### フェーズ設定

| フェーズ | 定数名 | 時間 |
|---|---|---|
| 作業 | `work` | 25 分（1500 秒） |
| 短い休憩 | `short_break` | 5 分（300 秒） |
| 長い休憩 | `long_break` | 15 分（900 秒） |

4 ポモドーロ（作業フェーズ）完了ごとに長い休憩へ移行する（`POMODOROS_BEFORE_LONG = 4`）。

### コンストラクタ

```javascript
new PomodoroTimer({ onTick, onPhaseChange, onComplete })
```

| コールバック | シグネチャ | 呼び出しタイミング |
|---|---|---|
| `onTick` | `(secondsLeft, totalSeconds, phase) => void` | 毎秒（1 秒ごと） |
| `onPhaseChange` | `(newPhase) => void` | フェーズ切り替え時 |
| `onComplete` | `(durationMinutes) => void` | 作業フェーズ完了時 |

### 読み取り専用プロパティ

| プロパティ | 型 | 説明 |
|---|---|---|
| `phase` | string | 現在のフェーズ名（`'work'` / `'short_break'` / `'long_break'`） |
| `secondsLeft` | number | 現在フェーズの残り秒数 |
| `totalSeconds` | number | 現在フェーズの総秒数 |
| `isRunning` | boolean | タイマーが動作中かどうか |
| `pomodoroCount` | number | 完了した作業フェーズの累計数 |

### 公開メソッド

| メソッド | 説明 |
|---|---|
| `start()` | タイマーを開始する。既に動作中の場合は何もしない |
| `pause()` | タイマーを一時停止する |
| `reset()` | 全状態をリセットし、作業フェーズの先頭に戻る |

### フェーズ遷移ロジック

```
作業完了 → pomodoroCount をインクリメント
         → pomodoroCount % 4 === 0 ? 長い休憩 : 短い休憩
休憩完了 → 作業フェーズへ
```

---

## CircleRenderer (`renderer.js`)

SVG の `stroke-dashoffset` を操作して円形プログレスバーとタイマー表示を更新するクラス。

### コンストラクタ

```javascript
new CircleRenderer(ringId, displayId, labelId)
```

| 引数 | 説明 |
|---|---|
| `ringId` | SVG の `<circle id="ring-progress">` の id |
| `displayId` | タイマー表示要素（`MM:SS`）の id |
| `labelId` | フェーズラベル要素の id |

SVG の円の半径は `r="80"` で固定。円周 = `2π × 80 ≈ 502.65`。

### メソッド

#### `update(secondsLeft, totalSeconds)`

進捗リングとタイマー表示（`MM:SS` 形式）を更新する。

```javascript
const progress = totalSeconds > 0 ? secondsLeft / totalSeconds : 1;
const offset   = circumference * (1 - progress);
ring.style.strokeDashoffset = offset;
```

#### `setPhaseLabel(phase)`

フェーズ名を日本語でラベル表示する。

| `phase` | 表示テキスト |
|---|---|
| `'work'` | 作業中 |
| `'short_break'` | 短い休憩 |
| `'long_break'` | 長い休憩 |

---

## ApiClient (`api.js`)

`fetch` API を使って Flask バックエンドと通信するクラス。

### メソッド

#### `postSession(duration)`

作業セッションの完了を記録する。

```javascript
await fetch('/api/sessions', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ duration }),
});
```

- 引数: `duration` (number) — 集中時間（分）
- 戻り値: `Promise<{ id: number, duration: number }>`
- HTTP ステータスが 2xx 以外の場合は `Error` を throw する

#### `getTodayStats()`

今日の進捗を取得する。

```javascript
await fetch('/api/sessions/today');
```

- 戻り値: `Promise<{ completed: number, total_minutes: number }>`
- HTTP ステータスが 2xx 以外の場合は `Error` を throw する

---

## index.html の初期化フロー

```javascript
// 1. インスタンス生成
const api      = new ApiClient();
const renderer = new CircleRenderer('ring-progress', 'timer-display', 'phase-label');

// 2. PomodoroTimer をコールバックつきで生成
const timer = new PomodoroTimer({
  onTick(secondsLeft, totalSeconds) {
    renderer.update(secondsLeft, totalSeconds);
  },
  onPhaseChange(phase) {
    renderer.setPhaseLabel(phase);
    btnStart.textContent = '開始';
  },
  async onComplete(durationMinutes) {
    await api.postSession(durationMinutes);
    await refreshStats();
  },
});

// 3. ページ読み込み時に今日の進捗を表示
refreshStats();
```

`total_minutes` の表示形式は `formatMinutes()` 関数で変換される。

| 値 | 表示例 |
|---|---|
| 60 未満 | `45分` |
| 60 以上 | `1時間30分` |
| 60 の倍数 | `2時間` |

---

## CSS スタイル概要 (`style.css`)

| クラス | 説明 |
|---|---|
| `.app-bg` | 紫グラデーション背景（135deg、`#7c6fe3` → `#b3a8f5`） |
| `.card` | 白背景の角丸カード（幅 340px） |
| `.title-bar` | タイトルバー（タイトルテキスト＋ウィンドウコントロール風装飾） |
| `.phase-label` | 現在フェーズ名のテキスト表示 |
| `.timer-ring-wrapper` | 200×200px の SVG タイマーコンテナ |
| `.ring-track` | 背景の円形トラック（薄い紫） |
| `.ring-progress` | 進捗を示す円形インジケーター（`stroke: #7c6fe3`） |
| `.timer-display` | タイマー数字（40px、太字、中央配置） |
| `.btn-primary` | 塗りつぶしボタン（開始/一時停止） |
| `.btn-outline` | アウトラインボタン（リセット） |
| `.progress-section` | 今日の進捗セクション（薄紫背景） |
