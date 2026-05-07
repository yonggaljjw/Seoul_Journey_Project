import asyncio
import json
from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import Trip
from app.utils import build_user_summary, build_weather_context, clean_json_text
from app.services import search_public_data_candidates
from agent.client import generate_travel_plan

bp = Blueprint("trip", __name__, url_prefix="/api")

@bp.route("/trips", methods=["POST", "OPTIONS"])
def save_trip():
    if request.method == "OPTIONS":
        return jsonify({"success": True}), 200
    try:
        data = request.get_json() or {}
        new_trip = Trip(
            user_id=data.get("user_id"),
            title=data.get("title"),
            query_text=data.get("query_text"),
            merged_query=data.get("merged_query"),
            travel_type=data.get("travel_type"),
            duration=data.get("duration"),
            budget=data.get("budget"),
            result=data.get("result"),
            weather=data.get("weather"),
            public_data_candidates=data.get("public_data_candidates"),
        )
        db.session.add(new_trip)
        db.session.commit()
        return jsonify({"success": True, "trip_id": new_trip.id}), 201
    except Exception as e:
        return jsonify({"success": False, "message": "여행 저장 중 오류가 발생했습니다.", "error": str(e)}), 500

@bp.route("/trips/<int:user_id>", methods=["GET"])
def get_trips(user_id):
    try:
        trips = Trip.query.filter_by(user_id=user_id).order_by(Trip.created_at.desc()).all()
        result = []
        for t in trips:
            result.append({
                "id": t.id,
                "title": t.title,
                "query_text": t.query_text,
                "travel_type": t.travel_type,
                "duration": t.duration,
                "budget": t.budget,
                "created_at": t.created_at.strftime("%Y-%m-%d %H:%M"),
            })
        return jsonify({"success": True, "trips": result}), 200
    except Exception as e:
        return jsonify({"success": False, "message": "보관함 조회 중 오류가 발생했습니다.", "error": str(e)}), 500

@bp.route("/trip/<int:trip_id>", methods=["GET"])
def get_trip_detail(trip_id):
    try:
        t = Trip.query.get(trip_id)
        if not t:
            return jsonify({"success": False, "message": "여행 정보를 찾을 수 없습니다."}), 404
        return jsonify({
            "success": True,
            "trip": {
                "id": t.id,
                "title": t.title,
                "result": t.result,
                "weather": t.weather,
                "public_data_candidates": t.public_data_candidates,
                "created_at": t.created_at.strftime("%Y-%m-%d %H:%M"),
            }
        }), 200
    except Exception as e:
        return jsonify({"success": False, "message": "상세 조회 중 오류가 발생했습니다.", "error": str(e)}), 500

@bp.route("/recommend", methods=["POST"])
def recommend():
    try:
        data = request.get_json() or {}

        query_text = (data.get("query_text") or "").strip()
        selected_tags = data.get("selected_tags") or []
        selected_themes = data.get("selected_themes") or []

        if not query_text and not selected_tags and not selected_themes:
            return jsonify({
                "success": False,
                "message": "취향 입력 또는 태그/테마 중 하나 이상은 필요합니다."
            }), 400

        user_input = build_user_summary(data)
        weather_context = build_weather_context(data)
        public_data_candidates = search_public_data_candidates(user_input, weather_context)

        raw_text = asyncio.run(generate_travel_plan(data))
        cleaned_text = clean_json_text(raw_text)

        try:
            result = json.loads(cleaned_text)
        except json.JSONDecodeError:
            return jsonify({
                "success": False,
                "message": "모델 응답을 JSON으로 해석하지 못했습니다.",
                "raw_response": raw_text
            }), 500

        return jsonify({
            "success": True,
            "message": "추천 생성 완료",
            "input": user_input,
            "weather": weather_context,
            "public_data_candidates": public_data_candidates,
            "result": result
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": "추천 생성 중 오류가 발생했습니다.",
            "error": str(e)
        }), 500