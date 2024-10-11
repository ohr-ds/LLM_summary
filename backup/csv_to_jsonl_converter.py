import pandas as pd
import json

# todo: py 파일로 만들기.
def csv_to_jsonl(csv_file_path, jsonl_file_path):
    # CSV 파일 불러오기
    df = pd.read_csv(csv_file_path)

    # JSONL 파일 저장 경로
    jsonl_file_path = jsonl_file_path

    # JSONL로 변환할 때 필요한 시스템 메시지
    system_message = { # todo: config.yaml 파일에서 불러오기
        "role": "system", 
        "content": "넌 글을 요약하는 전문가야. 내용을 입력하면 아래 지시사항에 따라 요약해줘.\n지시사항:\n1. 원문을 입력하면 주요 테마를 추출해줘.\n2. 테마와 관련된 구체적인 이슈나 관심사를 나열해줘.\n3. 테마별 감성 분석 결과를 나열해줘. 각 테마에 대해 매우 긍정, 긍정, 중립, 부정, 매우 부정 중 하나로 표현.\n4. 원문 전체에 대한 감성 분석 결과를 매우 긍정, 긍정, 중립, 부정, 매우 부정 중 하나로 표현.\n5. 결과를 포맷에 맞춰 출력해."
    }

    # 필요한 컬럼만 선택
    columns_to_use = ['raw_text', 'theme', 'issue', 'sentiment', 'sentiment(all)']
    df_filtered = df[columns_to_use]

    # JSONL 파일로 변환
    with open(jsonl_file_path, 'w', encoding='utf-8') as jsonl_file:
        for _, row in df_filtered.iterrows():
            # 각 행의 데이터로 JSON 메시지 구조 생성
            json_record = {
                "messages": [
                    system_message,
                    {"role": "user", "content": f"[원문]\n{row['raw_text']}\n[/원문]"},
                    {"role": "assistant", 
                    "content": f"[원문]\n{row['raw_text']}\n[/원문]\n[theme]\n{row['theme']}\n[/theme]\n[issue]\n{row['issue']}\n[/issue]\n[sentiment]\n{row['sentiment']}\n[/sentiment]\n[sentiment(all)]\n{row['sentiment(all)']}\n[/sentiment(all)]"}
                ]
            }
            # 한 줄씩 JSONL 형식으로 저장
            jsonl_file.write(json.dumps(json_record, ensure_ascii=False) + '\n')
    return f"JSONL 파일이 성공적으로 {jsonl_file_path}에 저장되었습니다."