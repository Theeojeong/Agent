"""
단일 문항(question, options 4개) → 'A'/'B'/'C'/'D' 예측 반환
"""
import json, faiss, numpy as np
from openai import OpenAI
from utils import embed_query, get_topk_context

CHAT_MODEL = "gpt-4o-mini"

# FAISS 초기화 (컨테이너 구동 시 1회)
index = faiss.read_index("data/processed/kb.index")
with open("data/processed/chunks.jsonl", encoding="utf-8") as f:
    KB_TEXTS = [json.loads(l)["text"] for l in f]

client = OpenAI()

def answer_one(sample: dict, k: int = 3) -> str:
    q, choices = sample["question"], sample["options"]  # options: ["(A)...", "(B)...", ...]
    # 1) 검색
    ctxs = get_topk_context(q, index, KB_TEXTS, k=k)

    # 2) 프롬프트
    system = "You are a helpful Korean criminal‑law expert."
    user_msg = (
        f"{q}\n"
        f"선택지:\n" +
        "\n".join(choices) +
        "\n\n[참고 자료]\n" + "\n---\n".join(ctxs) +
        "\n\n정답의 알파벳 한 글자만 답해주세요."
    )

    resp = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": user_msg}],
        temperature=0
    )
    text = resp.choices[0].message.content.strip().upper()
    return text[0]  # 'A' …
