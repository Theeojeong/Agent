import json, pandas as pd

def load_answers():
    df = pd.read_parquet("data/raw/kmmlu_test.parquet")
    return dict(zip(df["index_id"].astype(str), df["answer"]))  # "0":"A", ...

def main():
    gold = load_answers()
    correct = total = 0
    with open("batch_output.jsonl", encoding="utf-8") as f:
        for line in f:
            out = json.loads(line)
            idx = out["custom_id"]
            pred = (
                out["response"]["choices"][0]["message"]["content"]
                .strip().upper()[0]
            )  # 'A' ...
            if pred == gold[idx]:
                correct += 1
            total += 1
    acc = correct / total * 100
    print(f"KMMLU Criminal-Law accuracy: {acc:.2f}%")

    # 리포트 파일 저장
    with open("report.txt", "w") as f:
        f.write(f"Accuracy: {acc:.2f}%\n")
    print("✅ saved report.txt")

if __name__ == "__main__":
    main()