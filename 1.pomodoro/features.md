# ポモドーロタイマー 実装機能一覧

## バックエンド機能

### アプリケーション基盤
- [ ] Flask アプリケーション初期化（App Factory パターン）
- [ ] 環境別設定管理（`Config` / `TestConfig`）
- [ ] SQLAlchemy のセットアップ・DB マイグレーション
- [ ] `Session` モデルの定義（`id`, `completed_at`, `duration`）

### API エンドポイント
- [ ] `GET /` — `index.html` を返す
- [ ] `POST /api/sessions` — セッション完了を記録（`duration` を受け取り保存）
- [ ] `GET /api/sessions/today` — 今日の完了数・集中時間を返す

### ビジネスロジック（`services.py`）
- [ ] セッション保存時のバリデーション（`duration > 0` チェック）
- [ ] 今日の集計ロジック（完了数・合計時間の算出）

### データアクセス（`repositories.py`）
- [ ] `save_session(duration)` — セッションを DB に保存
- [ ] `find_today_sessions()` — 当日分のセッションを取得

---

## フロントエンド機能

### タイマーロジック（`timer.js` / `PomodoroTimer`）
- [ ] カウントダウン処理（1秒ごとに残り時間を減算）
- [ ] 開始 / 一時停止の切り替え
- [ ] リセット（現在フェーズの時間に戻す）
- [ ] フェーズ自動遷移（作業 → 短い休憩 → 作業 → … → 長い休憩）
- [ ] 4ポモドーロごとに長い休憩へ切り替え
- [ ] フェーズ完了時に API へセッション記録を送信（作業フェーズのみ）

### 円形プログレスバー（`renderer.js` / `CircleRenderer`）
- [ ] SVG `stroke-dashoffset` による進捗描画
- [ ] タイマー残り時間に応じてリアルタイム更新
- [ ] フェーズ切り替え時にリセット描画

### 画面表示（`index.html` + `style.css`）
- [ ] 現在フェーズ名の表示（「作業中」「短い休憩」「長い休憩」）
- [ ] 残り時間の `MM:SS` フォーマット表示
- [ ] 「開始」ボタン（開始中は「一時停止」に切り替え）
- [ ] 「リセット」ボタン
- [ ] 「今日の進捗」セクション（完了数・集中時間）
- [ ] 紫系カラーテーマの CSS

### API 通信（`api.js` / `ApiClient`）
- [ ] `POST /api/sessions` を呼び出してセッションを記録
- [ ] `GET /api/sessions/today` を呼び出して進捗を取得・画面に反映

---

## テスト

- [ ] `conftest.py` — pytest フィクスチャ（app, client, インメモリ DB）
- [ ] `test_services.py` — `PomodoroService` のモックテスト
- [ ] `test_repositories.py` — リポジトリの DB 操作テスト
- [ ] `test_routes.py` — HTTP エンドポイントのテスト

---

## インフラ・設定

- [ ] `requirements.txt` の作成（Flask, SQLAlchemy, pytest 等）

---

## 機能一覧サマリー

| カテゴリ | 機能数 |
|---|---|
| バックエンド基盤 | 4 |
| API エンドポイント | 3 |
| ビジネスロジック | 2 |
| データアクセス | 2 |
| タイマーロジック | 6 |
| 描画 | 3 |
| 画面表示・CSS | 7 |
| API 通信 | 2 |
| テスト | 4 |
| インフラ | 1 |
| **合計** | **34** |
