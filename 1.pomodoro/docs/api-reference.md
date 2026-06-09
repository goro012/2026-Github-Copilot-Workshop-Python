# API リファレンス

ポモドーロタイマーアプリケーションが提供する REST API の仕様書です。

---

## 共通仕様

- **ベース URL**: `http://localhost:5000`
- **リクエスト形式**: `application/json`
- **レスポンス形式**: `application/json`

---

## エンドポイント一覧

### GET /

メインページ（`index.html`）を返す。

**レスポンス**

| ステータスコード | 説明 |
|---|---|
| 200 | HTML ページを返す |

---

### POST /api/sessions

作業セッションの完了を記録する。

**リクエストボディ**

```json
{
  "duration": 25
}
```

| フィールド | 型 | 必須 | 説明 |
|---|---|---|---|
| `duration` | integer | ✓ | 集中時間（分）。正の整数のみ有効 |

**レスポンス（成功）**

ステータスコード: `201 Created`

```json
{
  "id": 1,
  "duration": 25
}
```

| フィールド | 型 | 説明 |
|---|---|---|
| `id` | integer | 保存されたセッションの主キー |
| `duration` | integer | 記録された集中時間（分） |

**レスポンス（エラー）**

ステータスコード: `400 Bad Request`

```json
{
  "error": "duration must be an integer"
}
```

| 条件 | エラーメッセージ |
|---|---|
| `duration` が整数でない | `"duration must be an integer"` |
| `duration` が 0 以下 | `"duration must be a positive integer"` |
| リクエストボディが JSON でない | `"duration must be an integer"` |

---

### GET /api/sessions/today

当日（UTC 基準の 00:00:00 以降）に完了したセッションの集計を返す。

**レスポンス（成功）**

ステータスコード: `200 OK`

```json
{
  "completed": 3,
  "total_minutes": 75
}
```

| フィールド | 型 | 説明 |
|---|---|---|
| `completed` | integer | 今日完了したセッション数 |
| `total_minutes` | integer | 今日の集中時間の合計（分） |

セッションがない場合は `completed: 0, total_minutes: 0` を返す。

---

## バリデーション仕様

`POST /api/sessions` のバリデーションは 2 段階で実施される。

1. **ルート層** (`app.py`): `duration` が `int` 型かどうかを確認。型が不正な場合は即座に 400 を返す。
2. **サービス層** (`services.py`): `duration > 0` かどうかを確認。0 以下の場合は `ValueError` を送出し、ルート層が 400 に変換する。
