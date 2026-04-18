"""무계 상사 제품별 핵심 셀링 포인트 매핑 테이블

데이터 출처(우선순위): 공식 홈페이지(muge.co.kr) > 뉴스 > 쇼핑 브로셔
- N-P-K / 원료성분: 공식 홈페이지 시험성적서 기준
- 가격: 네이버쇼핑 가격비교(2026-04-18 수집) 기준
"""

FOUR_MU = ["무항생제", "무염분", "무가스", "무취"]

PRODUCT_TABLE = [
    {
        "name": "하늘천",
        "category": "혼합유기질 펠렛비료",
        "npk": {"N": 6, "P": 6, "K": 3.3},
        "organic_matter": 66,
        "volume": "20kg",
        "four_mu": [],
        "ingredients": "가공계분 50% / 하이프로틴(피마자박) 30% / 미강 20%",
        "certifications": ["ISO 9001", "ISO 14001", "특허 출원", "상표등록"],
        "official_price_krw": 17000,
        "shipping_krw": 5000,
        "selling_points": [
            "㈜무계상사 최고 명품 비료 (해유기 1호의 직속 후계 라인)",
            "N-P-K 6-6-3.3↑, 유기물 66%↑ 고함량",
            "가공계분(100% 발효)과 하이프로틴(피마자박)을 주원료로 성분함량 월등",
            "타비료의 1/2 사용으로 효과 배가, 1회 시비로 수확까지 지속",
            "토양 미생물 번식 활성화, 산성화 예방, 연작장해 해소",
        ],
        "target_crops": ["과수", "채소", "화훼", "수도작"],
        "shop_links": {
            "naver": "https://smartstore.naver.com/greenmuge (친환경기업무계상사)",
        },
    },
    {
        "name": "따지",
        "category": "혼합유박 펠렛비료",
        "npk": {"N": 5, "P": 2.5, "K": 1.5},
        "organic_matter": 80,
        "volume": "20kg (텃밭용 500g)",
        "four_mu": [],
        "ingredients": "피마자박 60% / 미강 20% / 채종유박 20%",
        "certifications": ["ISO 9001", "ISO 14001", "특허 출원", "상표등록", "친환경 자재 지정"],
        "official_price_krw": 15500,
        "shipping_krw": 0,
        "selling_points": [
            "유기물 80%↑ — 무계 라인 중 최고 유기물 함량",
            "작물별 N-P-K 최적 비율 배합, 밑거름·웃거름 겸용",
            "국립공원·산림조합 등 공공기관 납품 실적",
            "친환경 자재 지정 — 무농약·유기농 재배 가능",
            "냄새없는 비료 (피마자박+채종유박 기반)",
        ],
        "target_crops": ["노지채소", "시설채소", "과수", "텃밭"],
        "shop_links": {
            "naver": "https://smartstore.naver.com/greenmuge (친환경기업무계상사)",
            "coupang": "쿠팡 '무계바이오 WITH블럭 냄새없는 비료 따지유박' 검색",
        },
    },
    {
        "name": "금계",
        "category": "가공계분 유기질비료 (양계용)",
        "npk": {"N": 3, "P": 5.5, "K": 4.5},
        "organic_matter": 66,
        "volume": "20kg",
        "four_mu": [],
        "ingredients": "가공계분 80% / 미강 20%",
        "certifications": ["ISO 9001", "ISO 14001", "특허 출원", "상표등록"],
        "official_price_krw": None,
        "shipping_krw": None,
        "selling_points": [
            "단 한번의 1년 농사 충분 — 완효성 비료",
            "천연석회 다량 함유 → 생리장애 예방 · 토양개량 효과",
            "유기안산 풍부로 뿌리발달 촉진, 당도·색채 향상",
            "발효+수경작물·저온성장에 탁월한 완효성",
        ],
        "target_crops": ["뿌리작물", "영농작물", "과수"],
        "shop_links": {
            "direct": "본사 054-701-2999 또는 공식 직영 '친환경기업무계상사' 문의",
        },
    },
    {
        "name": "해유기1호",
        "category": "해양 유기질비료 (일본 JAS 인증)",
        "npk": {"N": 3, "P": 5.5, "K": 4.5},
        "organic_matter": 66,
        "volume": "소포장 / 20kg",
        "four_mu": FOUR_MU,
        "ingredients": "일본 수입 가공계분 100% / 낫토균 100% 발효 + E.M균 첨가",
        "certifications": ["일본 유기 JAS 인증", "4無 공법", "친환경 농축공시"],
        "official_price_krw": 2010,
        "shipping_krw": 3500,
        "selling_points": [
            "🏆 국내 유일 일본 유기 JAS 인증 보유",
            "4無 공법 — 무항생제/무염분/무가스/무취",
            "항균제 미사용 채란계분 → 고온살균 → 낫토균 100% 발효 숙성",
            "15년 전국 농민 베스트셀러 (2005년 국내 도입)",
            "E.M균 첨가 완효성 — 작물 생육·면역력 활성화",
            "KOEM 협약 기반 괭생이모자반 자원화 기술과 연계 (ESG)",
        ],
        "target_crops": ["수도작", "과수", "채소", "특용작물"],
        "shop_links": {
            "naver": "https://smartstore.naver.com/greenmuge (친환경기업무계상사)",
            "direct": "20kg 정식가 본사 054-701-2999 문의",
        },
    },
]

# 무계바이오 액상 라인업 (서브 브랜드)
LIQUID_PRODUCTS = [
    {"name": "폴코스", "volume": "1L", "min_price": 12620, "max_price": 15000,
     "use": "관주/토양개량/호르몬제"},
    {"name": "황소 4종복합", "volume": "1L", "min_price": 9500, "max_price": 18000,
     "use": "고급 식물 영양제 (공식 1+1 시 7,000원/병)"},
    {"name": "농축칼슘제", "volume": "1L", "min_price": 13500, "max_price": 15000,
     "use": "칼슘 공급, 생리장애 예방 (공식 1+1 시 7,500원/병)"},
    {"name": "스테비아 액비", "volume": "1L", "min_price": 13000, "max_price": 15000,
     "use": "당도 증대 (토마토 결실 특화)"},
    {"name": "유황복합", "volume": "1L", "min_price": 15000, "max_price": 18000,
     "use": "당도 증대"},
    {"name": "달달이 바이오", "volume": "5L", "min_price": 44000, "max_price": 47000,
     "use": "마늘·양파 특화 대용량 복합비료"},
]


class ProductCatalog:
    """무계 상사 제품 매핑 테이블 관리 클래스"""

    def __init__(self):
        self._products = {p["name"]: p for p in PRODUCT_TABLE}
        self._liquids = {p["name"]: p for p in LIQUID_PRODUCTS}

    def list_product_names(self) -> list[str]:
        return list(self._products.keys())

    def list_liquid_names(self) -> list[str]:
        return list(self._liquids.keys())

    def get_product(self, name: str):
        return self._products.get(name) or self._liquids.get(name)

    def get_comparison_table(self) -> list[dict]:
        return [
            {"name": p["name"], "category": p["category"], "npk": p["npk"],
             "organic_matter": p.get("organic_matter")}
            for p in PRODUCT_TABLE
        ]

    def search(self, keyword: str) -> list[dict]:
        results = []
        for product in PRODUCT_TABLE + LIQUID_PRODUCTS:
            searchable = " ".join([
                product.get("name", ""),
                product.get("category", ""),
                " ".join(product.get("selling_points", [])),
            ])
            if keyword in searchable:
                results.append(product)
        return results
