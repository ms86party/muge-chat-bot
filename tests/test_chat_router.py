"""상담 워크플로우 분기 라우터 테스트 - TDD 선행 작성"""
import pytest

from src.chatbot.chat_router import ChatRouter, ChatResponse


@pytest.fixture
def router():
    return ChatRouter()


class TestChatRouter:
    # === 시나리오 분류 ===
    def test_route_faq(self, router):
        """일반 FAQ 질문을 faq 시나리오로 분류해야 한다."""
        assert router.classify("영업시간이 어떻게 되나요?") == "faq"
        assert router.classify("회사 주소 알려주세요") == "faq"
        assert router.classify("전화번호가 뭐예요?") == "faq"

    def test_route_product_consult(self, router):
        """제품 상담 질문을 product 시나리오로 분류해야 한다."""
        assert router.classify("하늘천 성분이 뭔가요?") == "product"
        assert router.classify("고추에 맞는 비료 추천해주세요") == "product"

    def test_route_tech_consult(self, router):
        """기술 상담을 tech 시나리오로 분류해야 한다."""
        assert router.classify("괭생이모자반 탈염 공정이 궁금합니다") == "tech"
        assert router.classify("ESG 경영 전략에 대해 알려주세요") == "tech"

    def test_route_human_transfer(self, router):
        """상담원 연결 요청을 human 시나리오로 분류해야 한다."""
        assert router.classify("상담원 연결해주세요") == "human"
        assert router.classify("사람과 통화하고 싶어요") == "human"
        assert router.classify("담당자 바꿔주세요") == "human"

    def test_route_purchase(self, router):
        """구매 관련 질문을 purchase 시나리오로 분류해야 한다."""
        assert router.classify("하늘천 어디서 구매하나요?") == "purchase"
        assert router.classify("주문하고 싶습니다") == "purchase"

    def test_route_greeting(self, router):
        """인사를 greeting 시나리오로 분류해야 한다."""
        assert router.classify("안녕하세요") == "greeting"

    # === 응답 생성 ===
    def test_handle_greeting(self, router):
        """인사에 브랜드 톤의 인사말을 반환해야 한다."""
        resp = router.handle("안녕하세요")
        assert resp.scenario == "greeting"
        assert "무계 상사" in resp.message

    def test_handle_faq_returns_answer(self, router):
        """FAQ 질문에 미리 등록된 답변을 반환해야 한다."""
        resp = router.handle("회사 주소 알려주세요")
        assert resp.scenario == "faq"
        assert len(resp.message) > 10

    def test_handle_human_transfer(self, router):
        """상담원 전환 시 안내 메시지와 transfer 플래그를 반환해야 한다."""
        resp = router.handle("상담원 연결해주세요")
        assert resp.scenario == "human"
        assert resp.transfer is True
        assert "상담" in resp.message

    def test_handle_purchase_includes_link(self, router):
        """구매 문의에 쇼핑몰 링크 안내가 포함되어야 한다."""
        resp = router.handle("하늘천 구매하고 싶어요")
        assert resp.scenario == "purchase"
        assert "coupang" in resp.message.lower() or "naver" in resp.message.lower() or "쇼핑" in resp.message

    def test_handle_returns_chat_response(self, router):
        """모든 응답이 ChatResponse 객체여야 한다."""
        resp = router.handle("아무 질문")
        assert isinstance(resp, ChatResponse)
        assert hasattr(resp, "scenario")
        assert hasattr(resp, "message")
        assert hasattr(resp, "transfer")

    def test_handle_tech_includes_context(self, router):
        """기술 상담 응답에 needs_rag 플래그가 True여야 한다."""
        resp = router.handle("괭생이모자반 자원화 기술 설명해주세요")
        assert resp.scenario == "tech"
        assert resp.needs_rag is True
