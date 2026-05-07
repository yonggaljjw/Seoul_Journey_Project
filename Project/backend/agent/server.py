import os
import json
from typing import Optional, Literal
import app.extensions as ext
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base

from app.config import Config
from app.constants import RAW_TABLES
from app.utils import build_weather_context, build_user_summary
from app.services import (
    search_table_by_keywords,
    search_food_candidates as app_search_food,
    search_public_data_candidates as app_search_public
)

load_dotenv()

mcp = FastMCP("SeoulTravelPlanner")

# DB 엔진 연결
rawdata_db_uri = URL.create(
    drivername="mysql+pymysql",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT", "3306")),
    database=os.getenv("DB_NAME", "rawdata"),
)
ext.rawdata_engine = create_engine(
    Config.RAWDATA_DB_URI,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# =========================================================
# 5. MCP Tools
# =========================================================

@mcp.tool()
def summarize_user_input(
    query_text: str,
    merged_query: str = "",
    selected_tags: Optional[list[str]] = None,
    selected_themes: Optional[list[str]] = None,
    travel_type: str = "혼자 여행",
    duration: str = "1일",
    budget: int = 70000,
) -> dict:
    """사용자의 여행 요청을 여행 추천에 필요한 표준 입력 형태로 정리한다."""
    data = {
        "query_text": query_text,
        "merged_query": merged_query,
        "selected_tags": selected_tags or [],
        "selected_themes": selected_themes or [],
        "travel_type": travel_type,
        "duration": duration,
        "budget": budget,
    }
    # utils.py의 실제 함수 호출
    return build_user_summary(data)


@mcp.tool()
def get_weather_context(
    query_text: str,
    merged_query: str = "",
    selected_tags: Optional[list[str]] = None,
) -> dict:
    """사용자 질의에서 서울 내 대상 지역을 추출하고, 날씨와 여행 추천 모드를 반환한다."""
    data = {
        "query_text": query_text,
        "merged_query": merged_query,
        "selected_tags": selected_tags or [],
    }
    return build_weather_context(data)


@mcp.tool()
def search_table_candidates(
    table_key: Literal["food", "attractions", "culture", "shopping", "lodging"],
    keywords: list[str],
    limit: int = 8,
    only_active: bool = False,
) -> list[dict]:
    """서울시 rawdata DB의 허용된 테이블에서 키워드 기반 후보를 조회한다."""
    table_name = RAW_TABLES[table_key]

    return search_table_by_keywords(
        table_name=table_name,
        keywords=keywords,
        limit=limit,
        only_active=only_active,
    )


@mcp.tool()
def search_food_candidates(
    query_text: str,
    area: str = "서울",
    district: str = "",
    merged_query: str = "",
    selected_tags: Optional[list[str]] = None,
    selected_themes: Optional[list[str]] = None,
    limit: int = 10,
) -> list[dict]:
    """서울시 개인서비스요금 데이터에서 음식/식사/카페 후보를 조회한다."""
    user_input = {
        "query_text": query_text,
        "merged_query": merged_query,
        "selected_tags": selected_tags or [],
        "selected_themes": selected_themes or [],
    }
    # services.py의 실제 함수 호출
    return app_search_food(area=area, district=district, user_input=user_input, limit=limit)


@mcp.tool()
def search_public_data_candidates(
    query_text: str,
    merged_query: str = "",
    selected_tags: Optional[list[str]] = None,
    selected_themes: Optional[list[str]] = None,
    travel_type: str = "혼자 여행",
    duration: str = "1일",
    budget: int = 70000,
    weather_context: Optional[dict] = None,
) -> dict:
    """사용자 입력과 날씨 정보를 기반으로 서울시 공공데이터 여행 후보를 통합 조회한다."""
    user_data = {
        "query_text": query_text,
        "merged_query": merged_query,
        "selected_tags": selected_tags or [],
        "selected_themes": selected_themes or [],
        "travel_type": travel_type,
        "duration": duration,
        "budget": budget,
    }
    
    user_input = build_user_summary(user_data)
    if weather_context is None:
        weather_context = build_weather_context(user_data)

    return app_search_public(user_input=user_input, weather_context=weather_context)


@mcp.tool()
def build_travel_planning_context(
    query_text: str,
    merged_query: str = "",
    selected_tags: Optional[list[str]] = None,
    selected_themes: Optional[list[str]] = None,
    travel_type: str = "혼자 여행",
    duration: str = "1일",
    budget: int = 70000,
) -> dict:
    """서울 여행 추천에 필요한 사용자 입력, 날씨, 공공데이터 후보를 한 번에 구성한다."""
    user_data = {
        "query_text": query_text,
        "merged_query": merged_query,
        "selected_tags": selected_tags or [],
        "selected_themes": selected_themes or [],
        "travel_type": travel_type,
        "duration": duration,
        "budget": budget,
    }
    
    user_input = build_user_summary(user_data)
    weather_context = build_weather_context(user_data)
    public_data_candidates = app_search_public(user_input, weather_context)

    return {
        "user_input": user_input,
        "weather_context": weather_context,
        "public_data_candidates": public_data_candidates,
    }


@mcp.tool()
def validate_budget(
    itinerary: list[dict],
    budget: int,
) -> dict:
    """생성된 여행 itinerary의 총 예상 비용이 사용자 예산을 초과하는지 검증한다."""
    estimated_total = 0
    for item in itinerary:
        try:
            estimated_total += int(item.get("estimated_cost", 0) or 0)
        except Exception:
            continue

    return {
        "estimated_total": estimated_total,
        "budget": budget,
        "remaining_budget": budget - estimated_total,
        "is_within_budget": estimated_total <= budget,
    }

# =========================================================
# 6. MCP Prompt
# =========================================================

@mcp.prompt()
def travel_planner_prompt(message: str) -> list[base.Message]:
    json_format = """{
  "summary": "전체 코스 한 줄 요약",
  "travel_style": "사용자 여행 스타일 해석",
  "public_data_usage": "공공데이터를 어떻게 활용했는지 한 문장",
  "itinerary": [
    {
      "time": "11:00",
      "title": "장소/구간 이름",
      "category": "관광/문화/쇼핑/식사/카페/야경/숙박 등",
      "source_table": "활용한 테이블명 또는 일반 추천",
      "reason": "왜 이 장소가 사용자와 날씨, 예산에 맞는지",
      "estimated_cost": 12000,
      "tips": "간단 팁"
    }
  ],
  "total_estimated_cost": 0,
  "budget_comment": "예산 설명",
  "tips": ["팁 1", "팁 2"],
  "alternative_plan": [
    {
      "time": "15:00",
      "title": "대체 장소/구간",
      "category": "실내 대체/저예산 대체/쇼핑 대체 등",
      "source_table": "활용한 테이블명 또는 일반 추천",
      "reason": "대체 이유",
      "estimated_cost": 10000,
      "tips": "간단 팁"
    }
  ]
}"""
    return [
        base.AssistantMessage(
            "너는 서울 로컬 여행 코스를 설계하는 AI 플래너다. "
            "반드시 MCP tool을 사용하여(특히 build_travel_planning_context 또는 search_public_data_candidates) "
            "서울 공공데이터 후보를 조회하고 우선 활용해야 한다. "
            "후보 데이터에 없는 장소를 완전히 지어내지 말고, 부족할 때만 일반적인 구간명으로 보완하라. "
            "예산을 초과하지 말고, 날씨 정보에 따라 실내/야외 비중을 조정하라. "
            f"최종 결과는 반드시 다음 JSON 형식으로만 응답해야 하며, 마크다운 기호를 제외한 순수 JSON만 반환해:\n{json_format}"
        ),
        base.UserMessage(message),
    ]

if __name__ == "__main__":
    mcp.run(transport="stdio")