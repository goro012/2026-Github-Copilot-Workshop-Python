# フロントエンド モジュールドキュメント

ポモドーロタイマーのフロントエンド実装について説明します。

---

## モジュール構成

| クラス           | ファイル          | 責務                                              |
|----------------|----------------|---------------------------------------------------|
| `PomodoroTimer`  | `timer.js`    | カウントダウンロジック・フェーズ管理（ブラウザ API に非依存） |
| `CircleRenderer` | `renderer.js` | SVG 円形プログレスバーの描画・波紋エフェクト             |
| `ApiClient`      | `api.js`      | Flask バックエンドとの HTTP 通信（fetch）             |

スクリプトの読み込み順（`index.html`）:

```html
<script src="/static/js/renderer.js"></script>
<script src="/static/js/timer.js"></script>
<script src="/static/js/api.js"></script>
```

---

## PomodoroTimer（`timer.js`）

カウントダウンとフェーズ管理を担うクラスです。DOM に依存せず、コールバック経由で外部に通知します。

### フェーズ設定

| フェーズ名      | 定数キー        | 時間    |
|--------------|--------------|--------|
| 作業           | `work`       | 25 分  |
| 短い休憩       | `short_break` | 5 分   |
| 長い休憩       | `long_break`  | 15 分  |

4ポモドーロ完了後に長い休憩へ遷移します（`POMODOROS_BEFORE_LONG = 4`）。

### コンストラクタ

```javascript
new PomodoroTimer({
  onTick(secondsLeft, totalSeconds, phase) { ... },
  onPhaseChange(newPhase) { ... },
  onComplete(durationMinutes) { ... },
})
```

| コールバック    | 呼び出しタイミング           | 引数                                          |
|-------------|--------------------------|----------------------------------------------|
| `onTick`    | 毎秒（1秒ごと）              | `secondsLeft`: 残り秒数, `totalSeconds`: フェーズ総秒数, `phase`: 現在フェーズ |
| `onPhaseChange` | フェーズ切り替え時           | `newPhase`: 新しいフェーズ名                     |
| `onComplete`   | 作業フェーズ完了時（のみ）   | `durationMinutes`: 完了した作業時間（分）         |

### 読み取り専用プロパティ

| プロパティ        | 型      | 説明                    |
|----------------|--------|-------------------------|
| `phase`        | string | 現在のフェーズ名           |
| `secondsLeft`  | number | 残り秒数                  |
| `totalSeconds` | number | 現在フェーズの総秒数        |
| `isRunning`    | boolean | タイマーが動作中かどうか   |
| `pomodoroCount` | number | 完了したポモドーロの数     |

### 公開メソッド

| メソッド  | 説明                                              |
|--------|---------------------------------------------------|
| `start()` | タイマーを開始する。既に実行中の場合は何もしない。    |
| `pause()` | タイマーを一時停止する。停止中の場合は何もしない。   |
| `reset()` | 全状態をリセットし、作業フェーズの先頭に戻る。        |

---

## CircleRenderer（`renderer.js`）

SVG を使った円形プログレスバーと付随するビジュアルエフェクトを管理するクラスです。

### コンストラクタ

```javascript
new CircleRenderer(ringId, displayId, labelId)
```

| 引数        | 説明                                    |
|-----------|----------------------------------------|
| `ringId`   | SVG の進捗リング要素の `id`（`ring-progress`） |
| `displayId` | タイマー数字表示要素の `id`（`timer-display`） |
| `labelId`  | フェーズラベル要素の `id`（`phase-label`）     |

### 公開メソッド

#### `update(secondsLeft, totalSeconds)`

進捗リングの `stroke-dashoffset` と表示時刻を更新します。

- リングカラーは残り時間の割合に応じて青→黄→赤に変化します:
  - 残り 100%〜50%: 青（hue 220°）→ 黄（hue 48°）
  - 残り 50%〜0%: 黄（hue 48°）→ 赤（hue 4°）

#### `setPhaseLabel(phase)`

フェーズラベルを日本語で更新し、波紋エフェクトの有効・無効を切り替えます。

| フェーズ      | 表示テキスト |
|------------|----------|
| `work`      | 作業中    |
| `short_break` | 短い休憩 |
| `long_break`  | 長い休憩 |

波紋エフェクト（SVG の `circle.ripple` 要素）は **作業フェーズ中のみ** 表示されます。

### SVG 仕様

- viewBox: `0 0 200 200`
- 円の半径（`r`）: `80`
- 円周: `2π × 80 ≈ 502.65`
- 進捗計算式:
  ```
  offset = circumference × (1 - secondsLeft / totalSeconds)
  ```

---

## ApiClient（`api.js`）

Flask バックエンドと通信するクラスです。

### メソッド

#### `postSession(duration)`

作業セッションの完了を記録します。

```javascript
await api.postSession(25);
// → { id: 1, duration: 25 }
```

- `POST /api/sessions`
- `Content-Type: application/json`
- 失敗時（HTTP エラー）は `Error` をスローします。

#### `getTodayStats()`

今日の進捗を取得します。

```javascript
const stats = await api.getTodayStats();
// → { completed: 4, total_minutes: 100 }
```

- `GET /api/sessions/today`
- 失敗時（HTTP エラー）は `Error` をスローします。

---

## index.html インライン初期化スクリプト

`index.html` の `<script>` ブロックで各クラスを初期化し、コールバックを通じて連携させています。

```javascript
const api      = new ApiClient();
const renderer = new CircleRenderer('ring-progress', 'timer-display', 'phase-label');
const timer    = new PomodoroTimer({
  onTick(secondsLeft, totalSeconds) {
    renderer.update(secondsLeft, totalSeconds);
  },
  onPhaseChange(phase) {
    renderer.setPhaseLabel(phase);
    btnStart.textContent = '開始';
    appBg.classList.toggle('working', phase === 'work');
  },
  async onComplete(durationMinutes) {
    await api.postSession(durationMinutes);
    await refreshStats();
  },
});
```

### UI 要素

| 要素 ID            | 役割                              |
|------------------|-----------------------------------|
| `ring-progress`   | SVG 進捗リング                     |
| `timer-display`   | タイマー数字表示（`MM:SS` 形式）      |
| `phase-label`     | フェーズラベル（「作業中」など）       |
| `btn-start`       | 開始 / 一時停止 / 再開ボタン          |
| `btn-reset`       | リセットボタン                       |
| `stat-completed`  | 当日の完了セッション数表示            |
| `stat-minutes`    | 当日の集中時間表示（「X時間Y分」形式） |

### 集中時間フォーマット

`total_minutes` の表示形式:

| 条件                     | 表示例        |
|------------------------|-------------|
| 時間と分が両方ある場合     | `1時間30分`  |
| 時間のみ（分が 0）         | `2時間`      |
| 分のみ（1時間未満）        | `45分`       |

---

## CSS テーマ（`style.css`）

紫系グラデーションをベースにしたデザインです。

| クラス               | 役割                                   |
|-------------------|---------------------------------------|
| `.app-bg`          | 背景（紫グラデーション）                   |
| `.app-bg.working`  | 作業中の背景放射グロー（パルスアニメーション）  |
| `.card`            | タイマーカード（白、角丸、シャドウ）          |
| `.ring-track`      | SVG タイマーリングの背景トラック            |
| `.ring-progress`   | SVG タイマーリングの進捗部分               |
| `.ripple`          | 波紋エフェクト（作業中のみ表示、SVG circle） |
| `.btn-primary`     | 開始/一時停止ボタン（塗りつぶし紫）          |
| `.btn-outline`     | リセットボタン（アウトライン紫）             |
| `.progress-section` | 今日の進捗セクション（薄紫背景）            |
