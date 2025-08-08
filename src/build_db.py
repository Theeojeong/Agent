from __future__ import annotations

from pathlib import Path

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

DOC_DIR = Path("documents")
PDF_FILES = [
    DOC_DIR / "형법(법률).pdf",
    DOC_DIR / "형사소송법(법률).pdf",
]
PERSIST_DIR = Path("data/processed/chroma")
PERSIST_DIR.mkdir(parents=True, exist_ok=True)

# LangChain
splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=100,
    separators=["\n\n", "\n", " "]
)
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")


def load_documents() -> list:
    """PDF 파일 로드 -> 텍스트 청크 리스트 반환"""
    documents = []
    for pdf_path in PDF_FILES:
        if not pdf_path.exists():
            raise FileNotFoundError(
                f"{pdf_path} 가 존재하지 않습니다."
            )

        loader = PyPDFLoader(str(pdf_path))
        pages = loader.load()  # 각 페이지가 Document 객체
        for page in pages:
            # 페이지 단위 → splitter 로 추가 분할
            documents.extend(splitter.split_documents([page]))
    return documents


def build_db():
    """Chroma 벡터스토어 구축 후 retriever 반환"""
    docs = load_documents()
    print(f"📄 문서 청크 수: {len(docs)}  / 임베딩 생성 중 …")

    vector_store = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        collection_name="criminal_law",
        persist_directory=str(PERSIST_DIR),
    )
    print(f"Chroma 인덱스 저장 완료 → {PERSIST_DIR}")
    return vector_store.as_retriever(search_kwargs={"k": 3})


if __name__ == "__main__":
    build_db()
