# src/submit_batch.py
from openai import OpenAI
import time

client = OpenAI()                       # OPENAI_API_KEY 환경변수 필요

def create_and_wait(input_path: str = "batch_input.jsonl",
                    output_path: str = "batch_output.jsonl",
                    poll_sec: int = 60):
    """OpenAI Batch API 제출 후 완료까지 대기, 결과 파일 다운로드"""

    # 1) 입력 파일 업로드
    with open(input_path, "rb") as f:
        file_obj = client.files.create(file=f, purpose="batch")
    print("📤 Uploaded input file:", file_obj.id)

    # 2) 배치 작업 생성
    batch = client.batches.create(
        input_file_id=file_obj.id,
        endpoint="/v1/chat/completions",
        completion_window="24h"
    )
    print("🆔 Batch ID:", batch.id)

    # 3) 폴링하여 상태 확인
    while True:
        status = client.batches.retrieve(batch.id).status
        print("⌛ Current status:", status)
        if status in {"failed", "expired"}:
            raise RuntimeError(f"Batch ended with status: {status}")
        if status == "completed":
            break
        time.sleep(poll_sec)

    # 4) 결과 파일 다운로드
    file_id = client.batches.retrieve(batch.id).output_file_id
    content = client.files.content(file_id)
    with open(output_path, "wb") as f:
        for chunk in content.iter_bytes():
            f.write(chunk)
    print(f"✅ Batch completed. Output saved to {output_path}")

if __name__ == "__main__":
    create_and_wait()
