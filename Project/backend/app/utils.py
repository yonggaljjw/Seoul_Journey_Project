import re
import html
import requests
from datetime import datetime, date
from decimal import Decimal
from app.constants import THEME_MAP, SEOUL_DISTRICT_COORDS, AREA_TO_DISTRICT

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
        "target_district": extract_target_district(area),
        "resolved_location": location,
        "weather_summary": weather_summary,
    }