"""GPT-4o-mini 기반 LLM 클라이언트

시스템 프롬프트(페르소나) + RAG 컨텍스트 + 대화 이력을 조합하여
OpenAI ChatCompletion API를 호출한다.
"""
from openai import OpenAI

from src.chatbot.persona import MugePersona


class LLMClient:
    def __init__(self, api_key: str):
        self._client = OpenAI(api_key=api_key)
        self.model = "gpt-4o-mini"
        self.system_prompt = MugePersona().get_system_prompt()

    def build_messages(self, query: str, context: str = None, history: list = None) -> list:
        messages = [{"role": "system", "content": self.system_prompt}]

        for msg in (history or []):
            messages.append(msg)

        if context:
            user_content = (
                f"[참고 자료]\n{context}\n\n"
                f"[고객 질문]\n{query}"
            )
        else:
            user_content = query

        messages.append({"role": "user", "content": user_content})
        return messages

    def chat(self, query: str, context: str = None, history: list = None) -> str:
        messages = self.build_messages(query, context, history)
        response = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
        )
        return response.choices[0].message.content
