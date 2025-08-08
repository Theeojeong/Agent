import json
from pathlib import Path

import pandas as pd
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

llm = "gpt-4o-mini"
CHROMA_DIR = "data/processed/chroma"


embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vector_store = Chroma(
    persist_directory=CHROMA_DIR,
    embedding_function=embeddings,
    collection_name="criminal_law",
)

retriever = vector_store.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 4, "fetch_k": 40, "lambda_mult": 0.7}
)


def make_prompt(row) -> str:
    """문제 + 선택지 + RAG 컨텍스트를 하나의 프롬프트 문자열로 생성"""
    query = row["question"]
    choices = "\n".join([
        f"(A) {row['A']}",
        f"(B) {row['B']}",
        f"(C) {row['C']}",
        f"(D) {row['D']}",
    ])

    docs = retriever.invoke(query)
    content_block = "\n---\n".join(d.page_content.strip() for d in docs)

    return (
        "다음은 형법 문제입니다. 주어진 참고 자료를 바탕으로 정확한 답을 선택해주세요.\n"
        f"문제: {query}\n"
        "선택지:\n"
        f"{choices}\n"
        "참고 자료:\n"
        f"{content_block}\n\n"
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
                "max_tokens": 2
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
