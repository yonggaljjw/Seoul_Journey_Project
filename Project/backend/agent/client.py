import os
import sys
import json
import traceback
from dotenv import load_dotenv

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_mcp_adapters.prompts import load_mcp_prompt
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

load_dotenv()

model = ChatOpenAI(
    model='gpt-4o',
    temperature=0.2,
)

server_params = StdioServerParameters(
    command=sys.executable,
    args=["-m", "agent.server"],
    env=dict(os.environ)
)

async def generate_travel_plan(user_data: dict) -> str:
    """app.py에서 호출하여 MCP 에이전트를 실행하는 래퍼 함수"""
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                tools = await load_mcp_tools(session)
                agent = create_react_agent(model, tools)

                message_str = json.dumps(user_data, ensure_ascii=False)

                prompts = await load_mcp_prompt(
                    session,
                    "travel_planner_prompt",
                    arguments={"message": f"다음 사용자 입력 및 요청을 바탕으로 여행 코스를 짜줘:\n{message_str}"},
                )

                response = await agent.ainvoke({"messages": prompts})
                return response["messages"][-1].content

    except Exception as e:
        print("\n" + "="*40)
        print("🚨 [MCP Agent 작동 중 치명적 오류 발생] 🚨")
        traceback.print_exc()
        
        if hasattr(e, 'exceptions'):
            for i, sub_e in enumerate(e.exceptions):
                print(f"  👉 Sub-Exception {i+1}: {type(sub_e).__name__} - {sub_e}")
        print("="*40 + "\n")
        
        fallback_response = {
            "summary": "여행 코스를 생성하는 도중 내부 서버 오류가 발생했습니다.",
            "travel_style": "오류 발생",
            "public_data_usage": "데이터를 불러오지 못했습니다.",
            "itinerary": [],
            "total_estimated_cost": 0,
            "budget_comment": "에러로 인해 계산 불가",
            "tips": ["잠시 후 다시 시도해주세요. (서버 로그를 확인하세요)"],
            "alternative_plan": []
        }
        return json.dumps(fallback_response, ensure_ascii=False)