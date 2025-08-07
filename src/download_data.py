from huggingface_hub import login
from datasets import load_dataset
from pathlib import Path
import os

# HF_TOKEN 이 설정된 경우에만 로그인
_token = os.getenv("HF_TOKEN")
if _token:
    login(_token)

def main():
    dataset = load_dataset(
        "HAERAE-HUB/KMMLU",
        name="Criminal-Law",
        split="test"
    )
    output = Path("data/raw/kmmlu_test.parquet")
    output.parent.mkdir(parents=True, exist_ok=True)
    dataset.to_parquet(output)
    print(f"✅ {output}에 저장 완료.")

if __name__ == "__main__":
    main()
