"""무계 상사 스마트 AgTech 상담 에이전트 — CLI 데모"""
from src.chatbot.persona import MugePersona
from src.chatbot.chat_router import ChatRouter
from src.chatbot.rag_engine import RAGEngine, Document
from src.chatbot.fertilizer_calculator import FertilizerCalculator
from src.data_preprocessing.product_catalog import ProductCatalog


def build_rag_engine():
    """제품 카탈로그 + 브랜드 데이터를 RAG 엔진에 로드"""
    docs = [
        Document(
            content="해양환경공단(KOEM)과 무계 상사가 괭생이모자반 자원화 협약을 체결했다. "
                    "탈염 및 열분해 공정을 통해 해양폐기물을 친환경 비료 원료로 전환하는 기술이 핵심이다.",
            source="news", tags=["ESG", "괭생이모자반", "기술력"], priority=2,
        ),
        Document(
            content="무계 상사는 1992년 설립, ISO 9001 인증 보유 농업 전문 기업이다. "
                    "자체 연구소를 통해 유기질비료 및 미생물제제를 개발하고 있다.",
            source="homepage", tags=["회사정보", "기술력"], priority=1,
        ),
        Document(
            content="하늘천은 N-P-K 12-4-6 고함량 유기질비료로 업계 최고 수준이며, "
                    "4無 공법(무항생제/무염분/무가스/무취)이 적용되었다.",
            source="brochure", tags=["제품", "4無공법"], priority=3,
        ),
        Document(
            content="따지는 N-P-K 8-3-4 균형 배합 유기질비료로, 밑거름·웃거름 겸용이 가능하다.",
            source="brochure", tags=["제품"], priority=3,
        ),
        Document(
            content="해유기1호는 괭생이모자반 원료 기반 해양 유기질비료(N-P-K 5-3-2)이다. "
                    "KOEM 협약 자원화 기술이 적용되어 ESG 경영을 실천한다.",
            source="brochure", tags=["제품", "괭생이모자반", "ESG"], priority=3,
        ),
    ]
    engine = RAGEngine(documents=docs)
    return engine


def handle_product_query(query, rag, catalog, calc):
    """제품/시비량 관련 질문 처리"""
    context = rag.build_context(query)
    response = f"[참고 자료]\n{context}\n"

    # 시비량 계산 요청 감지
    for crop in calc.list_supported_crops():
        if crop in query:
            for name in catalog.list_product_names():
                if name in query:
                    result = calc.calculate(crop, name, area_pyeong=300)
                    response += f"\n[시비량 계산 (기본 300평 기준)]\n{result['guide']}"
                    return response
            # 제품 미지정 시 하늘천 기본 추천
            result = calc.calculate(crop, "하늘천", area_pyeong=300)
            response += f"\n[시비량 계산 — 하늘천 추천 (300평 기준)]\n{result['guide']}"
            return response

    return response


def main():
    persona = MugePersona()
    router = ChatRouter()
    rag = build_rag_engine()
    catalog = ProductCatalog()
    calc = FertilizerCalculator()

    print("=" * 60)
    print(persona.get_greeting())
    print("=" * 60)
    print("(종료: 'quit' 또는 'q' 입력)\n")

    while True:
        try:
            query = input("🌱 고객: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n감사합니다. 좋은 하루 되세요!")
            break

        if not query:
            continue
        if query.lower() in ("quit", "q", "종료"):
            print("감사합니다. 대한민국 농업의 미래, 무계 상사가 함께합니다!")
            break

        resp = router.handle(query)

        if resp.transfer:
            print(f"🔔 {resp.message}\n")
            continue

        if resp.needs_rag:
            detail = handle_product_query(query, rag, catalog, calc)
            print(f"🧑‍🌾 무계 상사: {resp.message}\n{detail}\n")
        else:
            print(f"🧑‍🌾 무계 상사: {resp.message}\n")


if __name__ == "__main__":
    main()
