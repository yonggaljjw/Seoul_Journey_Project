THEME_MAP = {
    "drama": "K-드라마 감성",
    "kpop": "K-팝 & 트렌드",
    "food": "로컬 미식 탐방",
    "beauty": "뷰티 & 쇼핑",
    "walk": "조용한 산책",
}

SEOUL_DISTRICT_COORDS = {
    "성수": {"name": "Seongsu-dong, Seoul", "latitude": 37.5447, "longitude": 127.0557},
    "홍대": {"name": "Hongdae, Seoul", "latitude": 37.5563, "longitude": 126.9220},
    "연남": {"name": "Yeonnam-dong, Seoul", "latitude": 37.5627, "longitude": 126.9251},
    "명동": {"name": "Myeong-dong, Seoul", "latitude": 37.5636, "longitude": 126.9834},
    "강남": {"name": "Gangnam, Seoul", "latitude": 37.4979, "longitude": 127.0276},
    "잠실": {"name": "Jamsil, Seoul", "latitude": 37.5133, "longitude": 127.1002},
    "여의도": {"name": "Yeouido, Seoul", "latitude": 37.5219, "longitude": 126.9245},
    "서울숲": {"name": "Seoul Forest, Seoul", "latitude": 37.5444, "longitude": 127.0374},
    "익선동": {"name": "Ikseon-dong, Seoul", "latitude": 37.5743, "longitude": 126.9893},
    "북촌": {"name": "Bukchon, Seoul", "latitude": 37.5826, "longitude": 126.9830},
    "한강": {"name": "Han River, Seoul", "latitude": 37.5284, "longitude": 126.9327},
    "광화문": {"name": "Gwanghwamun, Seoul", "latitude": 37.5759, "longitude": 126.9768},
    "종로": {"name": "Jongno, Seoul", "latitude": 37.5704, "longitude": 126.9921},
    "동대문": {"name": "Dongdaemun, Seoul", "latitude": 37.5665, "longitude": 127.0090},
    "DDP": {"name": "Dongdaemun Design Plaza, Seoul", "latitude": 37.5665, "longitude": 127.0090},
    "이태원": {"name": "Itaewon, Seoul", "latitude": 37.5345, "longitude": 126.9946},
    "압구정": {"name": "Apgujeong, Seoul", "latitude": 37.5271, "longitude": 127.0286},
    "코엑스": {"name": "COEX, Seoul", "latitude": 37.5116, "longitude": 127.0594},
}

AREA_TO_DISTRICT = {
    "성수": "성동구",
    "서울숲": "성동구",
    "홍대": "마포구",
    "연남": "마포구",
    "명동": "중구",
    "동대문": "중구",
    "DDP": "중구",
    "강남": "강남구",
    "압구정": "강남구",
    "코엑스": "강남구",
    "잠실": "송파구",
    "여의도": "영등포구",
    "북촌": "종로구",
    "익선동": "종로구",
    "광화문": "종로구",
    "종로": "종로구",
    "한강": "광진구",
    "이태원": "용산구",
}

RAW_TABLES = {
    "food": "INDIVIDUAL_SERVICE_CHARGE",
    "attractions": "SEOUL_TOUR_ATTRACTIONS",
    "culture": "SEOUL_TOUR_CULTURE",
    "lodging": "SEOUL_TOUR_LODGING_LICENSE",
    "shopping": "SEOUL_TOUR_SHOPPING",
}