"""
공통 유틸 함수
"""
import numpy as np
import faiss
import tiktoken
from openai import OpenAI

embedding_model = "text-embedding-3-small"
tokenizer = tiktoken.get_encoding("cl100k_base")  # GPT‑4o 계열과 호환
client = OpenAI()


def chunk_text(text: str, max_tokens: int = 256) -> list[str]:
    """길이 N 토큰짜리 문서를 max_tokens 단위로 잘라 리스트 반환"""
    x = tokenizer.encode(text)
    chunks = [
        tokenizer.decode(x[i : i + max_tokens])
        for i in range(0, len(x), max_tokens)
    ]
    return chunks


def embed_query(query: str) -> list[float]:
    """query → 1536 차원 embedding 벡터"""
    response = client.embeddings.create(input=query, model=embedding_model)
    return response.data[0].embedding


def get_topk_context(query: str, index: faiss.Index, texts: list[str], k: int = 3) -> list[str]:
    """query 임베딩으로 FAISS 검색 → 상위 k개의 본문 반환"""
    embbeding = np.array(embed_query(query), dtype="float32").reshape(1, -1)
    D, I = index.search(embbeding, k)
    return [texts[i] for i in I[0] if i != -1]
