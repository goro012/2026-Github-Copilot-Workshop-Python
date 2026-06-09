# アーキテクチャ概要

ポモドーロタイマー Web アプリケーションの現在の構成を説明します。

---

## 技術スタック

| 区分          | 技術                         |
|-------------|------------------------------|
| バックエンド  | Python / Flask               |
| ORM         | Flask-SQLAlchemy             |
| DB          | SQLite                       |
| フロントエンド | HTML / CSS / Vanilla JS      |
| テスト       | pytest / unittest.mock       |

---

## ディレクトリ構成

```
1.pomodoro/
├── app.py                   # create_app()（App Factory パターン）
├── config.py                # 環境別設定（Config / TestConfig）
├── models.py                # SQLAlchemy モデル定義（Session）
├── repositories.py          # DB アクセス層（SessionRepository）
├── services.py              # ビジネスロジック層（PomodoroService）
├── requirements.txt         # 依存パッケージ
├── static/
│   ├── css/
│   │   └── style.css        # 紫系グラデーションテーマ
│   └── js/
│       ├── timer.js         # PomodoroTimer クラス（タイマーロジック）
│       ├── renderer.js      # CircleRenderer クラス（SVG描画・エフェクト）
│       └── api.js           # ApiClient クラス（Flask API 通信）
├── templates/
│   └── index.html           # メインページ（インライン初期化スクリプト含む）
└── tests/
    ├── conftest.py          # pytest フィクスチャ（app, client, db）
    ├── test_services.py     # ビジネスロジックのテスト（モック使用）
    ├── test_repositories.py # DB 操作のテスト（インメモリ SQLite）
    └── test_routes.py       # HTTP エンドポイントのテスト（Flask test client）
```

---

## バックエンドレイヤー構成

```
[ Flask Routes (app.py) ]
        │  HTTP リクエスト受け取り・レスポンス返却
        ▼
[ Service Layer (services.py / PomodoroService) ]
        │  ビジネスロジック・バリデーション
        │  依存注入（DI）によりテスト時にモック差し替え可能
        ▼
[ Repository Layer (repositories.py / SessionRepository) ]
        │  DB アクセス抽象化
        ▼
[ SQLite (models.py / Session モデル) ]
```

### App Factory パターン

`app.py` の `create_app(config=None)` 関数でアプリケーションを生成します。  
テスト時は `TestConfig`（インメモリ SQLite）を注入することで、本番 DB への影響なしにテストを実行できます。

```python
# 本番起動
app = create_app()

# テスト時
app = create_app(TestConfig)
```

### 依存注入（DI）

`PomodoroService` はコンストラクタで `SessionRepository` を受け取ります。  
`None` を渡すと自動的にデフォルトのリポジトリが使用されます。

```python
class PomodoroService:
    def __init__(self, repo: SessionRepository | None = None):
        self.repo = repo or SessionRepository()
```

---

## フロントエンドデータフロー

```
ブラウザ（JS）
  │
  ├─ 開始ボタン押下 → PomodoroTimer.start()
  │                        │ 1秒ごとに onTick コールバック
  │                        ▼
  │                   CircleRenderer.update()  ← SVG 更新・時刻表示
  │
  ├─ タイマーゼロ → PomodoroTimer._advancePhase()
  │                        │ onComplete コールバック（作業フェーズのみ）
  │                        ▼
  │                   ApiClient.postSession(durationMinutes)
  │                        │ POST /api/sessions
  │                        ▼
  │                   ApiClient.getTodayStats()
  │                        │ GET /api/sessions/today
  │                        ▼
  │                   refreshStats() → stat-completed / stat-minutes 更新
  │
  └─ フェーズ切り替え → CircleRenderer.setPhaseLabel(phase)
                                │ フェーズラベル更新・波紋エフェクト制御
```

---

## フェーズ遷移

```
作業 (25分) → 短い休憩 (5分) → 作業 (25分) → ... (4回繰り返し)
                                                         ↓
                                                   長い休憩 (15分)
```

- 4ポモドーロ完了ごとに長い休憩へ遷移
- 休憩完了後は常に作業フェーズへ戻る

---

## テスト戦略

| テスト種別          | 対象ファイル              | 手法                               |
|------------------|------------------------|------------------------------------|
| ビジネスロジック    | `test_services.py`     | `unittest.mock` でリポジトリをモック  |
| DB 操作           | `test_repositories.py` | インメモリ SQLite（`TestConfig`）     |
| HTTP エンドポイント | `test_routes.py`       | Flask test client                  |

テスト実行コマンド:

```bash
cd 1.pomodoro
python -m pytest tests/
```
