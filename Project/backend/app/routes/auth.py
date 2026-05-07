from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db
from app.models import User

bp = Blueprint("auth", __name__, url_prefix="/api/auth")

@bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = (data.get("password") or "").strip()

    if not name or not email or not password:
        return jsonify({"success": False, "message": "이름, 이메일, 비밀번호를 모두 입력해주세요."}), 400
    if len(password) < 8:
        return jsonify({"success": False, "message": "비밀번호는 8자 이상이어야 합니다."}), 400

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"success": False, "message": "이미 가입된 이메일입니다."}), 409

    password_hash = generate_password_hash(password)
    new_user = User(name=name, email=email, password_hash=password_hash)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "회원가입이 완료되었습니다.",
        "user": {"id": new_user.id, "name": new_user.name, "email": new_user.email}
    }), 201

@bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = (data.get("password") or "").strip()

    if not email or not password:
        return jsonify({"success": False, "message": "이메일과 비밀번호를 입력해주세요."}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"success": False, "message": "가입되지 않은 이메일입니다."}), 404
    if not check_password_hash(user.password_hash, password):
        return jsonify({"success": False, "message": "비밀번호가 올바르지 않습니다."}), 401

    return jsonify({
        "success": True,
        "message": "로그인에 성공했습니다.",
        "user": {"id": user.id, "name": user.name, "email": user.email}
    }), 200