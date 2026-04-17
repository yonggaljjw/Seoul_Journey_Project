from datetime import datetime
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.engine import URL
from dotenv import load_dotenv
from openai import OpenAI
import os
import json
import re
import requests

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

app.config["SQLALCHEMY_DATABASE_URI"] = URL.create(
    drivername="mysql+pymysql",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT")),
    database="main",
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

client = None


def get_openai_client():
    global client
    if client is not None:
        return client

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    client = OpenAI(api_key=api_key)
    return client


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Trip(db.Model):
    __tablename__ = "trips"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(255))
    query_text = db.Column(db.Text)
    merged_query = db.Column(db.Text)
    travel_type = db.Column(db.String(50))
    duration = db.Column(db.String(50))
    budget = db.Column(db.Integer)
    result = db.Column(db.JSON)
    weather = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


THEME_MAP = {
    "drama": "K-드라마 감성",
    "kpop": "K-팝 & 트렌드",
    "food": "로컬 미식 탐방",
    "beauty": "뷰티 & 쇼핑",
    "walk": "조용한 산책",
}

SEOUL_DISTRICT_COORDS = {
    "성수": {"name": "Seongsu-dong, Seoul", "latitude": 37.5447, "longitude": 127.0557},
    "홍대": {"name": "Hongdae, Seoul", "latitude": 37.5563, "longitude": 126.9220},
    "명동": {"name": "Myeong-dong, Seoul", "latitude": 37.5636, "longitude": 126.9834},
    "강남": {"name": "Gangnam, Seoul", "latitude": 37.4979, "longitude": 127.0276},
    "잠실": {"name": "Jamsil, Seoul", "latitude": 37.5133, "longitude": 127.1002},
    "여의도": {"name": "Yeouido, Seoul", "latitude": 37.5219, "longitude": 126.9245},
    "서울숲": {"name": "Seoul Forest, Seoul", "latitude": 37.5444, "longitude": 127.0374},
    "익선동": {"name": "Ikseon-dong, Seoul", "latitude": 37.5743, "longitude": 126.9893},
    "북촌": {"name": "Bukchon, Seoul", "latitude": 37.5826, "longitude": 126.9830},
    "한강": {"name": "Han River, Seoul", "latitude": 37.5284, "longitude": 126.9327},
}


def clean_json_text(text: str) -> str:
    if not text:
        return ""
    text = text.strip()
    text = re.sub(r"^```json\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def build_user_summary(data: dict) -> dict:
    selected_theme_titles = [
        THEME_MAP.get(theme_key, theme_key)
        for theme_key in data.get("selected_themes", [])
    ]

    return {
        "query_text": (data.get("query_text") or "").strip(),
        "selected_tags": data.get("selected_tags", []),
        "selected_themes": selected_theme_titles,
        "travel_type": data.get("travel_type", "혼자 여행"),
        "duration": data.get("duration", "1일"),
        "budget": data.get("budget", 70000),
    }


def extract_target_area(data: dict) -> str:
    query_text = (data.get("query_text") or "").strip()
    selected_tags = data.get("selected_tags") or []
    merged = " ".join([query_text] + selected_tags)

    for area in SEOUL_DISTRICT_COORDS.keys():
        if area in merged:
            return area

    return "서울"


def geocode_location(query: str):
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": query, "count": 1, "language": "ko", "format": "json"}
    response = requests.get(url, params=params, timeout=8)
    response.raise_for_status()
    data = response.json()
    results = data.get("results") or []
    if not results:
        return None

    first = results[0]
    return {
        "name": first.get("name"),
        "latitude": first.get("latitude"),
        "longitude": first.get("longitude"),
        "country": first.get("country"),
        "admin1": first.get("admin1"),
    }


def resolve_location(area: str) -> dict:
    if area in SEOUL_DISTRICT_COORDS:
        return SEOUL_DISTRICT_COORDS[area]

    if area == "서울":
        return {"name": "Seoul", "latitude": 37.5665, "longitude": 126.9780}

    try:
        geo = geocode_location(f"{area}, Seoul")
        if geo:
            return geo
    except Exception:
        pass

    return {"name": "Seoul", "latitude": 37.5665, "longitude": 126.9780}


def fetch_weather(latitude: float, longitude: float) -> dict:
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "timezone": "Asia/Seoul",
        "current": "temperature_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m",
        "hourly": "temperature_2m,precipitation_probability,weather_code",
        "forecast_days": 1,
    }
    response = requests.get(url, params=params, timeout=8)
    response.raise_for_status()
    return response.json()


def summarize_weather(weather_data: dict) -> dict:
    current = weather_data.get("current", {})
    hourly = weather_data.get("hourly", {})

    precipitation_probs = hourly.get("precipitation_probability", [])[:12]
    temps = hourly.get("temperature_2m", [])[:12]

    max_pop = max(precipitation_probs) if precipitation_probs else 0
    max_temp = max(temps) if temps else current.get("temperature_2m")
    min_temp = min(temps) if temps else current.get("temperature_2m")

    current_temp = current.get("temperature_2m")
    apparent_temp = current.get("apparent_temperature")
    wind_speed = current.get("wind_speed_10m")
    weather_code = current.get("weather_code")

    rain_risk = "높음" if max_pop >= 60 else "보통" if max_pop >= 30 else "낮음"

    if max_pop >= 60:
        recommendation_mode = "실내 중심"
    elif current_temp is not None and current_temp >= 30:
        recommendation_mode = "실내 + 저녁 중심"
    elif current_temp is not None and current_temp <= 5:
        recommendation_mode = "짧은 야외 + 실내 중심"
    else:
        recommendation_mode = "야외 포함 가능"

    return {
        "current_temperature": current_temp,
        "apparent_temperature": apparent_temp,
        "wind_speed": wind_speed,
        "weather_code": weather_code,
        "max_precipitation_probability": max_pop,
        "max_temp_today": max_temp,
        "min_temp_today": min_temp,
        "rain_risk": rain_risk,
        "recommendation_mode": recommendation_mode,
    }


def build_weather_context(data: dict) -> dict:
    area = extract_target_area(data)
    location = resolve_location(area)
    weather_raw = fetch_weather(location["latitude"], location["longitude"])
    weather_summary = summarize_weather(weather_raw)

    return {
        "target_area": area,
        "resolved_location": location,
        "weather_summary": weather_summary,
    }


def build_prompt(user_input: dict, weather_context: dict) -> str:
    return f"""
너는 서울 로컬 여행 코스를 설계하는 AI 플래너다.

아래 사용자 입력과 날씨 정보를 반영해 서울 여행 코스를 추천하라.

규칙:
- 반드시 JSON만 반환
- 마크다운 금지
- 전체 일정은 2~4개 장소로 간결하게 구성
- 예산을 초과하지 않게 구성
- 강수확률이 높으면 실내 위주
- 더위/추위/강풍이 심하면 장시간 야외 일정 축소
- 설명은 짧고 명확하게 작성

반환 JSON:
{{
  "summary": "전체 코스 한 줄 요약",
  "travel_style": "사용자 여행 스타일 해석",
  "itinerary": [
    {{
      "time": "11:00",
      "title": "장소/구간 이름",
      "category": "카페/산책/쇼핑/식사/야경 등",
      "reason": "왜 이 장소가 사용자와 날씨에 맞는지",
      "estimated_cost": 12000,
      "tips": "간단 팁"
    }}
  ],
  "total_estimated_cost": 0,
  "budget_comment": "예산 설명",
  "tips": ["팁 1", "팁 2"],
  "alternative_plan": [
    {{
      "time": "15:00",
      "title": "대체 장소/구간",
      "category": "실내 대체",
      "reason": "대체 이유",
      "estimated_cost": 10000,
      "tips": "간단 팁"
    }}
  ]
}}

사용자 입력:
{json.dumps(user_input, ensure_ascii=False)}

날씨 정보:
{json.dumps(weather_context, ensure_ascii=False)}
""".strip()


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"success": True, "message": "backend is running"}), 200


@app.route("/api/trips", methods=["POST", "OPTIONS"])
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
        )

        db.session.add(new_trip)
        db.session.commit()

        return jsonify({
            "success": True,
            "trip_id": new_trip.id
        }), 201

    except Exception as e:
        return jsonify({
            "success": False,
            "message": "여행 저장 중 오류가 발생했습니다.",
            "error": str(e)
        }), 500


@app.route("/api/trips/<int:user_id>", methods=["GET"])
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
        return jsonify({
            "success": False,
            "message": "보관함 조회 중 오류가 발생했습니다.",
            "error": str(e)
        }), 500


@app.route("/api/trip/<int:trip_id>", methods=["GET"])
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
                "created_at": t.created_at.strftime("%Y-%m-%d %H:%M"),
            }
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "message": "상세 조회 중 오류가 발생했습니다.",
            "error": str(e)
        }), 500


@app.route("/api/weather-preview", methods=["POST"])
def weather_preview():
    try:
        data = request.get_json() or {}
        weather_context = build_weather_context(data)
        return jsonify({"success": True, "weather": weather_context}), 200
    except requests.RequestException as e:
        return jsonify({"success": False, "message": "날씨 정보를 불러오는 중 오류가 발생했습니다.", "error": str(e)}), 500
    except Exception as e:
        return jsonify({"success": False, "message": "날씨 미리보기 생성 중 오류가 발생했습니다.", "error": str(e)}), 500


@app.route("/api/auth/signup", methods=["POST"])
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


@app.route("/api/auth/login", methods=["POST"])
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


@app.route("/api/recommend", methods=["POST"])
def recommend():
    try:
        data = request.get_json() or {}

        query_text = (data.get("query_text") or "").strip()
        selected_tags = data.get("selected_tags") or []
        selected_themes = data.get("selected_themes") or []

        if not query_text and not selected_tags and not selected_themes:
            return jsonify({"success": False, "message": "취향 입력 또는 태그/테마 중 하나 이상은 필요합니다."}), 400

        client = get_openai_client()
        if not client:
            return jsonify({"success": False, "message": "OPENAI_API_KEY가 설정되어 있지 않습니다."}), 500

        user_input = build_user_summary(data)
        weather_context = build_weather_context(data)
        prompt = build_prompt(user_input, weather_context)

        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-5.4"),
            input=prompt,
            timeout=90,
        )

        raw_text = response.output_text
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
            "result": result
        }), 200

    except requests.RequestException as e:
        return jsonify({"success": False, "message": "날씨 정보를 불러오는 중 오류가 발생했습니다.", "error": str(e)}), 500
    except Exception as e:
        return jsonify({"success": False, "message": "추천 생성 중 오류가 발생했습니다.", "error": str(e)}), 500


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0", port=5000)