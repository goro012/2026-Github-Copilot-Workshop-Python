from flask import Flask, jsonify, render_template, request

from config import Config
from models import db
from services import PomodoroService


def create_app(config=None):
    app = Flask(__name__)
    app.config.from_object(config or Config)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/api/sessions", methods=["POST"])
    def create_session():
        data = request.get_json(silent=True) or {}
        duration = data.get("duration")
        if not isinstance(duration, int):
            return jsonify({"error": "duration must be an integer"}), 400
        try:
            result = PomodoroService().complete_session(duration)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        return jsonify(result), 201

    @app.route("/api/sessions/today", methods=["GET"])
    def today_sessions():
        stats = PomodoroService().get_today_stats()
        return jsonify(stats)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
