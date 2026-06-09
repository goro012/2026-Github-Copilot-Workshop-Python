# データモデル仕様

ポモドーロタイマー Web アプリケーションで使用するデータモデルを説明します。

---

## Session モデル

**ファイル**: `models.py`  
**テーブル名**: `sessions`  
**ORM**: Flask-SQLAlchemy

### カラム定義

| カラム名        | 型        | 制約                  | 説明                           |
|--------------|----------|----------------------|-------------------------------|
| `id`          | Integer  | PRIMARY KEY, 自動採番  | セッションの一意識別子              |
| `completed_at`| DateTime | NOT NULL, デフォルト: `datetime.utcnow` | セッション完了日時（UTC）  |
| `duration`    | Integer  | NOT NULL              | 集中時間（分）                   |

### モデル定義（コード）

```python
class Session(db.Model):
    __tablename__ = "sessions"

    id           = db.Column(db.Integer, primary_key=True)
    completed_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    duration     = db.Column(db.Integer, nullable=False)
```

---

## データベース設定

| 環境        | URI                              |
|-----------|----------------------------------|
| 本番（開発） | `sqlite:///pomodoro.db`（ファイル） |
| テスト      | `sqlite:///:memory:`（インメモリ）  |

設定は `config.py` で管理されます:

```python
class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///pomodoro.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
```

---

## バリデーションルール

`duration` フィールドに対するバリデーションは `PomodoroService.complete_session()` で実施されます。

| ルール            | エラー                                    |
|----------------|------------------------------------------|
| 整数型であること    | `duration must be an integer`（route 層）  |
| 1 以上であること   | `duration must be a positive integer`（service 層） |

---

## API レスポンス形式

セッション保存後のレスポンス（`POST /api/sessions` の返却値）:

```json
{
  "id": 1,
  "duration": 25
}
```

今日の集計（`GET /api/sessions/today` の返却値）:

```json
{
  "completed": 4,
  "total_minutes": 100
}
```
