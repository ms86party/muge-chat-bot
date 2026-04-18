"""브랜드 페르소나 및 시스템 프롬프트 테스트 - TDD 선행 작성"""
import pytest

from src.chatbot.persona import MugePersona


@pytest.fixture
def persona():
    return MugePersona()


class TestMugePersona:
    def test_system_prompt_not_empty(self, persona):
        """시스템 프롬프트가 비어있지 않아야 한다."""
        prompt = persona.get_system_prompt()
        assert len(prompt) > 100

    def test_system_prompt_contains_brand_identity(self, persona):
        """시스템 프롬프트에 브랜드 정체성 키워드가 포함되어야 한다."""
        prompt = persona.get_system_prompt()
        assert "무계상사" in prompt or "무계 상사" in prompt
        assert "기술 전략 실장" in prompt

    def test_system_prompt_contains_tone(self, persona):
        """전문적이고 자부심 있는 톤 지침이 포함되어야 한다."""
        prompt = persona.get_system_prompt()
        assert "농업 기술" in prompt

    def test_system_prompt_contains_four_mu(self, persona):
        """4無 공법 관련 지침이 포함되어야 한다."""
        prompt = persona.get_system_prompt()
        assert "4無" in prompt or "무항생제" in prompt

    def test_system_prompt_contains_esg(self, persona):
        """ESG/괭생이모자반 기술 스토리 지침이 포함되어야 한다."""
        prompt = persona.get_system_prompt()
        assert "괭생이모자반" in prompt

    def test_system_prompt_contains_non_goals(self, persona):
        """비목표(재고수정/결제/레시피 비공개) 제한사항이 포함되어야 한다."""
        prompt = persona.get_system_prompt()
        assert "결제" in prompt or "쇼핑몰 링크" in prompt
        assert "레시피" in prompt or "배합비" in prompt

    def test_system_prompt_data_priority(self, persona):
        """데이터 우선순위(홈페이지 > 뉴스 > 브로셔)가 명시되어야 한다."""
        prompt = persona.get_system_prompt()
        assert "우선순위" in prompt or "홈페이지" in prompt

    def test_get_greeting(self, persona):
        """브랜드 톤에 맞는 인사말을 반환해야 한다."""
        greeting = persona.get_greeting()
        assert "무계상사" in greeting or "무계 상사" in greeting
        assert len(greeting) > 20

    def test_system_prompt_multilingual_mention(self, persona):
        """다국어 지원 관련 지침이 포함되어야 한다."""
        prompt = persona.get_system_prompt()
        assert "다국어" in prompt or "언어" in prompt
