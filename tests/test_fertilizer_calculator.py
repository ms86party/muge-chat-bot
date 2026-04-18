"""작물별 권장 시비량 계산 로직 테스트 - TDD 선행 작성"""
import pytest

from src.chatbot.fertilizer_calculator import FertilizerCalculator


@pytest.fixture
def calc():
    return FertilizerCalculator()


class TestFertilizerCalculator:
    def test_supported_crops(self, calc):
        """주요 작물이 지원 목록에 있어야 한다."""
        crops = calc.list_supported_crops()
        assert "벼" in crops
        assert "고추" in crops
        assert "사과" in crops

    def test_get_crop_requirement(self, calc):
        """작물별 표준 요구량(kg/10a)을 반환해야 한다."""
        req = calc.get_crop_requirement("벼")
        assert "N" in req and "P" in req and "K" in req
        assert all(v > 0 for v in req.values())

    def test_crop_not_found(self, calc):
        """지원하지 않는 작물은 None을 반환해야 한다."""
        assert calc.get_crop_requirement("바오밥나무") is None

    def test_calculate_for_hanulcheon(self, calc):
        """하늘천 기준 벼 재배 시비량을 계산할 수 있어야 한다."""
        result = calc.calculate("벼", "하늘천", area_pyeong=300)
        assert "product" in result
        assert "crop" in result
        assert "recommended_kg" in result
        assert result["recommended_kg"] > 0

    def test_calculate_for_ddaji(self, calc):
        """따지 기준 고추 재배 시비량을 계산할 수 있어야 한다."""
        result = calc.calculate("고추", "따지", area_pyeong=300)
        assert result["recommended_kg"] > 0
        assert result["product"] == "따지"

    def test_calculate_for_haeyugi(self, calc):
        """해유기1호 기준 시비량을 계산할 수 있어야 한다."""
        result = calc.calculate("사과", "해유기1호", area_pyeong=300)
        assert result["recommended_kg"] > 0

    def test_calculate_includes_guide_text(self, calc):
        """계산 결과에 시비 가이드 안내 문구가 포함되어야 한다."""
        result = calc.calculate("벼", "하늘천", area_pyeong=300)
        assert "guide" in result
        assert len(result["guide"]) > 10

    def test_area_conversion(self, calc):
        """평(坪) → 10a(1000㎡) 변환이 정확해야 한다."""
        # 300평 ≈ 991.7㎡ ≈ 약 0.99 × 10a
        assert abs(calc.pyeong_to_10a(300) - 0.9917) < 0.01

    def test_different_area_scales_result(self, calc):
        """면적이 2배면 시비량도 2배여야 한다 (반올림 오차 1kg 이내)."""
        r1 = calc.calculate("벼", "하늘천", area_pyeong=300)
        r2 = calc.calculate("벼", "하늘천", area_pyeong=600)
        assert abs(r2["recommended_kg"] - r1["recommended_kg"] * 2) < 1.0

    def test_unknown_product_raises(self, calc):
        """등록되지 않은 제품이면 ValueError를 발생시켜야 한다."""
        with pytest.raises(ValueError):
            calc.calculate("벼", "없는비료", area_pyeong=300)
