"""RAG 엔진 테스트 - TDD 선행 작성

'왜 무계인가' 질문에 괭생이모자반 자원화 기술을 근거로 답변하는 로직 검증
"""
import pytest

from src.chatbot.rag_engine import RAGEngine, Document


@pytest.fixture
def engine():
    docs = [
        Document(
            content="해양환경공단(KOEM)과 무계 상사가 괭생이모자반 자원화 협약을 체결했다.",
            source="news",
            tags=["ESG", "괭생이모자반"],
            priority=2,
        ),
        Document(
            content="탈염 및 열분해 공정을 통해 괭생이모자반을 친환경 비료 원료로 전환한다.",
            source="news",
            tags=["ESG", "괭생이모자반", "기술력"],
            priority=2,
        ),
        Document(
            content="무계 상사는 1992년 설립, ISO 9001 인증 보유 농업 전문 기업이다.",
            source="homepage",
            tags=["회사정보"],
            priority=1,
        ),
        Document(
            content="하늘천은 N-P-K 12-4-6 고함량 유기질비료로 4無 공법이 적용되었다.",
            source="brochure",
            tags=["제품", "4無공법"],
            priority=3,
        ),
        Document(
            content="해유기1호는 괭생이모자반 원료 기반 해양 유기질비료이다.",
            source="brochure",
            tags=["제품", "괭생이모자반"],
            priority=3,
        ),
    ]
    return RAGEngine(documents=docs)


class TestRAGEngine:
    def test_retrieve_by_keyword(self, engine):
        """키워드 기반으로 관련 문서를 검색할 수 있어야 한다."""
        results = engine.retrieve("괭생이모자반")
        assert len(results) >= 2
        assert all("괭생이모자반" in doc.content for doc in results)

    def test_retrieve_respects_priority(self, engine):
        """검색 결과가 데이터 우선순위(homepage > news > brochure) 순으로 정렬되어야 한다."""
        results = engine.retrieve("무계")
        priorities = [doc.priority for doc in results]
        assert priorities == sorted(priorities)

    def test_retrieve_top_k(self, engine):
        """top_k 파라미터로 반환 문서 수를 제한할 수 있어야 한다."""
        results = engine.retrieve("괭생이모자반", top_k=2)
        assert len(results) <= 2

    def test_retrieve_no_results(self, engine):
        """매칭 문서가 없으면 빈 리스트를 반환해야 한다."""
        results = engine.retrieve("존재하지않는키워드xyz")
        assert results == []

    def test_retrieve_by_tag(self, engine):
        """태그 기반으로 문서를 필터링할 수 있어야 한다."""
        results = engine.retrieve_by_tag("ESG")
        assert len(results) >= 2
        assert all("ESG" in doc.tags for doc in results)

    def test_build_context_for_why_muge(self, engine):
        """'왜 무계인가' 질문에 대한 컨텍스트를 구성할 수 있어야 한다."""
        context = engine.build_context("왜 무계 상사를 선택해야 하나요?")
        assert "괭생이모자반" in context
        assert "탈염" in context or "열분해" in context

    def test_build_context_includes_product(self, engine):
        """제품 관련 질문에는 제품 정보가 컨텍스트에 포함되어야 한다."""
        context = engine.build_context("하늘천 비료 성분이 뭔가요?")
        assert "하늘천" in context
        assert "N-P-K" in context

    def test_build_context_for_esg(self, engine):
        """ESG 관련 질문에는 자원화 기술 정보가 포함되어야 한다."""
        context = engine.build_context("무계 상사의 ESG 경영에 대해 알려주세요")
        assert "KOEM" in context or "해양환경공단" in context

    def test_intent_detection_why_muge(self, engine):
        """'왜 무계인가' 의도를 감지할 수 있어야 한다."""
        assert engine.detect_intent("무계 상사가 다른 회사랑 뭐가 다른가요?") == "why_muge"
        assert engine.detect_intent("왜 무계를 써야 하죠?") == "why_muge"

    def test_intent_detection_product(self, engine):
        """제품 문의 의도를 감지할 수 있어야 한다."""
        assert engine.detect_intent("하늘천 성분 알려주세요") == "product"
        assert engine.detect_intent("따지 비료 어디서 사나요") == "product"

    def test_intent_detection_general(self, engine):
        """일반 질문 의도를 감지할 수 있어야 한다."""
        assert engine.detect_intent("안녕하세요") == "general"
