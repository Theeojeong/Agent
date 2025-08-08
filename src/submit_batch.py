# src/submit_batch.py
from openai import OpenAI
import os
import sys
import time

# 명시적 타임아웃/재시도 설정 (연결 지연으로 무기한 대기 방지)
client = OpenAI(timeout=30.0, max_retries=2)


def create_and_wait(
    input_path: str = "batch_input.jsonl",
    output_path: str = "batch_output.jsonl",
    poll_sec: int = 30,
):

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY 가 설정되어 있지 않습니다 (.env 또는 환경변수 확인)")

    print("[submit] 시작: 입력=", input_path)
    # 1) 입력 파일 업로드
    try:
        print("[submit] 파일 업로드 시도…")
        with open(input_path, "rb") as f:
            file_obj = client.files.create(file=f, purpose="batch")
        print("📤 Uploaded input file:", file_obj.id)
    except Exception as e:
        print("[submit][에러] 파일 업로드 실패:", repr(e))
        raise

    # 2) 배치 작업 생성
    try:
        print("[submit] 배치 생성 시도…")
        batch = client.batches.create(
            input_file_id=file_obj.id,
            endpoint="/v1/chat/completions",
            completion_window="24h",
        )
        print("🆔 Batch ID:", batch.id)
    except Exception as e:
        print("[submit][에러] 배치 생성 실패:", repr(e))
        raise

    # 3) 폴링하여 상태 확인
    while True:
        try:
            status = client.batches.retrieve(batch.id).status
            print("⌛ Current status:", status)
        except Exception as e:
            print("[submit][경고] 상태 조회 실패 (재시도 대기):", repr(e))
            time.sleep(poll_sec)
            continue

        if status in {"failed", "expired"}:
            raise RuntimeError(f"Batch ended with status: {status}")
        if status == "completed":
            break
        time.sleep(poll_sec)

    # 4) 결과 파일 다운로드
    try:
        file_id = client.batches.retrieve(batch.id).output_file_id
        print("[submit] 결과 파일 ID:", file_id)
        content = client.files.content(file_id)
        with open(output_path, "wb") as f:
            for chunk in content.iter_bytes():
                f.write(chunk)
        print(f"✅ Batch completed. Output saved to {output_path}")
    except Exception as e:
        print("[submit][에러] 결과 다운로드 실패:", repr(e))
        raise


if __name__ == "__main__":
    try:
        create_and_wait()
    except Exception as e:
        print("[submit][중단]", repr(e))
        sys.exit(1)
