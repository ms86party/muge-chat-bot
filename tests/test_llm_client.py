"""GPT-4o-mini LLM 클라이언트 테스트 - TDD 선행 작성"""
import pytest
from unittest.mock import patch, MagicMock

from src.chatbot.llm_client import LLMClient


@pytest.fixture
def client():
    return LLMClient(api_key="test-key")


class TestLLMClient:
    def test_has_system_prompt(self, client):
        """시스템 프롬프트가 설정되어 있어야 한다."""
        assert "무계 상사" in client.system_prompt
        assert "기술 전략 실장" in client.system_prompt

    def test_model_is_gpt4o_mini(self, client):
        """모델이 gpt-4o-mini로 설정되어야 한다."""
        assert client.model == "gpt-4o-mini"

    def test_build_messages_without_context(self, client):
        """RAG 컨텍스트 없이 메시지 목록을 구성할 수 있어야 한다."""
        messages = client.build_messages("안녕하세요", context=None, history=[])
        assert messages[0]["role"] == "system"
        assert messages[-1]["role"] == "user"
        assert messages[-1]["content"] == "안녕하세요"

    def test_build_messages_with_context(self, client):
        """RAG 컨텍스트가 있으면 user 메시지에 포함되어야 한다."""
        ctx = "[news] 괭생이모자반 자원화 기술"
        messages = client.build_messages("왜 무계인가요?", context=ctx, history=[])
        user_msg = messages[-1]["content"]
        assert "괭생이모자반" in user_msg
        assert "왜 무계인가요?" in user_msg

    def test_build_messages_with_history(self, client):
        """대화 이력이 메시지에 포함되어야 한다."""
        history = [
            {"role": "user", "content": "하늘천이 뭔가요?"},
            {"role": "assistant", "content": "하늘천은 유기질비료입니다."},
        ]
        messages = client.build_messages("성분은요?", context=None, history=history)
        assert len(messages) == 4  # system + 2 history + user

    def test_chat_calls_openai(self, client):
        """chat 호출 시 OpenAI API를 호출해야 한다."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "테스트 응답입니다."

        with patch.object(client._client.chat.completions, "create", return_value=mock_response):
            result = client.chat("안녕하세요", context=None, history=[])
            assert result == "테스트 응답입니다."
