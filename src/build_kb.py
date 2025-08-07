import numpy as np
import faiss, pathlib, requests
from tqdm.auto import tqdm
from utils import chunk_text, embedding_model
from openai import OpenAI

raw_txt = pathlib.Path("data/raw/korean_criminal_law.txt")
OUT_DIR = pathlib.Path("data/processed")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def download_if_needed():
    if raw_txt.exists():
        return
    print("📥 형법 원본 다운로드 중")
    url = "https://raw.githubusercontent.com/law3340/korean-law/main/criminal_law.txt"
    text = requests.get(url, timeout=30).text
    raw_txt.write_text(text, encoding="utf-8")

def main():
    download_if_needed()
    client = OpenAI()

    text = raw_txt.read_text(encoding="utf-8")
    chunks = chunk_text(text, max_tokens=512)

    embedding = []
    for i in tqdm(chunks, desc="Embedding KB"):
        v = client.embeddings.create(input=i, model=embedding_model).data[0].embedding
        embedding.append(v)

    # FAISS
    index = faiss.IndexFlatIP(len(embedding[0]))
    index.add(np.array(embedding, dtype="float32"))
    faiss.write_index(index, str(OUT_DIR / "kb.index"))

    # chunk 저장
    with open(OUT_DIR / "chunks.jsonl", "w", encoding="utf-8") as f:
        for i in chunks:
            f.write('{"text": "' + i.replace('"', '\\"') + '"}\n')

    print("✅ KB 구축 완료:", len(chunks), "청크")

if __name__ == "__main__":
    main()
