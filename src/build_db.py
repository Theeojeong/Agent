from __future__ import annotations
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader  
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

DOC_DIR = Path("documents")
PDF_FILES = [
    DOC_DIR / "형법(법률).pdf",
    DOC_DIR / "형사소송법(법률).pdf",
]
PERSIST_DIR = Path("data/processed/chroma")
PERSIST_DIR.mkdir(parents=True, exist_ok=True)


splitter = RecursiveCharacterTextSplitter(
    chunk_size=600,
    chunk_overlap=120,
    separators=["\n\n", "\n", " "]
)

embedding_function = OpenAIEmbeddings(model="text-embedding-3-small")


def load_documents() -> list:
    """PDF 파일을 로드하여 텍스트 청크 리스트 반환"""
    documents = []
    for pdf_path in PDF_FILES:
        if not pdf_path.exists():
            raise FileNotFoundError(f"❌ {pdf_path} 가 존재하지 않습니다.")
        loader = PyMuPDFLoader(str(pdf_path))
        pages = loader.load()
        for page in pages:
            documents.extend(splitter.split_documents([page]))
    return documents


def main():
    """Chroma 벡터스토어 구축 후 retriever 반환"""
    docs = load_documents()
    print(f"📄 문서 청크 수: {len(docs)}  / 임베딩 생성 중 …")

    vector_store = Chroma.from_documents(
        documents=docs,
        embedding=embedding_function,
        collection_name="criminal_law",
        persist_directory=str(PERSIST_DIR),
    )
    vector_store.persist()
    print("✅ Chroma 인덱스 저장 완료")

    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    return retriever


def get_retriever(k: int, search_type: str):
    vector_store = Chroma(
        persist_directory=str(PERSIST_DIR),
        embedding_function=embedding_function,
        collection_name="criminal_law",
    )
    search_kwargs = {"k": k}
    if search_type == "mmr":
        # MMR일 때만 기본 하이퍼파라미터 적용
        search_kwargs.update({"fetch_k": max(20, k * 5), "lambda_mult": 0.7})
    return vector_store.as_retriever(search_type=search_type, search_kwargs=search_kwargs)


if __name__ == "__main__":
    main()
