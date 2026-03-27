"""무계 상사 제품별 핵심 셀링 포인트 매핑 테이블


TechSpec 기준 데이터 소스: 쿠팡/네이버 쇼핑 브로셔 기반
주요 강조점: 타사 대비 높은 N-P-K 함량, 4無 공법
"""

FOUR_MU = ["무항생제", "무염분", "무가스", "무취"]

PRODUCT_TABLE = [
    {
        "name": "하늘천",
        "category": "유기질비료",
        "npk": {"N": 12, "P": 4, "K": 6},
        "volume": "20kg",
        "four_mu": FOUR_MU,
        "selling_points": [
            "업계 최고 수준 N-P-K 12-4-6 고함량 유기질비료",
            "4無 공법(무항생제/무염분/무가스/무취) 적용",
            "토양 미생물 활성화를 통한 지력 증진",
            "과수·채소·화훼 등 다목적 사용 가능",
        ],
        "target_crops": ["과수", "채소", "화훼", "수도작"],
        "shop_links": {
            "coupang": "https://www.coupang.com/vp/products/muge-hanulcheon",
            "naver": "https://smartstore.naver.com/muge/hanulcheon",
        },
    },
    {
        "name": "따지",
        "category": "유기질비료",
        "npk": {"N": 8, "P": 3, "K": 4},
        "volume": "20kg",
        "four_mu": FOUR_MU,
        "selling_points": [
            "균형 잡힌 N-P-K 8-3-4 배합 유기질비료",
            "4無 공법으로 안전한 친환경 재배 지원",
            "밑거름·웃거름 겸용 범용 비료",
            "토양 산도(pH) 개선 효과",
        ],
        "target_crops": ["노지채소", "시설채소", "과수"],
        "shop_links": {
            "coupang": "https://www.coupang.com/vp/products/muge-ddaji",
            "naver": "https://smartstore.naver.com/muge/ddaji",
        },
    },
    {
        "name": "해유기1호",
        "category": "유기질비료(해양부산물)",
        "npk": {"N": 5, "P": 3, "K": 2},
        "volume": "20kg",
        "four_mu": FOUR_MU,
        "selling_points": [
            "괭생이모자반 원료 기반 해양 유기질비료",
            "해양환경공단(KOEM) 협약 자원화 기술 적용",
            "탈염·열분해 공정으로 염분 제거 완료",
            "해양 미네랄 풍부, 작물 면역력 강화",
            "ESG 경영 실천 — 해양폐기물의 친환경 자원 순환",
        ],
        "target_crops": ["수도작", "과수", "채소", "특용작물"],
        "shop_links": {
            "coupang": "https://www.coupang.com/vp/products/muge-haeyugi",
            "naver": "https://smartstore.naver.com/muge/haeyugi",
        },
    },
]


class ProductCatalog:
    """무계 상사 제품 매핑 테이블 관리 클래스"""

    def __init__(self):
        self._products = {p["name"]: p for p in PRODUCT_TABLE}

    def list_product_names(self) -> list[str]:
        return list(self._products.keys())

    def get_product(self, name: str):
        return self._products.get(name)

    def get_comparison_table(self) -> list[dict]:
        return [
            {"name": p["name"], "category": p["category"], "npk": p["npk"]}
            for p in PRODUCT_TABLE
        ]

    def search(self, keyword: str) -> list[dict]:
        results = []
        for product in PRODUCT_TABLE:
            searchable = " ".join([
                product["name"],
                product["category"],
                " ".join(product["selling_points"]),
            ])
            if keyword in searchable:
                results.append(product)
        return results
