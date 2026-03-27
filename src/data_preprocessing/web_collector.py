"""공식 홈페이지 및 뉴스 기사 수집/태깅 모듈

데이터 우선순위 (CLAUDE.md 기준): 공식 홈페이지(1) > 뉴스(2) > 쇼핑 브로셔(3)
"""
import json
import re
from dataclasses import dataclass, field, asdict
from pathlib import Path
from html.parser import HTMLParser

import requests


# 태깅용 키워드 매핑
TAG_RULES = {
    "ESG": ["괭생이모자반", "자원화", "친환경", "탈염", "열분해", "해양폐기물", "ESG"],
    "괭생이모자반": ["괭생이모자반"],
    "제품": ["하늘천", "따지", "해유기", "유기질비료", "미생물제제", "N-P-K"],
    "4無공법": ["4無", "무항생제", "무염분", "무가스", "무취"],
    "회사정보": ["설립", "연혁", "ISO", "인증", "연구소", "무계 상사"],
    "기술력": ["연구소", "특허", "기술", "공법", "공정"],
    "수출": ["베트남", "캄보디아", "수출", "글로벌"],
}

SOURCE_PRIORITY = {"homepage": 1, "news": 2, "brochure": 3}


@dataclass
class TaggedDocument:
    content: str
    source: str
    tags: list = field(default_factory=list)
    priority: int = 3

    def to_dict(self) -> dict:
        return asdict(self)


class _HTMLTextExtractor(HTMLParser):
    """HTML에서 태그를 제거하고 텍스트만 추출한다."""

    def __init__(self):
        super().__init__()
        self._texts = []

    def handle_data(self, data):
        self._texts.append(data.strip())

    def get_text(self) -> str:
        return " ".join(t for t in self._texts if t)


class WebCollector:
    """공식 홈페이지 및 뉴스 기사를 수집하고 태깅한다."""

    def fetch_page(self, url: str) -> str:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text

    def extract_text(self, html: str) -> str:
        parser = _HTMLTextExtractor()
        parser.feed(html)
        return parser.get_text()

    def tag_document(self, text: str, source: str) -> TaggedDocument:
        tags = []
        for tag_name, keywords in TAG_RULES.items():
            if any(kw in text for kw in keywords):
                tags.append(tag_name)

        if not tags and source == "homepage":
            tags.append("회사정보")

        priority = SOURCE_PRIORITY.get(source, 3)
        return TaggedDocument(
            content=text, source=source, tags=tags, priority=priority
        )

    def save_documents(self, docs: list[TaggedDocument], path: Path) -> None:
        data = [doc.to_dict() for doc in docs]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
