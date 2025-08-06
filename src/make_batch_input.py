import json, pandas as pd, faiss, pathlib
from utils import get_topk_context, embed_query
from openai import OpenAI
import numpy as np

CHAT_MODEL = "gpt-4o-mini"
KB_INDEX = faiss.read_index("data/processed/kb.index")
KB_TEXTS = [json.loads(l)["text"] for l in open("data/processed/chunks.jsonl", encoding="utf-8")]

def make_prompt(row, k=3):
    q = row["question"]
    choices = "\n".join([
        f"(A) {row['A']}",
        f"(B) {row['B']}",
        f"(C) {row['C']}",
        f"(D) {row['D']}"
    ])
    ctxs = get_topk_context(q, KB_INDEX, KB_TEXTS, k)
    ctx_block = "\n---\n".join(ctxs)
    return f"{q}\n선택지:\n{choices}\n\n[참고 자료]\n{ctx_block}\n\n정답의 알파벳 한 글자만 답해주세요."

def main():
    df = pd.read_parquet("data/raw/kmmlu_test.parquet")
    with open("batch_input.jsonl", "w", encoding="utf-8") as out:
        for i, row in df.iterrows():
            body = {
                "model": CHAT_MODEL,
                "messages": [
                    {"role": "system", "content": "You are a helpful Korean criminal‑law expert."},
                    {"role": "user", "content": make_prompt(row)}
                ],
                "temperature": 0
            }
            out.write(json.dumps({
                "custom_id": str(i),
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": body
            }, ensure_ascii=False) + "\n")
    print("✅ batch_input.jsonl 생성:", len(df), "행")

if __name__ == "__main__":
    main()