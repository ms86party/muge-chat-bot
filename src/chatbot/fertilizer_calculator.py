"""작물별 권장 시비량 계산 모듈

농촌진흥청 표준 시비 기준(kg/10a)을 기반으로,
무계 상사 제품의 N-P-K 함량에 맞춰 권장 투입량을 산출한다.
"""

# 무계 상사 제품별 N-P-K 함량 (%, 공식 홈페이지 시험성적서 기준)
PRODUCT_NPK = {
    "하늘천": {"N": 6, "P": 6, "K": 3.3},
    "따지": {"N": 5, "P": 2.5, "K": 1.5},
    "금계": {"N": 3, "P": 5.5, "K": 4.5},
    "해유기1호": {"N": 3, "P": 5.5, "K": 4.5},
}

# 작물별 표준 시비 요구량 (kg/10a, 농촌진흥청 기준 참고)
CROP_REQUIREMENTS = {
    "벼": {"N": 9, "P": 4.5, "K": 5.7},
    "고추": {"N": 19, "P": 6.2, "K": 11.5},
    "배추": {"N": 32, "P": 7.8, "K": 19.9},
    "사과": {"N": 21, "P": 7.0, "K": 15.0},
    "감귤": {"N": 24, "P": 8.0, "K": 14.0},
    "포도": {"N": 16, "P": 6.5, "K": 12.0},
    "토마토": {"N": 20, "P": 8.0, "K": 15.0},
    "딸기": {"N": 12, "P": 5.0, "K": 8.0},
    "감자": {"N": 14, "P": 6.0, "K": 10.0},
    "마늘": {"N": 17, "P": 5.5, "K": 9.0},
}

PYEONG_TO_SQM = 3.3058


class FertilizerCalculator:
    """작물·제품·면적 기반 권장 시비량 계산기"""

    def list_supported_crops(self) -> list:
        return list(CROP_REQUIREMENTS.keys())

    def get_crop_requirement(self, crop: str):
        return CROP_REQUIREMENTS.get(crop)

    def pyeong_to_10a(self, pyeong: float) -> float:
        """평(坪)을 10a(1000㎡) 단위로 변환"""
        sqm = pyeong * PYEONG_TO_SQM
        return sqm / 1000.0

    def calculate(self, crop: str, product: str, area_pyeong: float) -> dict:
        if product not in PRODUCT_NPK:
            raise ValueError(f"등록되지 않은 제품: {product}")

        req = CROP_REQUIREMENTS.get(crop)
        if req is None:
            raise ValueError(f"지원하지 않는 작물: {crop}")

        npk = PRODUCT_NPK[product]
        area_10a = self.pyeong_to_10a(area_pyeong)

        # 질소(N) 기준으로 투입량 산출 (유기질비료 표준 계산법)
        # 제품 N% → 100kg당 N kg = npk["N"] kg
        # 필요 N = req["N"] * area_10a
        n_needed = req["N"] * area_10a
        recommended_kg = round(n_needed / (npk["N"] / 100), 1)

        guide = (
            f"{crop} 재배 시 {product}(N-P-K {npk['N']}-{npk['P']}-{npk['K']}) "
            f"기준 권장 시비량: {area_pyeong}평 면적에 약 {recommended_kg}kg을 "
            f"투입하시는 것을 권장합니다. "
            f"밑거름으로 전량의 60~70%를 시비하고, "
            f"나머지는 생육 상태를 보아 웃거름으로 추비해 주세요."
        )

        return {
            "crop": crop,
            "product": product,
            "area_pyeong": area_pyeong,
            "area_10a": round(area_10a, 4),
            "n_required_kg": round(n_needed, 2),
            "recommended_kg": recommended_kg,
            "guide": guide,
        }
