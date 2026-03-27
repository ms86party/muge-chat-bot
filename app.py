"""무계 상사 스마트 AgTech 상담 에이전트 — Streamlit 웹 앱"""
import os
import streamlit as st

from src.chatbot.chat_router import ChatRouter
from src.chatbot.rag_engine import RAGEngine, Document
from src.chatbot.llm_client import LLMClient
from src.chatbot.fertilizer_calculator import FertilizerCalculator
from src.data_preprocessing.product_catalog import ProductCatalog
from src.chatbot.persona import MugePersona


# ── 페이지 설정 ──
st.set_page_config(
    page_title="무계 상사 AI 상담",
    page_icon="🌱",
    layout="centered",
)

st.title("🌱 무계 상사 스마트 AgTech 상담")
st.caption("대한민국 농업 기술의 자립을 이끄는 무계 상사 AI 상담 시스템")


# ── 사이드바: API 키 입력 ──
with st.sidebar:
    st.header("⚙️ 설정")
    api_key = st.text_input("OpenAI API Key", type="password", value=os.getenv("OPENAI_API_KEY", ""))
    st.divider()
    st.markdown("**주력 제품**")
    st.markdown("- 🌾 하늘천 (N-P-K 12-4-6)")
    st.markdown("- 🌿 따지 (N-P-K 8-3-4)")
    st.markdown("- 🌊 해유기1호 (N-P-K 5-3-2)")
    st.divider()
    st.markdown("**문의 예시**")
    st.markdown("- 하늘천 성분 알려주세요")
    st.markdown("- 벼에 맞는 비료 추천해주세요")
    st.markdown("- 왜 무계를 선택해야 하나요?")
    st.markdown("- 고추 시비량 계산해주세요")


# ── 초기화 (세션 상태) ──
@st.cache_resource
def init_rag():
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
                    "4無 공법(무항생제/무염분/무가스/무취)이 적용되었다. "
                    "과수, 채소, 화훼, 수도작 등 다목적 사용 가능.",
            source="brochure", tags=["제품", "4無공법"], priority=3,
        ),
        Document(
            content="따지는 N-P-K 8-3-4 균형 배합 유기질비료로, 밑거름·웃거름 겸용이 가능하다. "
                    "토양 산도(pH) 개선 효과가 있다.",
            source="brochure", tags=["제품"], priority=3,
        ),
        Document(
            content="해유기1호는 괭생이모자반 원료 기반 해양 유기질비료(N-P-K 5-3-2)이다. "
                    "KOEM 협약 자원화 기술이 적용되어 ESG 경영을 실천하며, "
                    "해양 미네랄이 풍부하여 작물 면역력을 강화한다.",
            source="brochure", tags=["제품", "괭생이모자반", "ESG"], priority=3,
        ),
    ]
    return RAGEngine(documents=docs)


@st.cache_resource
def init_components():
    return ChatRouter(), ProductCatalog(), FertilizerCalculator(), MugePersona()


rag = init_rag()
router, catalog, calc, persona = init_components()

# 대화 이력 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.openai_history = []

# 첫 인사말
if not st.session_state.messages:
    greeting = persona.get_greeting()
    st.session_state.messages.append({"role": "assistant", "content": greeting})


# ── 시비량 계산 보조 ──
def get_fertilizer_info(query):
    for crop in calc.list_supported_crops():
        if crop in query:
            for name in catalog.list_product_names():
                if name in query:
                    return calc.calculate(crop, name, area_pyeong=300)["guide"]
            return calc.calculate(crop, "하늘천", area_pyeong=300)["guide"]
    return None


# ── 기존 메시지 렌더링 ──
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# ── 사용자 입력 처리 ──
if query := st.chat_input("무엇이든 물어보세요..."):
    # 사용자 메시지 표시
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    # 라우팅
    resp = router.handle(query)

    # 상담원 전환
    if resp.transfer:
        answer = f"🔔 {resp.message}"
    # API 키 없으면 키워드 기반 응답
    elif not api_key:
        context = rag.build_context(query) if resp.needs_rag else ""
        fert = get_fertilizer_info(query)
        parts = [resp.message]
        if context:
            parts.append(f"\n\n📋 **참고 자료**\n{context}")
        if fert:
            parts.append(f"\n\n📊 **시비량 가이드**\n{fert}")
        if not api_key and resp.needs_rag:
            parts.append("\n\n⚠️ *OpenAI API 키를 입력하면 GPT-4o-mini 기반 자연어 답변을 받을 수 있습니다.*")
        answer = "\n".join(parts)
    # GPT-4o-mini 응답
    else:
        context = rag.build_context(query) if resp.needs_rag else None
        fert = get_fertilizer_info(query)
        if fert:
            context = (context or "") + f"\n\n[시비량 계산 결과]\n{fert}"

        llm = LLMClient(api_key=api_key)
        with st.chat_message("assistant"):
            with st.spinner("답변을 준비하고 있습니다..."):
                answer = llm.chat(
                    query,
                    context=context,
                    history=st.session_state.openai_history[-10:],  # 최근 5턴
                )
            st.markdown(answer)

        # 이력 저장
        st.session_state.openai_history.append({"role": "user", "content": query})
        st.session_state.openai_history.append({"role": "assistant", "content": answer})
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.stop()

    # GPT가 아닌 경우 응답 표시
    with st.chat_message("assistant"):
        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})
