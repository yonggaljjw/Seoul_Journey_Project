from sqlalchemy import text, inspect
import app.extensions as ext
from app.constants import RAW_TABLES
from app.utils import compact_row, extract_target_district, infer_theme_keywords

def get_table_columns(table_name: str) -> list:
    inspector = inspect(ext.rawdata_engine)
    columns = inspector.get_columns(table_name)
    return [col["name"] for col in columns]

def get_text_columns(table_name: str) -> list:
    inspector = inspect(ext.rawdata_engine)
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

    with ext.rawdata_engine.connect() as conn:
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