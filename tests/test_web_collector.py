"""웹 데이터 수집 및 태깅 테스트 - TDD 선행 작성"""
import json
import pytest
from unittest.mock import patch, MagicMock

from src.data_preprocessing.web_collector import WebCollector, TaggedDocument


SAMPLE_HTML = """
<html><body>
<h1>무계 상사 회사 소개</h1>
<p>무계 상사는 1992년 설립되어 ISO 9001 인증을 보유한 농업 전문 기업입니다.</p>
<p>자체 연구소를 통해 유기질비료 및 미생물제제를 개발하고 있습니다.</p>
</body></html>
"""

SAMPLE_NEWS_HTML = """
<html><body>
<h1>해양환경공단-무계상사, 괭생이모자반 자원화 협약</h1>
<p>해양환경공단(KOEM)과 무계 상사가 괭생이모자반을 활용한 자원화 기술 협약을 체결했다.</p>
<p>탈염 및 열분해 공정을 통해 친환경 비료 원료로 전환하는 기술이 핵심이다.</p>
<span class="date">2024-11-15</span>
</body></html>
"""


@pytest.fixture
def collector():
    return WebCollector()


class TestWebCollector:
    def test_fetch_page_returns_html(self, collector):
        """URL에서 HTML을 가져올 수 있어야 한다."""
        mock_response = MagicMock()
        mock_response.text = SAMPLE_HTML
        mock_response.status_code = 200
        with patch("requests.get", return_value=mock_response):
            html = collector.fetch_page("https://muge.co.kr")
            assert "<h1>" in html

    def test_extract_text_from_html(self, collector):
        """HTML에서 본문 텍스트를 추출해야 한다."""
        text = collector.extract_text(SAMPLE_HTML)
        assert "무계 상사" in text
        assert "ISO 9001" in text
        assert "<h1>" not in text  # HTML 태그 제거 확인

    def test_tag_document_homepage(self, collector):
        """홈페이지 문서에 올바른 태그를 부여해야 한다."""
        text = "무계 상사는 ISO 9001 인증을 보유한 농업 전문 기업입니다."
        doc = collector.tag_document(text, source="homepage")
        assert doc.source == "homepage"
        assert "회사정보" in doc.tags
        assert doc.priority == 1  # 홈페이지 우선순위 최상

    def test_tag_document_news_esg(self, collector):
        """뉴스 기사에서 ESG/자원화 키워드를 태깅해야 한다."""
        text = "괭생이모자반을 활용한 탈염 및 열분해 공정으로 친환경 비료 원료 생산"
        doc = collector.tag_document(text, source="news")
        assert "ESG" in doc.tags
        assert "괭생이모자반" in doc.tags
        assert doc.priority == 2  # 뉴스 우선순위 2순위

    def test_tag_document_product_keywords(self, collector):
        """제품 관련 키워드가 있으면 제품 태그를 부여해야 한다."""
        text = "하늘천은 N-P-K 12-4-6 함량의 고품질 유기질비료입니다. 4無 공법 적용."
        doc = collector.tag_document(text, source="homepage")
        assert "제품" in doc.tags
        assert "4無공법" in doc.tags

    def test_tagged_document_to_dict(self, collector):
        """TaggedDocument를 딕셔너리로 변환할 수 있어야 한다."""
        text = "테스트 문서"
        doc = collector.tag_document(text, source="homepage")
        d = doc.to_dict()
        assert d["content"] == "테스트 문서"
        assert d["source"] == "homepage"
        assert isinstance(d["tags"], list)

    def test_collect_and_save(self, collector, tmp_path):
        """수집 결과를 JSON 파일로 저장할 수 있어야 한다."""
        docs = [
            TaggedDocument(content="문서1", source="homepage", tags=["회사정보"], priority=1),
            TaggedDocument(content="문서2", source="news", tags=["ESG"], priority=2),
        ]
        output_path = tmp_path / "collected.json"
        collector.save_documents(docs, output_path)
        with open(output_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert len(data) == 2
        assert data[0]["source"] == "homepage"
