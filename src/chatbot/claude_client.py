"""Anthropic Claude 기반 LLM 클라이언트

무계 상사 페르소나 + RAG 컨텍스트 + 대화 이력을 조합하여 Claude Messages API를 호출한다.
"""
from anthropic import Anthropic

from src.chatbot.persona import MugePersona


class ClaudeClient:
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-6"):
        self._client = Anthropic(api_key=api_key)
        self.model = model
        self.system_prompt = MugePersona().get_system_prompt()

    def build_messages(self, query: str, context: str = None, history: list = None) -> list:
        messages = []
        for msg in (history or []):
            messages.append({"role": msg["role"], "content": msg["content"]})

        if context:
            user_content = f"[참고 자료]\n{context}\n\n[고객 질문]\n{query}"
        else:
            user_content = query
        messages.append({"role": "user", "content": user_content})
        return messages

    def chat(self, query: str, context: str = None, history: list = None) -> str:
        messages = self.build_messages(query, context, history)
        resp = self._client.messages.create(
            model=self.model,
            system=self.system_prompt,
            messages=messages,
            max_tokens=1024,
            temperature=0.7,
        )
        return "".join(block.text for block in resp.content if block.type == "text")
