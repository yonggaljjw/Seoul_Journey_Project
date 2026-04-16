from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime
import os
import pandas as pd
import requests
from seoul_api import get_engine, fetch_page

# 임시 파일 저장 경로 (Airflow 워커 컨테이너 내부)
TEMP_DATA_PATH = "/tmp/seoul_tours_raw.csv"

# -----------------------------
# Extract
# -----------------------------
def extract(**context):
    API_KEY = os.getenv("SEOUL_API_KEY")
    SERVICE_NAME = "TbVwAttractions"
    BASE_URL = "http://openapi.seoul.go.kr:8088"

    # 1. 첫 요청
    first_body = fetch_page(BASE_URL, API_KEY, SERVICE_NAME, 1, 1000)
    total_count = int(first_body["list_total_count"])
    rows = first_body.get("row", [])

    # 2. 전체 데이터 수집 (인자 개수 수정!)

    for start in range(1001, total_count + 1, 1000):
        end = min(start + 999, total_count)
        body = fetch_page(BASE_URL, API_KEY, SERVICE_NAME, start, end)
        rows.extend(body.get("row", []))

    df = pd.DataFrame(rows)

    # 3. 컬럼명 변환 (DDL 맞춤)
    df = df.rename(columns={
        "POST_SN": "post_sn",
        "LANG_CODE_ID": "lang_code_id",
        "POST_SJ": "post_sj",
        "POST_URL": "post_url",
        "ADDRESS": "address",
        "NEW_ADDRESS": "new_address",
        "CMMN_TELNO": "cmmn_telno",
        "CMMN_FAX": "cmmn_fax",
        "CMMN_HMPG_URL": "cmmn_hmpg_url",
        "CMMN_USE_TIME": "cmmn_use_time",
        "CMMN_BSNDE": "cmmn_bsnde",
        "CMMN_RSTDE": "cmmn_rstde",
        "SUBWAY_INFO": "subway_info",
        "TAG": "tag",
        "BF_DESC": "bf_desc",
    })

    # 필요한 컬럼만 선택
    df = df[[
        "post_sn", "lang_code_id", "post_sj", "post_url",
        "address", "new_address", "cmmn_telno", "cmmn_fax",
        "cmmn_hmpg_url", "cmmn_use_time", "cmmn_bsnde",
        "cmmn_rstde", "subway_info", "tag", "bf_desc"
    ]]

    # XCom 대신 로컬 파일로 저장 (DB 뻗음 방지)
    df.to_csv(TEMP_DATA_PATH, index=False)
    print(f"Data extracted and saved to {TEMP_DATA_PATH}")

# -----------------------------
# Transform
# -----------------------------
def transform(**context):
    # 파일에서 데이터 읽기
    df = pd.read_csv(TEMP_DATA_PATH)

    # NULL 처리
    df = df.where(pd.notnull(df), None)

    # 타입 변환
    df["post_sn"] = df["post_sn"].astype("int64")

    # 문자열 길이 제한 (DDL 보호)
    df["post_sj"] = df["post_sj"].str.slice(0, 255)
    df["post_url"] = df["post_url"].str.slice(0, 500)

    # 중복 제거
    df = df.drop_duplicates(subset=["post_sn"])

    # 다시 덮어쓰기 저장
    df.to_csv(TEMP_DATA_PATH, index=False)
    print("Data transformed successfully.")

# -----------------------------
# Load
# -----------------------------
def load(**context):
    # 파일에서 처리된 데이터 읽기
    df = pd.read_csv(TEMP_DATA_PATH)
    engine = get_engine()

    df.to_sql(
        name="SEOUL_TOUR_ATTRACTIONS",
        con=engine,
        if_exists="append",
        index=False,
        method="multi",
        chunksize=1000
    )
    
    # 적재 완료 후 임시 파일 삭제 (용량 확보)
    if os.path.exists(TEMP_DATA_PATH):
        os.remove(TEMP_DATA_PATH)

# -----------------------------
# DAG 정의
# -----------------------------
with DAG(
    dag_id="seoul_tour_api_to_mysql",
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