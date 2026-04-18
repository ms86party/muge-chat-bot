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
    "하늘천", "따지", "금계", "해유기", "천년유박",
    "폴코스", "풀코스", "황소", "스테비아", "유황", "농축칼슘", "달달이",
    "비료", "영양제", "액비", "성분", "N-P-K", "시비",
    "추천", "용량", "사용법", "작물",
]
_FAQ_KW = [
    "영업시간", "운영시간", "주소", "위치", "전화번호", "연락처",
    "홈페이지", "이메일", "설립", "연혁",
]
_GREETING_KW = ["안녕", "하이", "hello", "hi", "반갑"]

# FAQ 답변 사전 (공식 홈페이지 muge.co.kr 기준)
FAQ_ANSWERS = {
    "주소": "㈜무계상사 본사는 **경상북도 영천시 북안면 대경로 2166-112 (유하리 41번지)** 에 위치하고 있습니다. 자가용 이용 시 네비게이션에 '무계상사' 로 검색하시면 됩니다.",
    "위치": "㈜무계상사 본사는 **경상북도 영천시 북안면 대경로 2166-112** 입니다.",
    "전화번호": "㈜무계상사 대표 전화는 **054-701-2999**, 팩스는 054-701-2990 입니다. 드론 관련 문의는 **010-9896-4228 (류한웅 연구원)** 또는 drone@muge.co.kr 로 연락 주세요.",
    "연락처": "본사 054-701-2999 / 드론 010-9896-4228 / 이메일 drone@muge.co.kr",
    "영업시간": "㈜무계상사 영업시간은 평일 09:00~18:00 입니다. (점심 12:00~13:00)",
    "연혁": "무계상사는 **2005년 설립**, **2008년 법인 전환**된 이래, 2015년 클린사업장 지정, 2017년 영천 제2공장 완공 및 하늘천·따지 출시, 2018년 전담 연구소 설립, 벤처·여성·수출유망기업 인증을 받은 농업 전문 기업입니다.",
    "설립": "㈜무계상사는 2005년 설립(2008년 법인 전환)된 친환경 명품 비료 전문 기업입니다.",
    "대표": "㈜무계상사 대표이사는 **유명하** 입니다. 무계스마트농업 대표는 **류한웅**, ㈜무계바이오 농업회사법인 대표는 **류욱하** 입니다.",
    "홈페이지": "공식 홈페이지: http://www.muge.co.kr (도메인 별칭: www.goldhand.kr)",
    "이메일": "드론·방제 관련 문의: drone@muge.co.kr / 담당: 류한웅 연구원",
    "default": "해당 문의사항은 공식 홈페이지(muge.co.kr) 또는 본사 054-701-2999 로 연락 부탁드립니다.",
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
                    "㈜무계상사 제품은 아래 공식 채널에서 구매하실 수 있습니다.\n"
                    "• **네이버 스마트스토어 '친환경기업무계상사'** (공식 직영, 무료배송·1+1 프로모션)\n"
                    "• 쿠팡 / G마켓 / 옥션 / 11번가 / SSG (무계바이오 라인업)\n"
                    "• 본사 B2B·대리점 문의: 054-701-2999\n"
                    "원하시는 제품명(하늘천·따지·금계·해유기1호·폴코스·황소4종·스테비아 등)을 말씀해 주시면 자세한 가격·스펙을 안내해 드리겠습니다."
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
