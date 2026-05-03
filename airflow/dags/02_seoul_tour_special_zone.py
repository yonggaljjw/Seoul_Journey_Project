from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime
import os
import pandas as pd
# requests는 여기서 직접 안 쓰인다면 제외해도 되지만 유지했습니다.
import requests 
from seoul_api import get_engine, fetch_page

# 임시 파일 저장 경로 (Airflow 워커 컨테이너 내부)
TEMP_DATA_PATH = "/tmp/seoul_tours_special_zone.csv"

# -----------------------------
# Extract
# -----------------------------
def extract(**context):
    API_KEY = os.getenv("SEOUL_API_KEY")
    SERVICE_NAME = "SebcTourZoneKor"
    BASE_URL = "http://openapi.seoul.go.kr:8088"

    # 1. 첫 요청
    first_body = fetch_page(BASE_URL, API_KEY, SERVICE_NAME, 1, 1000)
    total_count = int(first_body["list_total_count"])
    rows = first_body.get("row", [])

    # 2. 전체 데이터 수집
    for start in range(1001, total_count + 1, 1000):
        end = min(start + 999, total_count)
        body = fetch_page(BASE_URL, API_KEY, SERVICE_NAME, start, end)
        rows.extend(body.get("row", []))

    df = pd.DataFrame(rows)

    # XCom 대신 로컬 파일로 저장 (DB 뻗음 방지)
    df.to_csv(TEMP_DATA_PATH, index=False)
    print(f"Data extracted and saved to {TEMP_DATA_PATH}")

# -----------------------------
# Transform
# -----------------------------
def transform(**context):
    # 파일에서 데이터 읽기
    df = pd.read_csv(TEMP_DATA_PATH)

    # 1. MAIN_KEY 컬럼이 결측치인 행 제거 (DB NOT NULL 에러 방지)
    if 'MAIN_KEY' in df.columns:
        original_count = len(df)
        df = df.dropna(subset=['MAIN_KEY'])
        dropped_count = original_count - len(df)
        if dropped_count > 0:
            print(f"Dropped {dropped_count} rows due to missing MAIN_KEY.")

    # 2. 덮어쓰기 저장
    df.to_csv(TEMP_DATA_PATH, index=False)
    print("Data transformed successfully.")

# -----------------------------
# Load
# -----------------------------
def load(**context):
    # 파일에서 처리된 데이터 읽기
    df = pd.read_csv(TEMP_DATA_PATH)
    engine = get_engine()

    # CSV에서 읽어오면서 생긴 NaN 값을 DB 적재를 위해 None(NULL)으로 최종 변환
    df = df.where(pd.notnull(df), None)

    df.to_sql(
        name="SEOUL_TOUR_SPECIAL_ZONE",
        con=engine,
        if_exists="append",
        index=False,
        method="multi",
        chunksize=1000
    )
    
    # 적재 완료 후 임시 파일 삭제 (용량 확보)
    if os.path.exists(TEMP_DATA_PATH):
        os.remove(TEMP_DATA_PATH)
    print("Data loaded and temporary file cleaned up.")

# -----------------------------
# DAG 정의
# -----------------------------
with DAG(
    dag_id="SEOUL_TOUR_SPECIAL_ZONE",
    start_date=datetime(2026, 4, 1),
    schedule="@daily",
    catchup=False,
) as dag:

    extract_task = PythonOperator(
        task_id="extract",
        python_callable=extract,
    )

    transform_task = PythonOperator(
        task_id="transform",
        python_callable=transform,
    )

    load_task = PythonOperator(
        task_id="load",
        python_callable=load,
    )

    extract_task >> transform_task >> load_task