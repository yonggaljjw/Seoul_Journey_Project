FROM apache/airflow:3.2.0-python3.12

USER airflow

# 추가 파이썬 패키지가 필요해지면 아래 두 줄만 활성화하면 됩니다.
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["airflow", "webserver"]