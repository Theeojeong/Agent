"""langchain.py

한국 형법·형사소송법 PDF → 텍스트 분할 → OpenAI 임베딩(text-embedding-small) → Chroma 벡터스토어 구축

이 스크립트는 기존 build_kb.py 를 대체한다. 실행 후
    data/processed/chroma/  아래에 벡터 인덱스가 저장된다.
"""
from pathlib import Path

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma


DOC_DIR = Path("documents")
PDF_FILES = [
    DOC_DIR / "형법(법률).pdf",
    DOC_DIR / "형사소송법(법률).pdf",
]
PERSIST_DIR = Path("data/processed/chroma")
PERSIST_DIR.mkdir(parents=True, exist_ok=True)

# LangChain 컴포넌트
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1500,
    chunk_overlap=100,
    separators=["\n\n", "\n", " "]
)
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")



def load_documents() -> list:
    """PDF 파일을 로드하여 텍스트 청크 리스트 반환"""
    documents = []
    for pdf_path in PDF_FILES:
        if not pdf_path.exists():
            raise FileNotFoundError(f"❌ {pdf_path} 가 존재하지 않습니다. PDF 를 documents/ 폴더에 넣어주세요.")

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
        persist_directory=str(PERSIST_DIR)
    )
    vector_store.persist()
    print(f"✅ Chroma 인덱스 저장 완료 → {PERSIST_DIR}")
    return vector_store.as_retriever(search_kwargs={"k": 3})


if __name__ == "__main__":
    build_db()
