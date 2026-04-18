"""외부 마크다운 데이터(공식 홈페이지 / 가격 / 뉴스)를 RAG Document 리스트로 로드.

CLAUDE.md 우선순위: homepage(1) > news(2) > brochure(3)
- 260418 Website Data/   → homepage (priority 1)
- 260418 Latest News/    → news      (priority 2)
- 260418 price information/ → brochure (priority 3)

마크다운을 H2(`## `) 헤딩 단위로 쪼개 청크를 만든다.
너무 긴 청크는 문단(빈 줄) 단위로 재분할한다.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path

from src.chatbot.rag_engine import Document


PROJECT_ROOT = Path(__file__).resolve().parents[2]

# (폴더명, source, priority, 기본 태그)
KNOWLEDGE_SOURCES: list[tuple[str, str, int, list[str]]] = [
    ("260418 Website Data", "homepage", 1, ["회사정보", "기술력"]),
    ("260418 Latest News", "news", 2, ["뉴스"]),
    ("260418 price information", "brochure", 3, ["가격", "제품"]),
]

# 청크 최대 글자수 (긴 섹션은 추가 분할)
CHUNK_MAX_CHARS = 900

# 공통 태그 추출 키워드
TAG_KEYWORDS = {
    "하늘천": "제품",
    "따지": "제품",
    "금계": "제품",
    "해유기": "제품",
    "천년유박": "제품",
    "폴코스": "제품",
    "황소": "제품",
    "스테비아": "제품",
    "달달이": "제품",
    "유황복합": "제품",
    "농축칼슘": "제품",
    "괭생이모자반": "괭생이모자반",
    "탈염": "기술력",
    "열분해": "기술력",
    "KOEM": "ESG",
    "해양환경공단": "ESG",
    "ESG": "ESG",
    "JAS": "인증",
    "ISO": "인증",
    "드론": "드론",
    "방제": "드론",
    "맵핑": "드론",
    "수출": "수출",
    "베트남": "수출",
    "캄보디아": "수출",
    "대만": "수출",
    "녹색상품": "인증",
    "4無": "공법",
    "N-P-K": "제품",
    "가격": "가격",
    "원": "가격",
}


def _extract_tags(text: str, base_tags: list[str]) -> list[str]:
    tags = set(base_tags)
    for kw, tag in TAG_KEYWORDS.items():
        if kw in text:
            tags.add(tag)
    return sorted(tags)


def _split_long_chunk(text: str, max_chars: int = CHUNK_MAX_CHARS) -> list[str]:
    """긴 청크를 문단(빈 줄) 단위로 재분할."""
    if len(text) <= max_chars:
        return [text]
    paragraphs = re.split(r"\n\s*\n", text)
    chunks: list[str] = []
    current = ""
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if len(current) + len(para) + 2 > max_chars and current:
            chunks.append(current.strip())
            current = para
        else:
            current = f"{current}\n\n{para}" if current else para
    if current:
        chunks.append(current.strip())
    return chunks or [text]


def _chunk_markdown(md: str) -> list[tuple[str, str]]:
    """`## ` 헤딩 단위로 (heading, body) 리스트 생성. 첫 헤딩 이전 본문은 'intro'."""
    lines = md.splitlines()
    chunks: list[tuple[str, str]] = []
    buf: list[str] = []
    heading = "intro"
    for line in lines:
        if line.startswith("## "):
            if buf:
                chunks.append((heading, "\n".join(buf).strip()))
            heading = line[3:].strip()
            buf = []
        else:
            buf.append(line)
    if buf:
        chunks.append((heading, "\n".join(buf).strip()))
    # 비어있는 청크 제거
    return [(h, b) for h, b in chunks if b]


def load_documents(root: str | os.PathLike | None = None) -> list[Document]:
    """세 폴더의 .md 파일을 읽어 Document 리스트 반환."""
    root_path = Path(root) if root else PROJECT_ROOT
    documents: list[Document] = []

    for folder, source, priority, base_tags in KNOWLEDGE_SOURCES:
        folder_path = root_path / folder
        if not folder_path.is_dir():
            continue
        for md_file in sorted(folder_path.glob("*.md")):
            try:
                raw = md_file.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            for heading, body in _chunk_markdown(raw):
                for piece in _split_long_chunk(body):
                    content = f"[{md_file.stem} > {heading}]\n{piece}"
                    documents.append(Document(
                        content=content,
                        source=source,
                        tags=_extract_tags(content, base_tags),
                        priority=priority,
                    ))
    return documents


if __name__ == "__main__":
    docs = load_documents()
    print(f"로드된 Document 수: {len(docs)}")
    by_source: dict[str, int] = {}
    for d in docs:
        by_source[d.source] = by_source.get(d.source, 0) + 1
    for src, cnt in by_source.items():
        print(f"  - {src}: {cnt}")
