from huggingface_hub import login
from datasets import load_dataset
from pathlib import Path
import pandas as pd
import os

# HF_TOKEN 이 설정된 경우에만 로그인
_token = os.getenv("HF_TOKEN")
if _token:
    login(_token)

def main():
    dataset = load_dataset(
        "HAERAE-HUB/KMMLU",
        name="Criminal-Law",
        split="test"          # 요구사항
    )
    out = Path("data/raw/kmmlu_test.parquet")
    out.parent.mkdir(parents=True, exist_ok=True)
    dataset.to_parquet(out)
    print(f"✅ Saved {len(dataset)} rows → {out}")

if __name__ == "__main__":
    main()
