"""make_batch_input.py

KMMLU Criminal-Law 테스트셋을 읽어 OpenAI Batch API용 input JSONL 생성.
LangChain-Chroma 벡터스토어( data/processed/chroma/ )에서 관련 조문을 검색하여
프롬프트에 포함한다.
"""
import json
from pathlib import Path

import pandas as pd
from src.build_db import get_retriever

llm = "gpt-4o-mini"
retriever = get_retriever(k=3, search_type="mmr")


def make_prompt(row) -> str:
    query = row["question"]
    choices = "\n".join([
        f"(A) {row['A']}",
        f"(B) {row['B']}",
        f"(C) {row['C']}",
        f"(D) {row['D']}",
    ])

    docs = retriever.invoke(query)
    context = "\n---\n".join(d.page_content.strip() for d in docs)

    return (
        "다음은 형법 문제입니다. 주어진 참고 자료를 바탕으로 정확한 답을 선택해주세요.\n"
        f"문제: {query}\n"
        "선택지:\n"
        f"{choices}\n"
        "참고 자료:\n"
        f"{context}\n\n"
        "위의 자료를 바탕으로 가장 정확한 답을 A, B, C, D 중에서 하나만 선택하여 답해주세요.\n"
        "답변은 반드시 A, B, C, D 중 하나의 알파벳만 작성해주세요."
    )


def main():
    df = pd.read_parquet("data/raw/kmmlu_test.parquet")
    out_path = Path("batch_input.jsonl")
    with out_path.open("w", encoding="utf-8") as out:
        for i, row in df.iterrows():
            body = {
                "model": llm,
                "messages": [
                    {
                        "role": "system",
                        "content": "당신은 한국 형법 전문가입니다. 주어진 참고 자료를 바탕으로 정확한 법률 판단을 내려야 합니다. 답변은 반드시 A, B, C, D 중 하나의 알파벳만 작성해주세요.",
                    },
                    {"role": "user", "content": make_prompt(row)},
                ],
                "temperature": 0,
                "max_tokens": 1
            }
            out.write(
                json.dumps(
                    {
                        "custom_id": str(i),
                        "method": "POST",
                        "url": "/v1/chat/completions",
                        "body": body,
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
    print(f"✅ batch_input.jsonl 생성: {len(df)} 행 → {out_path}")


if __name__ == "__main__":
    main()
