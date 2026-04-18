"""RAG 엔진 — 질문 의도 감지, 문서 검색, 컨텍스트 빌드

'왜 무계인가' 질문 시 괭생이모자반 자원화 기술을 핵심 근거로 연결한다.
데이터 우선순위: homepage(1) > news(2) > brochure(3)
"""
import re
from dataclasses import dataclass, field


PRODUCT_NAMES = ["하늘천", "따지", "금계", "해유기1호", "해유기", "천년유박", "폴코스", "황소", "스테비아", "달달이"]

WHY_MUGE_KEYWORDS = [
    "왜 무계", "왜 선택", "다른 회사", "차별", "강점", "장점",
    "뭐가 다른", "뭐가 좋", "특별", "경쟁력",
]

PRODUCT_KEYWORDS = PRODUCT_NAMES + [
    "제품", "비료", "성분", "N-P-K", "시비", "어디서 사",
    "가격", "용량", "사용법",
]

ESG_KEYWORDS = [
    "ESG", "친환경", "괭생이모자반", "자원화", "해양", "탈염", "열분해",
]


@dataclass
class Document:
    content: str
    source: str = "unknown"
    tags: list = field(default_factory=list)
    priority: int = 3


class RAGEngine:
    """키워드 기반 RAG 검색 엔진 (벡터DB 연동 전 프로토타입)"""

    def __init__(self, documents: list = None):
        self._documents = documents or []

    def add_document(self, doc: Document):
        self._documents.append(doc)

    def _tokenize(self, text: str) -> list[str]:
        # 한/영/숫자 토큰 추출 (2자 이상)
        tokens = re.findall(r"[0-9A-Za-z가-힣]+", text)
        return [t for t in tokens if len(t) >= 2]

    def retrieve(self, query: str, top_k: int = 5) -> list:
        """토큰 오버랩 + 우선순위 기반 스코어링."""
        q_tokens = set(self._tokenize(query))
        if not q_tokens:
            return []

        scored = []
        for doc in self._documents:
            d_tokens = set(self._tokenize(doc.content)) | set(doc.tags)
            overlap = len(q_tokens & d_tokens)
            if overlap == 0:
                continue
            # 우선순위가 낮을수록(1=최상) 점수 가중
            score = overlap * 10 - doc.priority
            scored.append((score, doc))

        scored.sort(key=lambda x: (-x[0], x[1].priority))
        return [doc for _, doc in scored[:top_k]]

    def retrieve_by_tag(self, tag: str) -> list:
        matched = [doc for doc in self._documents if tag in doc.tags]
        matched.sort(key=lambda d: d.priority)
        return matched

    def detect_intent(self, query: str) -> str:
        if any(kw in query for kw in WHY_MUGE_KEYWORDS):
            return "why_muge"
        if any(kw in query for kw in PRODUCT_KEYWORDS):
            return "product"
        if any(kw in query for kw in ESG_KEYWORDS):
            return "esg"
        return "general"

    def build_context(self, query: str, top_k: int = 5) -> str:
        intent = self.detect_intent(query)

        if intent == "why_muge":
            docs = (self.retrieve_by_tag("괭생이모자반")
                    + self.retrieve_by_tag("ESG")
                    + self.retrieve(query, top_k=top_k))
        elif intent == "product":
            docs = self.retrieve(query, top_k=top_k) + self.retrieve_by_tag("제품")[:3]
        elif intent == "esg":
            docs = (self.retrieve_by_tag("ESG")
                    + self.retrieve_by_tag("괭생이모자반")
                    + self.retrieve(query, top_k=top_k))
        else:
            docs = self.retrieve(query, top_k=top_k)

        # 중복 제거 및 우선순위 정렬, 상위 top_k만 컨텍스트로
        seen = set()
        unique_docs = []
        for doc in docs:
            if id(doc) not in seen:
                seen.add(id(doc))
                unique_docs.append(doc)
        unique_docs.sort(key=lambda d: d.priority)
        unique_docs = unique_docs[:top_k]

        lines = [f"[{doc.source}] {doc.content}" for doc in unique_docs]
        return "\n\n".join(lines)
