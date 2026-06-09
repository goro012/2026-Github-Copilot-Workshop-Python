# アーキテクチャ概要

Flask + HTML/CSS/JavaScript で構築されたポモドーロタイマー Web アプリケーションの現在のアーキテクチャを記述する。

---

## ディレクトリ構成

```
1.pomodoro/
├── app.py               # App Factory（create_app）、ルート定義
├── config.py            # 環境別設定クラス
├── models.py            # SQLAlchemy モデル定義
├── repositories.py      # DB アクセス層
├── services.py          # ビジネスロジック層
├── requirements.txt     # 依存パッケージ
├── static/
│   ├── css/
│   │   └── style.css    # 紫系カラーテーマ
│   └── js/
│       ├── timer.js     # PomodoroTimer クラス（タイマーロジック）
│       ├── renderer.js  # CircleRenderer クラス（SVG 描画）
│       └── api.js       # ApiClient クラス（Flask API 通信）
├── templates/
│   └── index.html       # メインページ（JS の初期化・イベントバインディングを含む）
├── docs/                # ドキュメント
└── tests/
    ├── conftest.py          # pytest フィクスチャ
    ├── test_services.py     # サービス層のテスト（モック使用）
    ├── test_repositories.py # リポジトリ層のテスト（インメモリ SQLite）
    └── test_routes.py       # HTTP エンドポイントのテスト
```

---

## バックエンドレイヤー構成

```
[ Flask Routes (app.py) ]
        ↓ 呼び出し
[ Service Layer (services.py) ]   ← ビジネスロジック・バリデーション
        ↓ 依存注入（DI）
[ Repository Layer (repositories.py) ]
        ↓
[ SQLite (models.py / SQLAlchemy) ]
```

### App Factory パターン

`app.py` の `create_app(config=None)` 関数でアプリケーションを生成する。  
テスト時は `TestConfig`（インメモリ SQLite）を渡すことで本番 DB を汚染せずにテストできる。

```python
def create_app(config=None):
    app = Flask(__name__)
    app.config.from_object(config or Config)
    db.init_app(app)
    with app.app_context():
        db.create_all()
    # ルート定義 ...
    return app
```

### 依存注入（DI）

`PomodoroService` はコンストラクタで `SessionRepository` を受け取る。  
テスト時はモックに差し替え可能。

```python
class PomodoroService:
    def __init__(self, repo: SessionRepository | None = None):
        self.repo = repo or SessionRepository()
```

---

## フロントエンド構成

### クラス分離

| クラス | ファイル | 責務 |
|---|---|---|
| `PomodoroTimer` | `timer.js` | カウントダウン・フェーズ管理（ブラウザ API に非依存） |
| `CircleRenderer` | `renderer.js` | SVG 円形プログレスバーの描画 |
| `ApiClient` | `api.js` | Flask API との通信（`fetch` 使用） |

メイン処理（インスタンス生成・イベントバインディング）は `index.html` 内の `<script>` タグに記述されている。

### データフロー

```
ブラウザ (JS)
  │
  ├─ 開始ボタンクリック → PomodoroTimer.start()
  │
  ├─ 毎秒 tick → CircleRenderer.update(secondsLeft, totalSeconds)
  │
  ├─ フェーズ完了（作業） → ApiClient.postSession(durationMinutes)
  │                              ↓
  │                        POST /api/sessions → Flask → SQLite 保存
  │
  └─ セッション保存後 → ApiClient.getTodayStats()
                              ↓
                        GET /api/sessions/today → Flask → SQLite 集計
                              ↓
                        統計表示を更新（完了数・集中時間）
```

---

## 設定管理

| クラス | DB URI | 用途 |
|---|---|---|
| `Config` | `sqlite:///pomodoro.db` | 本番（開発） |
| `TestConfig` | `sqlite:///:memory:` | テスト実行時 |

---

## テスト戦略

| テスト種別 | ファイル | 手法 |
|---|---|---|
| ビジネスロジック | `test_services.py` | `unittest.mock.MagicMock` でリポジトリをモック |
| DB 操作 | `test_repositories.py` | インメモリ SQLite（`TestConfig`）を使用 |
| HTTP エンドポイント | `test_routes.py` | Flask test client を使用 |

テスト実行コマンド:

```bash
python -m pytest 1.pomodoro/tests/
```

---

## 採用技術

| 区分 | 技術 |
|---|---|
| バックエンド | Python / Flask |
| ORM | Flask-SQLAlchemy |
| DB | SQLite |
| フロントエンド | HTML / CSS / Vanilla JS |
| テスト | pytest / unittest.mock |
