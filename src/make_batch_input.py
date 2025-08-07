import json, pandas as pd, faiss, pathlib
from utils import get_topk_context, embed_query
from openai import OpenAI
import numpy as np

CHAT_MODEL = "gpt-4o-mini"  # gpt-4o-mini에서 gpt-4o로 변경
KB_INDEX = faiss.read_index("data/processed/kb.index")
KB_TEXTS = [json.loads(l)["text"] for l in open("data/processed/chunks.jsonl", encoding="utf-8")]

def make_prompt(row, k=5):  # k를 3에서 5로 증가
    q = row["question"]
    choices = "\n".join([
        f"(A) {row['A']}",
        f"(B) {row['B']}",
        f"(C) {row['C']}",
        f"(D) {row['D']}"
    ])
    ctxs = get_topk_context(q, KB_INDEX, KB_TEXTS, k)
    ctx_block = "\n---\n".join(ctxs)
    
    return f"""다음은 형법 문제입니다. 주어진 참고 자료를 바탕으로 정확한 답을 선택해주세요.

문제: {q}

선택지:
{choices}

참고 자료:
{ctx_block}

위의 참고 자료를 바탕으로 가장 정확한 답을 A, B, C, D 중에서 하나만 선택하여 답해주세요. 
답변은 반드시 A, B, C, D 중 하나의 알파벳만 작성해주세요.

예시:
- 문제가 "형법상 살인의 정의는?"이고 참고 자료에서 "살인은 사람을 사망하게 하는 행위"라고 나와 있다면
- 답변: A (만약 A가 "사람을 사망하게 하는 행위"라면)"""

def main():
    df = pd.read_parquet("data/raw/kmmlu_test.parquet")
    with open("batch_input.jsonl", "w", encoding="utf-8") as out:
        for i, row in df.iterrows():
            body = {
                "model": CHAT_MODEL,
                "messages": [
                    {"role": "system", "content": "당신은 한국 형법 전문가입니다. 주어진 참고 자료를 바탕으로 정확한 법률 판단을 내려야 합니다. 답변은 반드시 A, B, C, D 중 하나의 알파벳만 작성해주세요."},
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