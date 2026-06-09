# データモデル仕様

ポモドーロタイマーアプリで使用するデータモデルの定義。

---

## Session（セッションモデル）

`models.py` で定義。Flask-SQLAlchemy を使用し、SQLite の `sessions` テーブルにマッピングされる。

````python
class Session(db.Model):
    __tablename__ = "sessions"

    id           = db.Column(db.Integer, primary_key=True)
    completed_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    duration     = db.Column(db.Integer, nullable=False)
````

| カラム        | 型        | 制約                     | 説明                     |
|-------------|----------|------------------------|------------------------|
| `id`         | Integer  | PRIMARY KEY, AUTO INCREMENT | セッションの一意識別子     |
| `completed_at`| DateTime | NOT NULL, デフォルト: UTC現在時刻 | セッション完了日時（UTC） |
| `duration`   | Integer  | NOT NULL               | 集中時間（分）             |

---

## リポジトリ（SessionRepository）

`repositories.py` で定義。`Session` モデルへのデータアクセスをカプセル化する。

| メソッド                               | 引数                                | 戻り値             | 説明                                         |
|--------------------------------------|------------------------------------|--------------------|---------------------------------------------|
| `save_session(duration)`             | `duration: int`                    | `Session`          | 新規セッションを作成・保存して返す               |
| `find_today_sessions()`              | なし                                | `list[Session]`    | 当日 0:00 以降のセッションをすべて返す           |
| `find_all_sessions()`                | なし                                | `list[Session]`    | 全セッションを完了日時の降順で返す               |
| `find_sessions_in_range(start, end)` | `start: datetime`, `end: datetime` | `list[Session]`    | 指定期間内（`start` 以上 `end` 以下）のセッションを返す |

---

## サービス層のデータ構造

### PomodoroService

#### `complete_session(duration: int) -> dict`

バリデーション: `duration` が正の整数でない場合は `ValueError` を送出。

````json
{ "id": 1, "duration": 25 }
````

#### `get_today_stats() -> dict`

````json
{
  "completed": 4,
  "total_minutes": 100
}
````

---

### GamificationService

#### 定数

| 定数名               | 値   | 説明                        |
|--------------------|-----|---------------------------|
| `XP_PER_SESSION`   | 100 | 1セッション完了ごとに獲得する XP  |
| `XP_PER_LEVEL`     | 500 | 1レベルアップに必要な XP         |

#### `get_gamification_stats() -> dict`

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

#### バッジデータ構造

| フィールド      | 型     | 説明          |
|-------------|------|--------------|
| `id`         | string | バッジ識別子   |
| `name`       | string | 表示名         |
| `description`| string | バッジの説明文  |

#### `get_weekly_stats() -> dict` / `get_monthly_stats() -> dict`

````json
{
  "days": [
    { "date": "2026-06-03", "completed": 3, "total_minutes": 75 }
  ],
  "total_completed": 10,
  "total_minutes": 250
}
````

#### ストリーク計算ロジック

- 全セッションの `completed_at.date()` を重複除去・降順ソートする
- 今日から遡って連続している日数をカウントする
- 途切れた時点で集計を終了する

#### レベル計算ロジック

````
total_xp    = セッション数 × 100
level       = total_xp // 500 + 1
xp_in_level = total_xp % 500
````

---

## 設定

`config.py` で定義。

| クラス        | `SQLALCHEMY_DATABASE_URI`   | 用途              |
|-------------|----------------------------|-----------------|
| `Config`    | `sqlite:///pomodoro.db`    | 通常実行（ファイル DB） |
| `TestConfig`| `sqlite:///:memory:`       | テスト実行（インメモリ DB）|
