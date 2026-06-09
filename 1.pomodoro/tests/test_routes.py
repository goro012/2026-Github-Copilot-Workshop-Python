class TestIndexRoute:
    def test_GETルートが200を返す(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_レスポンスにHTMLが含まれる(self, client):
        response = client.get("/")
        assert b"timer-ring" in response.data


class TestCreateSession:
    def test_正常なdurationで201を返す(self, client):
        response = client.post("/api/sessions", json={"duration": 25})
        assert response.status_code == 201

    def test_レスポンスにidとdurationが含まれる(self, client):
        response = client.post("/api/sessions", json={"duration": 25})
        data = response.get_json()
        assert "id" in data
        assert data["duration"] == 25

    def test_負のdurationで400を返す(self, client):
        response = client.post("/api/sessions", json={"duration": -1})
        assert response.status_code == 400

    def test_duration_0で400を返す(self, client):
        response = client.post("/api/sessions", json={"duration": 0})
        assert response.status_code == 400

    def test_durationが文字列で400を返す(self, client):
        response = client.post("/api/sessions", json={"duration": "abc"})
        assert response.status_code == 400

    def test_durationなしで400を返す(self, client):
        response = client.post("/api/sessions", json={})
        assert response.status_code == 400

    def test_JSONなしで400を返す(self, client):
        response = client.post("/api/sessions")
        assert response.status_code == 400


class TestTodaySessions:
    def test_セッションなしで初期統計を返す(self, client):
        response = client.get("/api/sessions/today")
        assert response.status_code == 200
        data = response.get_json()
        assert data == {"completed": 0, "total_minutes": 0}

    def test_セッション追加後に統計が更新される(self, client):
        client.post("/api/sessions", json={"duration": 25})
        client.post("/api/sessions", json={"duration": 25})

        response = client.get("/api/sessions/today")
        data = response.get_json()
        assert data["completed"] == 2
        assert data["total_minutes"] == 50


class TestGamification:
    def test_ゲーミフィケーションエンドポイントが200を返す(self, client):
        response = client.get("/api/gamification")
        assert response.status_code == 200

    def test_レスポンスに必要なフィールドが含まれる(self, client):
        response = client.get("/api/gamification")
        data = response.get_json()
        assert "total_xp" in data
        assert "level" in data
        assert "xp_in_level" in data
        assert "xp_to_next_level" in data
        assert "xp_per_level" in data
        assert "streak" in data
        assert "badges" in data

    def test_セッションなしのとき初期値を返す(self, client):
        response = client.get("/api/gamification")
        data = response.get_json()
        assert data["total_xp"] == 0
        assert data["level"] == 1
        assert data["streak"] == 0
        assert data["badges"] == []

    def test_セッション追加後にXPが増える(self, client):
        client.post("/api/sessions", json={"duration": 25})

        response = client.get("/api/gamification")
        data = response.get_json()
        assert data["total_xp"] == 100
        assert data["xp_in_level"] == 100


class TestWeeklyStats:
    def test_週間統計エンドポイントが200を返す(self, client):
        response = client.get("/api/stats/weekly")
        assert response.status_code == 200

    def test_レスポンスに7日分のデータが含まれる(self, client):
        response = client.get("/api/stats/weekly")
        data = response.get_json()
        assert len(data["days"]) == 7
        assert "total_completed" in data
        assert "total_minutes" in data


class TestMonthlyStats:
    def test_月間統計エンドポイントが200を返す(self, client):
        response = client.get("/api/stats/monthly")
        assert response.status_code == 200

    def test_レスポンスに30日分のデータが含まれる(self, client):
        response = client.get("/api/stats/monthly")
        data = response.get_json()
        assert len(data["days"]) == 30
        assert "total_completed" in data
        assert "total_minutes" in data
