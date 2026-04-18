"""무계 상사 스마트 AgTech 상담 에이전트 — Streamlit 웹 앱

데이터 소스 (CLAUDE.md 우선순위: 공식 홈페이지 > 뉴스 > 쇼핑 브로셔)
- 260418 Website Data/     → homepage (priority 1)
- 260418 Latest News/      → news      (priority 2)
- 260418 price information/→ brochure (priority 3)
"""
import os
import streamlit as st

from src.chatbot.chat_router import ChatRouter
from src.chatbot.rag_engine import RAGEngine
from src.chatbot.claude_client import ClaudeClient
from src.chatbot.fertilizer_calculator import FertilizerCalculator
from src.chatbot.persona import MugePersona
from src.data_preprocessing.product_catalog import ProductCatalog
from src.data_preprocessing.knowledge_loader import load_documents


# ── 페이지 설정 ──
st.set_page_config(
    page_title="무계 상사 AI 상담",
    page_icon="🌱",
    layout="centered",
)

st.title("🌱 무계 상사 스마트 AgTech 상담")
st.caption("대한민국 농업 기술의 자립을 이끄는 무계 상사 AI 상담 시스템")


# ── API 키 (Streamlit Secrets 고정) ──
def _load_api_key() -> str:
    try:
        return st.secrets["ANTHROPIC_API_KEY"]
    except (KeyError, FileNotFoundError, st.errors.StreamlitSecretNotFoundError):
        return os.getenv("ANTHROPIC_API_KEY", "")


ANTHROPIC_API_KEY = _load_api_key()


# ── 초기화 (세션 캐시) ──
@st.cache_resource
def init_rag():
    docs = load_documents()
    return RAGEngine(documents=docs), len(docs)


@st.cache_resource
def init_components():
    return ChatRouter(), ProductCatalog(), FertilizerCalculator(), MugePersona()


rag, doc_count = init_rag()
router, catalog, calc, persona = init_components()


# ── 퀵 메뉴 정의 ──
QUICK_MENU = {
    "🏢 회사정보": "무계 상사 회사 개요와 연혁, 본사 주소와 연락처를 알려주세요.",
    "🌾 제품정보": "무계 상사 주력 제품(하늘천·따지·금계·해유기1호) 특징과 N-P-K 성분을 비교해주세요.",
    "📰 회사뉴스": "최근 무계 상사 주요 뉴스(괭생이모자반 자원화 협약, 베트남 수출 등)를 정리해주세요.",
    "👤 담당자 정보": "무계 상사 대표이사와 드론·방제 담당자 연락처를 안내해주세요.",
}


# ── 사이드바 (설정 / 키 입력란 제거) ──
with st.sidebar:
    st.markdown("**📚 지식베이스**")
    st.markdown(f"총 **{doc_count}** 개 청크 (홈페이지·뉴스·가격)")
    st.divider()
    st.markdown("**주력 제품 (공식 홈페이지 기준)**")
    st.markdown("- 🌾 하늘천 — N-P-K 6-6-3.3, 유기물 66%↑")
    st.markdown("- 🌿 따지 — N-P-K 5-2.5-1.5, 유기물 80%↑")
    st.markdown("- 🐓 금계 — N-P-K 3-5.5-4.5, 유기물 66%↑")
    st.markdown("- 🌊 해유기1호 — 일본 JAS, 4無 공법")
    st.divider()
    st.markdown("**📞 문의**")
    st.markdown("- 본사: 054-701-2999")
    st.markdown("- 드론: drone@muge.co.kr / 010-9896-4228")


# 대화 이력 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.claude_history = []

# 첫 인사말
if not st.session_state.messages:
    st.session_state.messages.append({"role": "assistant", "content": persona.get_greeting()})


# ── 시비량 계산 보조 ──
def get_fertilizer_info(query):
    for crop in calc.list_supported_crops():
        if crop in query:
            for name in catalog.list_product_names():
                if name in query:
                    try:
                        return calc.calculate(crop, name, area_pyeong=300)["guide"]
                    except ValueError:
                        continue
            try:
                return calc.calculate(crop, "하늘천", area_pyeong=300)["guide"]
            except ValueError:
                return None
    return None


# ── 답변 생성 로직 ──
def generate_answer(query: str) -> str:
    resp = router.handle(query)

    if resp.transfer:
        return f"🔔 {resp.message}"

    if not ANTHROPIC_API_KEY:
        context = rag.build_context(query) if resp.needs_rag else ""
        fert = get_fertilizer_info(query)
        parts = [resp.message]
        if context:
            parts.append(f"\n\n📋 **참고 자료**\n{context}")
        if fert:
            parts.append(f"\n\n📊 **시비량 가이드**\n{fert}")
        if resp.needs_rag:
            parts.append("\n\n⚠️ *Claude API 키 설정 전이라 참고자료만 표시됩니다.*")
        return "\n".join(parts)

    context = rag.build_context(query) if resp.needs_rag else None
    fert = get_fertilizer_info(query)
    if fert:
        context = (context or "") + f"\n\n[시비량 계산 결과]\n{fert}"

    llm = ClaudeClient(api_key=ANTHROPIC_API_KEY)
    answer = llm.chat(
        query,
        context=context,
        history=st.session_state.claude_history[-10:],
    )
    st.session_state.claude_history.append({"role": "user", "content": query})
    st.session_state.claude_history.append({"role": "assistant", "content": answer})
    return answer


def handle_user_input(query: str):
    st.session_state.messages.append({"role": "user", "content": query})
    answer = generate_answer(query)
    st.session_state.messages.append({"role": "assistant", "content": answer})


# ── 기존 메시지 렌더링 ──
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# ── 퀵 메뉴 버튼 ──
st.markdown("**💡 빠른 문의**")
cols = st.columns(len(QUICK_MENU))
for col, (label, prompt) in zip(cols, QUICK_MENU.items()):
    if col.button(label, use_container_width=True, key=f"quick_{label}"):
        handle_user_input(prompt)
        st.rerun()


# ── 사용자 자유 입력 ──
if query := st.chat_input("무엇이든 물어보세요..."):
    handle_user_input(query)
    st.rerun()
