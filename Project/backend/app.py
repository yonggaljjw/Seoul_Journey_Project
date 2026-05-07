import asyncio
from datetime import datetime, date
from decimal import Decimal
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.engine import URL
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv
import os
import json
import re
import html
import requests

# 에이전트 실행 함수 임포트
from agent.client import generate_travel_plan

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# =========================================================
# 1. main DB: 사용자, 여행 보관함 저장용
# =========================================================
app.config["SQLALCHEMY_DATABASE_URI"] = URL.create(
    drivername="mysql+pymysql",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT", 3306)),
    database="main",
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# =========================================================
# 2. rawdata DB: 서울 공공데이터 조회용 (프론트/기타 API용 유지)
# =========================================================
rawdata_db_uri = URL.create(
    drivername="mysql+pymysql",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT", 3306)),
    database="rawdata",
)

rawdata_engine = create_engine(
    rawdata_db_uri,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# =========================================================
# 3. main DB Models
# =========================================================
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
    public_data_candidates = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# =========================================================
# 4. 기본 상수
# =========================================================
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
    "연남": {"name": "Yeonnam-dong, Seoul", "latitude": 37.5627, "longitude": 126.9251},
    "명동": {"name": "Myeong-dong, Seoul", "latitude": 37.5636, "longitude": 126.9834},
    "강남": {"name": "Gangnam, Seoul", "latitude": 37.4979, "longitude": 127.0276},
    "잠실": {"name": "Jamsil, Seoul", "latitude": 37.5133, "longitude": 127.1002},
    "여의도": {"name": "Yeouido, Seoul", "latitude": 37.5219, "longitude": 126.9245},
    "서울숲": {"name": "Seoul Forest, Seoul", "latitude": 37.5444, "longitude": 127.0374},
    "익선동": {"name": "Ikseon-dong, Seoul", "latitude": 37.5743, "longitude": 126.9893},
    "북촌": {"name": "Bukchon, Seoul", "latitude": 37.5826, "longitude": 126.9830},
    "한강": {"name": "Han River, Seoul", "latitude": 37.5284, "longitude": 126.9327},
    "광화문": {"name": "Gwanghwamun, Seoul", "latitude": 37.5759, "longitude": 126.9768},
    "종로": {"name": "Jongno, Seoul", "latitude": 37.5704, "longitude": 126.9921},
    "동대문": {"name": "Dongdaemun, Seoul", "latitude": 37.5665, "longitude": 127.0090},
    "DDP": {"name": "Dongdaemun Design Plaza, Seoul", "latitude": 37.5665, "longitude": 127.0090},
    "이태원": {"name": "Itaewon, Seoul", "latitude": 37.5345, "longitude": 126.9946},
    "압구정": {"name": "Apgujeong, Seoul", "latitude": 37.5271, "longitude": 127.0286},
    "코엑스": {"name": "COEX, Seoul", "latitude": 37.5116, "longitude": 127.0594},
}

AREA_TO_DISTRICT = {
    "성수": "성동구",
    "서울숲": "성동구",
    "홍대": "마포구",
    "연남": "마포구",
    "명동": "중구",
    "동대문": "중구",
    "DDP": "중구",
    "강남": "강남구",
    "압구정": "강남구",
    "코엑스": "강남구",
    "잠실": "송파구",
    "여의도": "영등포구",
    "북촌": "종로구",
    "익선동": "종로구",
    "광화문": "종로구",
    "종로": "종로구",
    "한강": "광진구",
    "이태원": "용산구",
}

RAW_TABLES = {
    "food": "INDIVIDUAL_SERVICE_CHARGE",
    "attractions": "SEOUL_TOUR_ATTRACTIONS",
    "culture": "SEOUL_TOUR_CULTURE",
    "lodging": "SEOUL_TOUR_LODGING_LICENSE",
    "shopping": "SEOUL_TOUR_SHOPPING",
}

# =========================================================
# 5. 공통 유틸
# =========================================================
def clean_json_text(text_value: str) -> str:
    if not text_value:
        return ""
    text_value = text_value.strip()
    text_value = re.sub(r"^```json\s*", "", text_value, flags=re.IGNORECASE)
    text_value = re.sub(r"^```\s*", "", text_value)
    text_value = re.sub(r"\s*```$", "", text_value)
    return text_value.strip()

def sanitize_value(value):
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(value, date):
        return value.strftime("%Y-%m-%d")
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="ignore")
    if isinstance(value, str):
        value = html.unescape(value)
        value = re.sub(r"\s+", " ", value).strip()
        return value
    return value

def compact_row(row: dict, max_fields: int = 18) -> dict:
    cleaned = {}
    count = 0
    for key, value in row.items():
        value = sanitize_value(value)
        if value in [None, "", " ", "\n"]:
            continue
        cleaned[str(key)] = value
        count += 1
        if count >= max_fields:
            break
    return cleaned

def build_user_summary(data: dict) -> dict:
    selected_theme_titles = [
        THEME_MAP.get(theme_key, theme_key)
        for theme_key in data.get("selected_themes", [])
    ]
    return {
        "query_text": (data.get("query_text") or "").strip(),
        "merged_query": (data.get("merged_query") or "").strip(),
        "selected_tags": data.get("selected_tags", []),
        "selected_themes": selected_theme_titles,
        "travel_type": data.get("travel_type", "혼자 여행"),
        "duration": data.get("duration", "1일"),
        "budget": int(data.get("budget") or 70000),
    }

def extract_target_area(data: dict) -> str:
    query_text = (data.get("query_text") or "").strip()
    merged_query = (data.get("merged_query") or "").strip()
    selected_tags = data.get("selected_tags") or []
    merged = " ".join([query_text, merged_query] + selected_tags)
    for area in SEOUL_DISTRICT_COORDS.keys():
        if area in merged:
            return area
    return "서울"

def extract_target_district(area: str) -> str:
    return AREA_TO_DISTRICT.get(area, "")

def infer_theme_keywords(user_input: dict, weather_context: dict) -> list:
    merged = " ".join(
        [
            user_input.get("query_text", ""),
            user_input.get("merged_query", ""),
            " ".join(user_input.get("selected_tags", [])),
            " ".join(user_input.get("selected_themes", [])),
        ]
    )
    keywords = []
    if any(word in merged for word in ["쇼핑", "뷰티", "올리브영", "패션", "소품", "서점"]):
        keywords += ["쇼핑", "뷰티", "패션", "소품", "서점"]
    if any(word in merged for word in ["드라마", "한류", "촬영", "K-드라마", "선재", "겨울연가"]):
        keywords += ["Hallyu", "Filming", "드라마", "촬영", "한류"]
    if any(word in merged for word in ["K팝", "K-팝", "아이돌", "엔터", "케이팝", "팝업"]):
        keywords += ["K-pop", "K팝", "엔터", "팝업", "공연"]
    if any(word in merged for word in ["전시", "문화", "공연", "체험", "미술관", "박물관"]):
        keywords += ["전시", "문화", "공연", "체험", "Museum", "Gallery"]
    if any(word in merged for word in ["맛집", "밥", "식사", "카페", "로컬", "미식"]):
        keywords += ["한식", "카페", "음식", "김밥", "비빔밥", "돈가스", "냉면"]
    if any(word in merged for word in ["산책", "야경", "한강", "공원", "조용"]):
        keywords += ["산책", "야경", "공원", "Park", "Walk", "Night"]
    
    weather_summary = weather_context.get("weather_summary", {})
    if weather_summary.get("rain_risk") == "높음":
        keywords += ["실내", "전시", "쇼핑", "문화", "카페"]
    return list(dict.fromkeys([k for k in keywords if k]))

# =========================================================
# 6. 날씨
# =========================================================
def geocode_location(query: str):
    url = "[https://geocoding-api.open-meteo.com/v1/search](https://geocoding-api.open-meteo.com/v1/search)"
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
    url = "[https://api.open-meteo.com/v1/forecast](https://api.open-meteo.com/v1/forecast)"
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
        "target_district": extract_target_district(area),
        "resolved_location": location,
        "weather_summary": weather_summary,
    }

# =========================================================
# 7. rawdata DB 조회 함수 (프론트/기타 API 응답용)
# =========================================================
def get_table_columns(table_name: str) -> list:
    inspector = inspect(rawdata_engine)
    columns = inspector.get_columns(table_name)
    return [col["name"] for col in columns]

def get_text_columns(table_name: str) -> list:
    inspector = inspect(rawdata_engine)
    columns = inspector.get_columns(table_name)
    text_columns = []
    for col in columns:
        col_type = str(col.get("type", "")).lower()
        if any(t in col_type for t in ["char", "text", "varchar", "longtext", "mediumtext"]):
            text_columns.append(col["name"])
    return text_columns

def search_table_by_keywords(table_name: str, keywords: list, limit: int = 8, only_active: bool = False) -> list:
    keywords = [k for k in keywords if k]
    text_columns = get_text_columns(table_name)
    if not text_columns:
        return []

    concat_expr = "CONCAT_WS(' ', " + ", ".join([f"`{c}`" for c in text_columns]) + ")"
    where_parts = []
    params = {}

    for idx, keyword in enumerate(keywords):
        param_name = f"kw{idx}"
        where_parts.append(f"{concat_expr} LIKE :{param_name}")
        params[param_name] = f"%{keyword}%"

    where_clause = " OR ".join(where_parts) if where_parts else "1=1"
    active_clause = ""
    if only_active:
        active_clause = f" AND {concat_expr} LIKE :active_kw"
        params["active_kw"] = "%영업중%"

    sql = text(f"""
        SELECT *
        FROM `{table_name}`
        WHERE ({where_clause})
        {active_clause}
        LIMIT :limit
    """)
    params["limit"] = limit

    with rawdata_engine.connect() as conn:
        rows = conn.execute(sql, params).mappings().all()

    return [compact_row(dict(row)) for row in rows]

def search_food_candidates(area: str, district: str, user_input: dict, limit: int = 10) -> list:
    table_name = RAW_TABLES["food"]
    base_keywords = []
    if district:
        base_keywords.append(district)
    if area and area != "서울":
        base_keywords.append(area)

    merged = " ".join([
        user_input.get("query_text", ""),
        user_input.get("merged_query", ""),
        " ".join(user_input.get("selected_tags", [])),
        " ".join(user_input.get("selected_themes", [])),
    ])
    food_words = ["김밥", "비빔밥", "돈가스", "냉면", "한식", "카페", "식사", "맛집", "조리라면", "김치찌개", "된장찌개"]
    if any(word in merged for word in ["저예산", "가성비", "싸게", "혼자"]):
        food_words = ["김밥", "비빔밥", "조리라면", "김치찌개", "된장찌개", "돈가스"]
    keywords = base_keywords + food_words
    return search_table_by_keywords(table_name, keywords, limit=limit)

def search_public_data_candidates(user_input: dict, weather_context: dict) -> dict:
    area = weather_context.get("target_area") or "서울"
    district = weather_context.get("target_district") or extract_target_district(area)
    theme_keywords = infer_theme_keywords(user_input, weather_context)

    area_keywords = []
    if area and area != "서울":
        area_keywords.append(area)
    if district:
        area_keywords.append(district)
    general_keywords = list(dict.fromkeys(area_keywords + theme_keywords))
    if not general_keywords:
        general_keywords = ["서울"]

    weather_mode = weather_context.get("weather_summary", {}).get("recommendation_mode", "")
    rain_risk = weather_context.get("weather_summary", {}).get("rain_risk", "")

    attraction_limit = 8 if rain_risk != "높음" else 4
    culture_limit = 8 if rain_risk == "높음" else 6
    shopping_limit = 8 if any(k in general_keywords for k in ["쇼핑", "뷰티", "패션", "소품"]) or rain_risk == "높음" else 5

    candidates = {
        "area": area,
        "district": district,
        "weather_mode": weather_mode,
        "attractions": search_table_by_keywords(
            RAW_TABLES["attractions"], general_keywords, limit=attraction_limit,
        ),
        "culture": search_table_by_keywords(
            RAW_TABLES["culture"], general_keywords + ["전시", "문화", "체험", "공연"], limit=culture_limit,
        ),
        "shopping": search_table_by_keywords(
            RAW_TABLES["shopping"], general_keywords + ["쇼핑", "서점", "소품", "패션"], limit=shopping_limit,
        ),
        "food": search_food_candidates(
            area=area, district=district, user_input=user_input, limit=10,
        ),
        "lodging": [],
    }

    duration = str(user_input.get("duration", ""))
    if any(word in duration for word in ["박", "2일", "3일", "숙박"]):
        candidates["lodging"] = search_table_by_keywords(
            RAW_TABLES["lodging"], area_keywords + ["영업중", "호스텔", "호텔", "관광숙박업"], limit=6, only_active=True,
        )
    return candidates

# =========================================================
# 8. API
# =========================================================
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"success": True, "message": "backend is running"}), 200

@app.route("/api/raw/candidates", methods=["POST"])
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
            public_data_candidates=data.get("public_data_candidates"),
        )
        db.session.add(new_trip)
        db.session.commit()
        return jsonify({"success": True, "trip_id": new_trip.id}), 201
    except Exception as e:
        return jsonify({"success": False, "message": "여행 저장 중 오류가 발생했습니다.", "error": str(e)}), 500

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
        return jsonify({"success": False, "message": "보관함 조회 중 오류가 발생했습니다.", "error": str(e)}), 500

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
                "public_data_candidates": t.public_data_candidates,
                "created_at": t.created_at.strftime("%Y-%m-%d %H:%M"),
            }
        }), 200
    except Exception as e:
        return jsonify({"success": False, "message": "상세 조회 중 오류가 발생했습니다.", "error": str(e)}), 500

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

# =========================================================
# 9. MCP Agent를 활용한 여행 코스 추천 API
# =========================================================
@app.route("/api/recommend", methods=["POST"])
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

        # 프론트엔드 응답을 위해 기존 정보 준비
        user_input = build_user_summary(data)
        weather_context = build_weather_context(data)
        public_data_candidates = search_public_data_candidates(user_input, weather_context)

        # Agent 비동기 호출을 동기적으로 실행
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

# =========================================================
# 10. 실행
# =========================================================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0", port=5000)