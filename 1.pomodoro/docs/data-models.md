# データモデル仕様

アプリケーションが使用するデータモデルを記述する。

---

## Session モデル

**ファイル**: `models.py`  
**テーブル名**: `sessions`  
**ORM**: Flask-SQLAlchemy

### カラム定義

| カラム名 | 型 | 制約 | 説明 |
|---|---|---|---|
| `id` | Integer | PRIMARY KEY, AUTO INCREMENT | セッションの主キー |
| `completed_at` | DateTime | NOT NULL, デフォルト: `datetime.utcnow` | セッション完了日時（UTC） |
| `duration` | Integer | NOT NULL | 集中時間（分） |

### Python 定義

```python
class Session(db.Model):
    __tablename__ = "sessions"

    id           = db.Column(db.Integer, primary_key=True)
    completed_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    duration     = db.Column(db.Integer, nullable=False)
```

---

## リポジトリ層

**ファイル**: `repositories.py`  
**クラス**: `SessionRepository`

### メソッド

#### `save_session(duration: int) -> Session`

セッションを DB に保存して返す。

- `completed_at` には保存時点の UTC 日時（`datetime.utcnow()`）が設定される。
- `db.session.commit()` を呼び出してトランザクションをコミットする。

```python
def save_session(self, duration: int) -> Session:
    session = Session(duration=duration, completed_at=datetime.utcnow())
    db.session.add(session)
    db.session.commit()
    return session
```

#### `find_today_sessions() -> list[Session]`

当日 00:00:00（UTC 基準）以降に `completed_at` が設定されたセッションを全件返す。

```python
def find_today_sessions(self) -> list[Session]:
    today_start = datetime.combine(date.today(), datetime.min.time())
    return Session.query.filter(Session.completed_at >= today_start).all()
```

---

## サービス層の制約

**ファイル**: `services.py`  
**クラス**: `PomodoroService`

`save_session` を呼び出す前に以下のバリデーションが実施される。

| 条件 | 例外 |
|---|---|
| `duration` が `int` 型でない | `ValueError("duration must be a positive integer")` |
| `duration <= 0` | `ValueError("duration must be a positive integer")` |

---

## DB 設定

| 設定 | 値 |
|---|---|
| 本番 DB URI | `sqlite:///pomodoro.db`（`instance/` フォルダ以下に生成） |
| テスト DB URI | `sqlite:///:memory:`（テスト終了後に破棄） |
| `SQLALCHEMY_TRACK_MODIFICATIONS` | `False` |
