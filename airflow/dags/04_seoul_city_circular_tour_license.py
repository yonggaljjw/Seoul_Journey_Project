from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime
import os
import pandas as pd
from seoul_api import get_engine, fetch_page

# 임시 파일 저장 경로
TEMP_DATA_PATH = "/tmp/seoul_city_circular_tour_license.csv"

# 날짜 컬럼
DATE_COLS = [
    "APVPERMYMD",
    "APVCANCELYMD",
    "DCBYMD",
    "CLGSTDT",
    "CLGENDDT",
    "INSURSTDT",
    "INSURENDDT",
]

# 날짜 + 시간 컬럼
DATETIME_COLS = [
    "LASTMODTS",
    "UPDATEDT",
]

# -----------------------------
# 공통 전처리 함수
# -----------------------------
def clean_for_mysql(df):
    df = df.copy()

    # 1. 문자열 공백 제거
    def clean_value(x):
        if pd.isna(x):
            return None

        if isinstance(x, str):
            x = x.strip()

            # 공백 문자열, 빈 문자열 처리
            if x == "":
                return None

        return x

    # pandas 버전에 따라 map / applymap 대응
    if hasattr(df, "map"):
        df = df.map(clean_value)
    else:
        df = df.applymap(clean_value)

    # 2. 날짜 컬럼 처리: 잘못된 날짜, 공백은 None
    for col in DATE_COLS:
        if col in df.columns:
            parsed = pd.to_datetime(df[col], errors="coerce")
            df[col] = parsed.dt.strftime("%Y-%m-%d")
            df.loc[parsed.isna(), col] = None

    # 3. 날짜시간 컬럼 처리
    for col in DATETIME_COLS:
        if col in df.columns:
            parsed = pd.to_datetime(df[col], errors="coerce")
            df[col] = parsed.dt.strftime("%Y-%m-%d %H:%M:%S")
            df.loc[parsed.isna(), col] = None

    # 4. X, Y 좌표 컬럼 숫자 처리
    for col in ["X", "Y"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            df[col] = df[col].where(pd.notnull(df[col]), None)

    return df


# -----------------------------
# Extract
# -----------------------------
def extract(**context):
    API_KEY = os.getenv("SEOUL_API_KEY")
    SERVICE_NAME = "LOCALDATA_030706"
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

    # CSV 저장
    df.to_csv(TEMP_DATA_PATH, index=False)
    print(f"Data extracted and saved to {TEMP_DATA_PATH}")


# -----------------------------
# Transform
# -----------------------------
def transform(**context):
    # dtype=str: 우편번호 03901 같은 값이 3901로 바뀌는 것 방지
    # keep_default_na=False: 빈 문자열을 임의로 NaN 처리하지 않고 직접 제어
    df = pd.read_csv(
        TEMP_DATA_PATH,
        dtype=str,
        keep_default_na=False
    )

    df = clean_for_mysql(df)

    # 다시 저장
    df.to_csv(TEMP_DATA_PATH, index=False)
    print("Data transformed successfully.")


# -----------------------------
# Load
# -----------------------------
def load(**context):
    df = pd.read_csv(
        TEMP_DATA_PATH,
        dtype=str,
        keep_default_na=False
    )

    # CSV를 다시 읽으면서 빈값이 문자열로 복원될 수 있으므로 한 번 더 안전 처리
    df = clean_for_mysql(df)

    engine = get_engine()

    df.to_sql(
        name="SEOUL_CITY_CIRCULAR_TOUR_LICENSE",
        con=engine,
        if_exists="append",
        index=False,
        method="multi",
        chunksize=1000
    )

    # 적재 완료 후 임시 파일 삭제
    if os.path.exists(TEMP_DATA_PATH):
        os.remove(TEMP_DATA_PATH)

    print("Data loaded successfully.")


# -----------------------------
# DAG 정의
# -----------------------------
with DAG(
    dag_id="SEOUL_CITY_CIRCULAR_TOUR_LICENSE",
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