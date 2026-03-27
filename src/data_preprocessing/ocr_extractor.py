"""쿠팡/네이버 쇼핑 브로셔 이미지 OCR 추출 및 JSON 정형화 모듈"""
import json
import re
from pathlib import Path
from PIL import Image
import pytesseract


# 무계 상사 주력 제품 목록 (TechSpec 기준)
KNOWN_PRODUCTS = ["하늘천", "따지", "해유기1호", "해유기"]

NPK_PATTERN = re.compile(r"N-P-K[:\s]*(\d+)-(\d+)-(\d+)")
VOLUME_PATTERN = re.compile(r"용량[:\s]*([\d.]+\s*kg)", re.IGNORECASE)


class BrochureOCRExtractor:
    """쇼핑 브로셔 이미지에서 제품 정보를 추출하여 JSON으로 정형화한다."""

    def extract_text(self, image_path: Path) -> str:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, lang="kor+eng")
        return text.strip()

    def parse_product_info(self, raw_text: str) -> dict:
        product = {"name": "", "npk": {}, "volume": "", "raw_text": raw_text}

        for name in KNOWN_PRODUCTS:
            if name in raw_text:
                product["name"] = name
                break

        npk_match = NPK_PATTERN.search(raw_text)
        if npk_match:
            product["npk"] = {
                "N": int(npk_match.group(1)),
                "P": int(npk_match.group(2)),
                "K": int(npk_match.group(3)),
            }

        vol_match = VOLUME_PATTERN.search(raw_text)
        if vol_match:
            product["volume"] = vol_match.group(1).replace(" ", "")

        return product

    def to_json(self, product_data: dict) -> str:
        return json.dumps(product_data, ensure_ascii=False, indent=2)

    def process_directory(self, dir_path: Path) -> list[dict]:
        results = []
        extensions = (".png", ".jpg", ".jpeg", ".bmp", ".tiff")
        for img_file in sorted(dir_path.iterdir()):
            if img_file.suffix.lower() in extensions:
                text = self.extract_text(img_file)
                product = self.parse_product_info(text)
                product["source_file"] = img_file.name
                results.append(product)
        return results
