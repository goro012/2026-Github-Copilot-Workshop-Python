# アーキテクチャ概要

Flask + HTML/CSS/JavaScript で構築したポモドーロタイマー Web アプリケーションの現在の実装アーキテクチャ。

---

## ディレクトリ構成

````
1.pomodoro/
├── app.py               # App Factory（create_app）、Flask ルート定義
├── config.py            # 環境別設定（Config / TestConfig）
├── models.py            # SQLAlchemy モデル（Session）
├── repositories.py      # DB アクセス層（SessionRepository）
├── services.py          # ビジネスロジック層（PomodoroService / GamificationService）
├── requirements.txt     # 依存パッケージ
├── static/
│   ├── css/
│   │   └── style.css    # 紫系カラーテーマ、アニメーション
│   └── js/
│       ├── timer.js     # PomodoroTimer クラス（タイマーロジック）
│       ├── renderer.js  # CircleRenderer クラス（SVG 描画）
│       └── api.js       # ApiClient クラス（Flask API 通信）
├── templates/
│   └── index.html       # メインページ（インライン JS 含む）
├── docs/                # ドキュメント
└── tests/
    ├── conftest.py      # pytest フィクスチャ
    ├── test_services.py
    ├── test_repositories.py
    ├── test_routes.py
    └── test_gamification.py
````

---

## バックエンド レイヤー構成

````
[ Flask Routes (app.py) ]
        ↓ 呼び出し
[ Service Layer (services.py) ]   ← ビジネスロジックの中心
   ├── PomodoroService             セッション記録・今日の集計
   └── GamificationService         XP・レベル・ストリーク・バッジ算出
        ↓ 依存注入（DI）
[ Repository Layer (repositories.py) ]
   └── SessionRepository
        ↓
[ SQLite (models.py / SQLAlchemy) ]
   └── Session テーブル
````

### App Factory パターン

`create_app(config=None)` でアプリを生成する。テスト時は `TestConfig` を渡すことでインメモリ SQLite を使用する。

````python
def create_app(config=None):
    app = Flask(__name__)
    app.config.from_object(config or Config)
    db.init_app(app)
    with app.app_context():
        db.create_all()
    # ルート定義 ...
    return app
````

### 依存注入（DI）

`PomodoroService` と `GamificationService` はいずれも `repo` 引数を省略可能。省略時は `SessionRepository()` を自動生成する。これによりテスト時にモックリポジトリを差し替えることができる。

````python
class PomodoroService:
    def __init__(self, repo: SessionRepository | None = None):
        self.repo = repo or SessionRepository()
````

---

## フロントエンド 構成

### JavaScript クラス構成

| クラス           | ファイル        | 責務                                                |
|----------------|-------------|---------------------------------------------------|
| `PomodoroTimer`  | `timer.js`  | カウントダウン・フェーズ管理（DOM 非依存、コールバック方式） |
| `CircleRenderer` | `renderer.js`| SVG 円形プログレスバー描画・フェーズラベル表示・波紋エフェクト |
| `ApiClient`      | `api.js`    | Flask API との非同期通信（fetch）                   |

### データフロー

````
[ユーザー操作]
    ↓ 開始ボタン
[PomodoroTimer.start()]
    ↓ onTick コールバック（毎秒）
[CircleRenderer.update()]  → SVG リング・タイマー表示を更新
    ↓ onPhaseChange コールバック（フェーズ切り替え時）
[CircleRenderer.setPhaseLabel()]  → フェーズラベル更新・波紋エフェクト切替
    ↓ onComplete コールバック（作業フェーズ完了時）
[ApiClient.postSession()]  → POST /api/sessions
[ApiClient.getTodayStats()] → GET /api/sessions/today → 今日の進捗を表示
[ApiClient.getGamification()] → GET /api/gamification → XP/レベル/バッジを表示
````

---

## テスト戦略

| テストファイル              | 対象                    | 手法                             |
|--------------------------|------------------------|--------------------------------|
| `test_services.py`       | `PomodoroService`      | `unittest.mock` でリポジトリをモック |
| `test_gamification.py`   | `GamificationService`  | `unittest.mock` でリポジトリをモック |
| `test_repositories.py`   | `SessionRepository`    | インメモリ SQLite（`TestConfig`）   |
| `test_routes.py`         | HTTP エンドポイント       | Flask test client                |

---

## 採用技術

| 区分         | 技術                     |
|------------|------------------------|
| バックエンド  | Python / Flask          |
| ORM        | SQLAlchemy (Flask-SQLAlchemy) |
| DB         | SQLite                  |
| フロントエンド | HTML / CSS / Vanilla JS |
| テスト       | pytest / unittest.mock  |
