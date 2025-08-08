from huggingface_hub import login
from datasets import load_dataset
from pathlib import Path
import os

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
