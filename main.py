"""무계 상사 스마트 AgTech 상담 에이전트 — CLI 데모

데이터 소스: 260418 Website Data / 260418 Latest News / 260418 price information
"""
from src.chatbot.persona import MugePersona
from src.chatbot.chat_router import ChatRouter
from src.chatbot.rag_engine import RAGEngine
from src.chatbot.fertilizer_calculator import FertilizerCalculator
from src.data_preprocessing.product_catalog import ProductCatalog
from src.data_preprocessing.knowledge_loader import load_documents


def build_rag_engine() -> tuple[RAGEngine, int]:
    """홈페이지·뉴스·가격 마크다운을 RAG 엔진에 로드"""
    docs = load_documents()
    return RAGEngine(documents=docs), len(docs)


def handle_product_query(query, rag, catalog, calc):
    """제품/시비량 관련 질문 처리"""
    context = rag.build_context(query)
    response = f"[참고 자료]\n{context}\n"

    for crop in calc.list_supported_crops():
        if crop in query:
            for name in catalog.list_product_names():
                if name in query:
                    try:
                        result = calc.calculate(crop, name, area_pyeong=300)
                        response += f"\n[시비량 계산 (기본 300평 기준)]\n{result['guide']}"
                        return response
                    except ValueError:
                        continue
            try:
                result = calc.calculate(crop, "하늘천", area_pyeong=300)
                response += f"\n[시비량 계산 — 하늘천 추천 (300평 기준)]\n{result['guide']}"
            except ValueError:
                pass
            return response

    return response


def main():
    persona = MugePersona()
    router = ChatRouter()
    rag, doc_count = build_rag_engine()
    catalog = ProductCatalog()
    calc = FertilizerCalculator()

    print("=" * 60)
    print(persona.get_greeting())
    print(f"\n[지식베이스] 홈페이지·뉴스·가격 문서 {doc_count}개 청크 로드")
    print("=" * 60)
    print("(종료: 'quit' / 'q' / '종료' 입력)\n")

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
