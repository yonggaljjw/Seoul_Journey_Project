import os
import requests
from sqlalchemy import create_engine

def fetch_page(BASE_URL, API_KEY, SERVICE_NAME, start: int, end: int, LANG_CODE_ID=None) -> dict:
    if LANG_CODE_ID :
        url = f"{BASE_URL}/{API_KEY}/json/{SERVICE_NAME}/{start}/{end}/{LANG_CODE_ID}"
    else :
        url = f"{BASE_URL}/{API_KEY}/json/{SERVICE_NAME}/{start}/{end}"
        
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    data = response.json()

    if SERVICE_NAME not in data:
        raise ValueError(f"응답 구조 오류: {data}")

    body = data[SERVICE_NAME]
    result = body.get("RESULT", {})

    if result.get("CODE") != "INFO-000":
        raise RuntimeError(f"API 오류: {result}")

    return body


def get_engine():
    return create_engine(
        f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}",
        echo=False
    )