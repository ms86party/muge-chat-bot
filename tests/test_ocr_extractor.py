"""OCR 브로셔 추출기 테스트 - TDD 선행 작성"""
import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from PIL import Image

from src.data_preprocessing.ocr_extractor import BrochureOCRExtractor


@pytest.fixture
def extractor():
    return BrochureOCRExtractor()


@pytest.fixture
def sample_image(tmp_path):
    """테스트용 더미 이미지 생성"""
    img = Image.new("RGB", (200, 100), color="white")
    path = tmp_path / "test_brochure.png"
    img.save(path)
    return path


class TestBrochureOCRExtractor:
    def test_extract_text_from_image(self, extractor, sample_image):
        """이미지에서 텍스트를 추출할 수 있어야 한다."""
        with patch("pytesseract.image_to_string", return_value="하늘천 N-P-K 12-4-6"):
            result = extractor.extract_text(sample_image)
            assert isinstance(result, str)
            assert len(result) > 0

    def test_parse_product_info_npk(self, extractor):
        """추출된 텍스트에서 N-P-K 성분 정보를 파싱해야 한다."""
        raw_text = "하늘천 유기질비료\nN-P-K: 12-4-6\n용량: 20kg"
        product = extractor.parse_product_info(raw_text)
        assert product["name"] == "하늘천"
        assert product["npk"] == {"N": 12, "P": 4, "K": 6}

    def test_parse_product_info_volume(self, extractor):
        """추출된 텍스트에서 용량 정보를 파싱해야 한다."""
        raw_text = "따지 유기질비료\nN-P-K: 8-3-4\n용량: 20kg"
        product = extractor.parse_product_info(raw_text)
        assert product["name"] == "따지"
        assert product["volume"] == "20kg"

    def test_to_json_format(self, extractor):
        """파싱 결과를 JSON 형식으로 직렬화할 수 있어야 한다."""
        product_data = {
            "name": "해유기1호",
            "npk": {"N": 5, "P": 3, "K": 2},
            "volume": "20kg",
            "source": "coupang",
        }
        json_str = extractor.to_json(product_data)
        parsed = json.loads(json_str)
        assert parsed["name"] == "해유기1호"
        assert parsed["npk"]["N"] == 5

    def test_process_brochure_directory(self, extractor, tmp_path):
        """디렉토리 내 모든 브로셔 이미지를 일괄 처리해야 한다."""
        for i in range(3):
            img = Image.new("RGB", (200, 100), color="white")
            img.save(tmp_path / f"brochure_{i}.png")

        with patch("pytesseract.image_to_string", return_value="하늘천\nN-P-K: 12-4-6\n용량: 20kg"):
            results = extractor.process_directory(tmp_path)
            assert len(results) == 3
            assert all(isinstance(r, dict) for r in results)
