# API リファレンス

ポモドーロタイマー Web アプリケーションの REST API リファレンスです。

---

## ベース URL

```
http://localhost:5000
```

---

## エンドポイント一覧

### `GET /`

メインページ（HTML）を返します。

**レスポンス**

- ステータスコード: `200 OK`
- Content-Type: `text/html`
- ボディ: `templates/index.html` のレンダリング結果

---

### `POST /api/sessions`

作業セッションの完了を記録します。

**リクエスト**

- Content-Type: `application/json`

| フィールド  | 型      | 必須 | 説明                 |
|-----------|--------|------|----------------------|
| `duration` | integer | ✓    | 集中時間（分）。正の整数のみ受け付ける。 |

**リクエスト例**

```json
{
  "duration": 25
}
```

**レスポンス（成功）**

- ステータスコード: `201 Created`
- Content-Type: `application/json`

| フィールド  | 型      | 説明                    |
|-----------|--------|-------------------------|
| `id`       | integer | 保存されたセッションの ID  |
| `duration` | integer | 記録された集中時間（分）   |

**レスポンス例（成功）**

```json
{
  "id": 1,
  "duration": 25
}
```

**レスポンス（エラー）**

- ステータスコード: `400 Bad Request`
- Content-Type: `application/json`

エラーになるケース:
- `duration` が整数でない（文字列、浮動小数点など）
- `duration` が 0 以下
- `duration` フィールドが存在しない
- リクエストボディが JSON でない

**エラーレスポンス例**

```json
{
  "error": "duration must be an integer"
}
```

```json
{
  "error": "duration must be a positive integer"
}
```

---

### `GET /api/sessions/today`

当日（UTC）の作業セッション集計結果を返します。

**リクエスト**

パラメータなし。

**レスポンス（成功）**

- ステータスコード: `200 OK`
- Content-Type: `application/json`

| フィールド        | 型      | 説明                       |
|----------------|--------|----------------------------|
| `completed`     | integer | 当日完了したセッション数         |
| `total_minutes` | integer | 当日の合計集中時間（分）         |

**レスポンス例**

```json
{
  "completed": 4,
  "total_minutes": 100
}
```

セッションがない場合:

```json
{
  "completed": 0,
  "total_minutes": 0
}
```
