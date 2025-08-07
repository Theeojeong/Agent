import numpy as np               # ← 누락 부분
import faiss, pathlib, requests, hashlib, os
from tqdm.auto import tqdm
from utils import chunk_text
from utils import _EMBED_MODEL as EMBED_MODEL
from openai import OpenAI

RAW_TXT = pathlib.Path("data/raw/korean_criminal_law.txt")
OUT_DIR = pathlib.Path("data/processed")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def download_if_needed():
    if RAW_TXT.exists():
        return
    print("📥 형법 원본 다운로드 중 ...")
    url = "https://raw.githubusercontent.com/law3340/korean-law/main/criminal_law.txt"
    text = requests.get(url, timeout=30).text
    RAW_TXT.write_text(text, encoding="utf-8")

def main():
    download_if_needed()
    client = OpenAI()

    text = RAW_TXT.read_text(encoding="utf-8")
    chunks = chunk_text(text, max_tokens=512)  # 256에서 512로 증가

    embeds = []
    for ch in tqdm(chunks, desc="Embedding KB"):
        v = client.embeddings.create(input=ch, model=EMBED_MODEL).data[0].embedding
        embeds.append(v)

    # FAISS
    index = faiss.IndexFlatIP(len(embeds[0]))
    index.add(np.array(embeds, dtype="float32"))
    faiss.write_index(index, str(OUT_DIR / "kb.index"))

    # chunk 저장
    with open(OUT_DIR / "chunks.jsonl", "w", encoding="utf-8") as f:
        for ch in chunks:
            f.write('{"text": "' + ch.replace('"', '\\"') + '"}\n')

    print("✅ KB 구축 완료:", len(chunks), "청크")

if __name__ == "__main__":
    main()
