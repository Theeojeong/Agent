import json, pandas as pd
import re

def load_answers():
    df = pd.read_parquet("data/raw/kmmlu_test.parquet").reset_index(drop=True)
    print(df)
    # 숫자를 문자로 변환: 1->A, 2->B, 3->C, 4->D
    answer_mapping = {0: 'A', 1: 'B', 2: 'C', 3: 'D'}
    return {str(i): answer_mapping[ans] for i, ans in enumerate(df["answer"])} 

def extract_answer(response_text):
    """응답 텍스트에서 A, B, C, D 중 하나를 추출"""
    # A, B, C, D 중 하나를 찾기 (대소문자 구분 없이)
    match = re.search(r'[ABCD]', response_text.upper())
    if match:
        return match.group()
    return None

def main():
    gold = load_answers()
    correct = total = 0
    with open("batch_output.jsonl", encoding="utf-8") as f:
        for line in f:
            out = json.loads(line)
            idx = out["custom_id"]
            response_text = out["response"]["body"]["choices"][0]["message"]["content"].strip()
            
            # 개선된 답변 추출
            pred = extract_answer(response_text)
            
            if pred and pred == gold[idx]:
                correct += 1
            total += 1
            
            # 디버깅을 위한 출력 (처음 몇 개만)
            if total <= 5:
                print(f"ID {idx}: Gold={gold[idx]}, Pred={pred}, Response='{response_text}'")
    
    acc = correct / total * 100
    print(f"KMMLU Criminal-Law accuracy: {acc:.2f}%")

    # 리포트 파일 저장
    with open("benchmark.txt", "w") as f:
        f.write(f"점수: {acc:.2f}%\n")
    print("✅ saved benchmark.txt")

if __name__ == "__main__":
    main()