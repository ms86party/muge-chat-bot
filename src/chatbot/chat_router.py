"""상담 워크플로우 분기 라우터

시나리오: greeting, faq, product, tech, purchase, human
TechSpec 기준: 일반 FAQ / 기술 상담 / 상담원 전환 3단계 분기
"""
from dataclasses import dataclass, field

from src.chatbot.persona import MugePersona

# 시나리오별 키워드 사전
_HUMAN_KW = ["상담원", "상담사", "사람", "담당자", "통화하고", "연결해", "바꿔"]
_PURCHASE_KW = ["구매", "구입", "주문", "결제", "어디서 사", "어디서 살", "배송", "가격"]
_TECH_KW = [
    "괭생이모자반", "탈염", "열분해", "자원화", "esg", "공정", "기술력",
    "연구소", "특허", "ISO", "공법",
]
_PRODUCT_KW = [
    "하늘천", "따지", "해유기", "비료", "성분", "N-P-K", "시비",
    "추천", "용량", "사용법", "작물",
]
_FAQ_KW = [
    "영업시간", "운영시간", "주소", "위치", "전화번호", "연락처",
    "홈페이지", "이메일", "설립", "연혁",
]
_GREETING_KW = ["안녕", "하이", "hello", "hi", "반갑"]

# FAQ 답변 사전
FAQ_ANSWERS = {
    "주소": "무계 상사 본사는 경상남도에 위치하고 있습니다. 자세한 주소는 공식 홈페이지(muge.co.kr)에서 확인하실 수 있습니다.",
    "전화번호": "무계 상사 대표 연락처는 공식 홈페이지(muge.co.kr)에서 확인하실 수 있습니다.",
    "영업시간": "무계 상사 영업시간은 평일 09:00~18:00입니다. (점심 12:00~13:00)",
    "연혁": "무계 상사는 1992년 설립되어 30년 이상의 농업 기술 노하우를 보유하고 있습니다.",
    "default": "해당 문의사항은 공식 홈페이지(muge.co.kr)에서 확인하시거나, 고객센터로 연락 부탁드립니다.",
}


@dataclass
class ChatResponse:
    scenario: str
    message: str
    transfer: bool = False
    needs_rag: bool = False


class ChatRouter:
    """질문을 시나리오별로 분류하고 적절한 응답 흐름으로 라우팅한다."""

    def __init__(self):
        self._persona = MugePersona()

    def classify(self, query: str) -> str:
        q = query.lower()
        if any(kw in q for kw in _HUMAN_KW):
            return "human"
        if any(kw in q for kw in _GREETING_KW):
            return "greeting"
        if any(kw in q for kw in _PURCHASE_KW):
            return "purchase"
        if any(kw in q for kw in _TECH_KW):
            return "tech"
        if any(kw in q for kw in _PRODUCT_KW):
            return "product"
        if any(kw in q for kw in _FAQ_KW):
            return "faq"
        return "faq"

    def handle(self, query: str) -> ChatResponse:
        scenario = self.classify(query)

        if scenario == "greeting":
            return ChatResponse(
                scenario="greeting",
                message=self._persona.get_greeting(),
            )

        if scenario == "human":
            return ChatResponse(
                scenario="human",
                message="상담원 연결을 도와드리겠습니다. 잠시만 기다려 주세요. 근무시간(평일 09:00~18:00) 내 순차적으로 연결해 드립니다.",
                transfer=True,
            )

        if scenario == "purchase":
            return ChatResponse(
                scenario="purchase",
                message=(
                    "무계 상사 제품은 아래 공식 쇼핑몰에서 구매하실 수 있습니다.\n"
                    "• 쿠팡(Coupang): 무계 상사 공식 스토어\n"
                    "• 네이버(Naver) 스마트스토어: 무계 상사\n"
                    "원하시는 제품명을 말씀해 주시면 직접 링크를 안내해 드리겠습니다."
                ),
            )

        if scenario == "tech":
            return ChatResponse(
                scenario="tech",
                message="기술 관련 문의를 확인하고 있습니다. 관련 자료를 바탕으로 답변드리겠습니다.",
                needs_rag=True,
            )

        if scenario == "product":
            return ChatResponse(
                scenario="product",
                message="제품 상담을 도와드리겠습니다. 관련 제품 정보를 확인하고 있습니다.",
                needs_rag=True,
            )

        # faq
        answer = FAQ_ANSWERS["default"]
        for key, value in FAQ_ANSWERS.items():
            if key != "default" and key in query:
                answer = value
                break
        return ChatResponse(scenario="faq", message=answer)
