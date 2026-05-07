import requests
from flask import Blueprint, request, jsonify
from app.utils import build_user_summary, build_weather_context
from app.services import search_public_data_candidates

bp = Blueprint("raw", __name__, url_prefix="/api")

@bp.route("/raw/candidates", methods=["POST"])
def raw_candidates():
    try:
        data = request.get_json() or {}
        user_input = build_user_summary(data)
        weather_context = build_weather_context(data)
        candidates = search_public_data_candidates(user_input, weather_context)
        return jsonify({
            "success": True,
            "input": user_input,
            "weather": weather_context,
            "candidates": candidates,
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "공공데이터 후보 조회 중 오류가 발생했습니다.",
            "error": str(e),
        }), 500

@bp.route("/weather-preview", methods=["POST"])
def weather_preview():
    try:
        data = request.get_json() or {}
        weather_context = build_weather_context(data)
        return jsonify({"success": True, "weather": weather_context}), 200
    except requests.RequestException as e:
        return jsonify({"success": False, "message": "날씨 정보를 불러오는 중 오류가 발생했습니다.", "error": str(e)}), 500
    except Exception as e:
        return jsonify({"success": False, "message": "날씨 미리보기 생성 중 오류가 발생했습니다.", "error": str(e)}), 500