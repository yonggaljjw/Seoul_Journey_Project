from flask import Flask, jsonify
from sqlalchemy import create_engine
from app.config import Config
from app.extensions import db, cors
import app.extensions as ext

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # 확장 모듈 초기화
    db.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    
    # Raw DB Engine 초기화 (앱 컨텍스트와 무관하게 동작하는 순수 sqlalchemy 엔진)
    ext.rawdata_engine = create_engine(
        app.config["RAWDATA_DB_URI"],
        pool_pre_ping=True,
        pool_recycle=3600,
    )

    # Blueprint(라우트) 등록
    from app.routes.auth import bp as auth_bp
    from app.routes.trip import bp as trip_bp
    from app.routes.raw import bp as raw_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(trip_bp)
    app.register_blueprint(raw_bp)

    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({"success": True, "message": "backend is running"}), 200

    return app