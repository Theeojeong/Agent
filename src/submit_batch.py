# src/submit_batch.py
from openai import OpenAI
import time

client = OpenAI()

def create_and_wait(input_path: str = "batch_input.jsonl",
                    output_path: str = "batch_output.jsonl",
                    poll_sec: int = 60):

    # 입력 파일 업로드
    with open(input_path, "rb") as f:
        file_obj = client.files.create(file=f, purpose="batch")
    print("Uploaded input file:", file_obj.id)

    # 배치 작업 생성
    batch = client.batches.create(
        input_file_id=file_obj.id,
        endpoint="/v1/chat/completions",
        completion_window="24h"
    )
    print("배치 ID:", batch.id)

    # 상태 확인
    while True:
        status = client.batches.retrieve(batch.id).status
        print("⌛ 배치 상태 ->", status)
        if status in {"failed", "expired"}:
            raise RuntimeError(f"배치 런타임 에러: {status}")
        if status == "completed":
            break
        time.sleep(poll_sec)

    # 결과 파일 다운로드
    file_id = client.batches.retrieve(batch.id).output_file_id
    content = client.files.content(file_id)
    with open(output_path, "wb") as f:
        for chunk in content.iter_bytes():
            f.write(chunk)
    print(f"✅ 배치 작업 완료 -> {output_path}")

if __name__ == "__main__":
    create_and_wait()
