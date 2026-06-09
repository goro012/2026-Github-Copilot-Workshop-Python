# API リファレンス

ポモドーロタイマーアプリの REST API エンドポイント一覧。

---

## エンドポイント一覧

| メソッド | パス                    | 概要                              |
|--------|------------------------|----------------------------------|
| GET    | `/`                    | メインページ（index.html）を返す    |
| POST   | `/api/sessions`        | セッション完了を記録する            |
| GET    | `/api/sessions/today`  | 今日の進捗（完了数・集中時間）を返す |
| GET    | `/api/gamification`    | ゲーミフィケーション統計を返す       |
| GET    | `/api/stats/weekly`    | 週間統計（過去7日）を返す           |
| GET    | `/api/stats/monthly`   | 月間統計（過去30日）を返す          |

---

## POST /api/sessions

作業セッションの完了を記録する。

### リクエスト

````http
POST /api/sessions
Content-Type: application/json

{
  "duration": 25
}
````

| フィールド  | 型      | 説明                |
|-----------|--------|---------------------|
| `duration` | integer | 集中時間（分）。正の整数のみ有効。 |

### レスポンス（成功）

HTTP ステータス: `201 Created`

````json
{
  "id": 1,
  "duration": 25
}
````

### レスポンス（エラー）

HTTP ステータス: `400 Bad Request`

````json
{ "error": "duration must be an integer" }
````

または

````json
{ "error": "duration must be a positive integer" }
````

---

## GET /api/sessions/today

今日（当日 0:00 以降）に完了したセッションの統計を返す。

### レスポンス

HTTP ステータス: `200 OK`

````json
{
  "completed": 4,
  "total_minutes": 100
}
````

| フィールド       | 型      | 説明               |
|---------------|--------|-------------------|
| `completed`    | integer | 今日の完了セッション数 |
| `total_minutes`| integer | 今日の合計集中時間（分）|

---

## GET /api/gamification

全セッションを集計したゲーミフィケーション統計を返す。

### レスポンス

HTTP ステータス: `200 OK`

````json
{
  "total_xp": 300,
  "level": 1,
  "xp_in_level": 300,
  "xp_to_next_level": 200,
  "xp_per_level": 500,
  "streak": 3,
  "total_sessions": 3,
  "badges": [
    {
      "id": "first",
      "name": "初回達成",
      "description": "最初のポモドーロを完了"
    }
  ]
}
````

| フィールド         | 型      | 説明                                  |
|-----------------|--------|--------------------------------------|
| `total_xp`       | integer | 累計 XP（1セッション = 100 XP）         |
| `level`          | integer | 現在のレベル（500 XP ごとに 1 増加）     |
| `xp_in_level`    | integer | 現在レベル内の XP                       |
| `xp_to_next_level`| integer| 次のレベルまでの残り XP                 |
| `xp_per_level`   | integer | 1レベルアップに必要な XP（固定値: 500）  |
| `streak`         | integer | 連続達成日数                            |
| `total_sessions` | integer | 累計セッション数                         |
| `badges`         | array   | 獲得バッジのリスト                       |

#### バッジ一覧

| バッジID     | 取得条件                        |
|------------|-------------------------------|
| `first`    | 累計セッション数 ≥ 1             |
| `five`     | 累計セッション数 ≥ 5             |
| `ten`      | 累計セッション数 ≥ 10            |
| `streak3`  | 連続達成日数 ≥ 3                 |
| `streak7`  | 連続達成日数 ≥ 7                 |
| `week10`   | 今週（月曜日起点）の完了数 ≥ 10   |

---

## GET /api/stats/weekly

過去7日間（今日を含む）の日別セッション統計を返す。

### レスポンス

HTTP ステータス: `200 OK`

````json
{
  "days": [
    { "date": "2026-06-03", "completed": 3, "total_minutes": 75 },
    { "date": "2026-06-04", "completed": 0, "total_minutes": 0 },
    ...
  ],
  "total_completed": 10,
  "total_minutes": 250
}
````

| フィールド         | 型      | 説明                              |
|-----------------|--------|----------------------------------|
| `days`           | array   | 7日分の日別データ（古い順）           |
| `days[].date`    | string  | 日付（YYYY-MM-DD）                 |
| `days[].completed`| integer| その日の完了セッション数             |
| `days[].total_minutes`| integer | その日の合計集中時間（分）      |
| `total_completed`| integer | 7日間の合計完了数                   |
| `total_minutes`  | integer | 7日間の合計集中時間（分）            |

---

## GET /api/stats/monthly

過去30日間（今日を含む）の日別セッション統計を返す。レスポンス形式は `/api/stats/weekly` と同じ。

### レスポンス

HTTP ステータス: `200 OK`

````json
{
  "days": [
    { "date": "2026-05-11", "completed": 2, "total_minutes": 50 },
    ...
  ],
  "total_completed": 45,
  "total_minutes": 1125
}
````

`days` は30日分（古い順）。それ以外のフィールドは週間統計と同様。
