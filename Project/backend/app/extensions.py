from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

db = SQLAlchemy()
cors = CORS()

# rawdata DB 엔진 (create_app에서 초기화됨)
rawdata_engine = None