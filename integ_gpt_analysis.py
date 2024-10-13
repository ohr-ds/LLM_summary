# 패키지 불러오기
import os
import time
import yaml
import re
import json
import requests
import pickle
import argparse
from api_utils import *
from openai import OpenAI
import pandas as pd
import numpy as np
import ipywidgets as widgets # interactive display
from tqdm import tqdm # progress bar
from dotenv import load_dotenv
from collections import defaultdict

'''
*사용 예시: python integ_gpt_analysis.py data/제공/제공_네이버쇼핑리뷰.csv 내용 제공_네이버쇼핑리뷰
결과: 
result/에 S1_감성분석_제공_네이버쇼핑리뷰.pkl
result/에 S1_감성분석_제공_네이버쇼핑리뷰.xlsx
result/에 S2_감성테마_제공_네이버쇼핑리뷰.pkl
result/에 S2_감성테마_제공_네이버쇼핑리뷰.xlsx
result/에 S3_기회영역값_제공_네이버쇼핑리뷰.xlsx
'''

'''
args.file_path = 'data/제공/제공_네이버쇼핑리뷰.csv'
args.column_name = '내용'
args.output = '제공_네이버쇼핑리뷰'
'''

# input 파일명, 컬럼이름 파싱
parser = argparse.ArgumentParser(description='CSV 파일 경로와 컬럼 이름을 입력받기')
parser.add_argument('file_path', type=str, help='CSV 파일 경로')
parser.add_argument('column_name', type=str, help='분석할 컬럼 이름')
parser.add_argument('output', type=str, help='결과 파일 이름')
args = parser.parse_args()

# .env 파일에서 환경 변수 로드(API 키)
load_dotenv()

# YAML 파일 열기
yaml_path = 'config.yaml'
with open(yaml_path, 'r') as f:
    config = yaml.safe_load(f)

# gpt prompt 설정
sentiment_instructions = config['gptapi']['sentiment']['instructions']
sentiment_few_shots = config['gptapi']['sentiment']['few_shot_examples']
theme_instructions = config['gptapi']['theme']['instructions']
theme_few_shots = config['gptapi']['theme']['few_shot_examples']

# OpenAI API 클라이언트 생성
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

####################################################
# Step 0) 데이터 선택
####################################################
df = pd.read_csv(args.file_path)

####################################################
## Step 1) 핵심 구문 추출(Key Phrase Extraction)&감정 분석(Sentiment Analysis)
####################################################

text_apply = df[args.column_name]

# 응답들을 저장할 리스트
content_list = []

total_iterations = len(text_apply)
print("핵심 구문 추출&감정 분석 진행 중...")
with tqdm(total=total_iterations) as pbar:
    for i, text in enumerate(text_apply):

        # (Step 1) 각 raw_text에 대해 issue와 sentiment 추출
        input_raw_text = text
        system_message = {"role": "system", "content": sentiment_instructions}
        user_message = {"role": "user", "content": f"{sentiment_few_shots}\n<raw_text>\n{input_raw_text}\n</raw_text>"}
        messages = [system_message, user_message]

        # GPT-4로부터 응답 받기
        content = get_response(client, messages)
        if not content:
            pbar.update(1)
            time.sleep(1)
            continue
        
        # 응답을 리스트에 저장
        content_list.append((content, input_raw_text))
        
        pbar.update(1)
        time.sleep(1)

# 답변 dataframe 변환

data_list = []

for content, original_raw_text in content_list:
    parsed_content = convert_to_dict(content)

    raw_text = extract_raw_text(parsed_content)
    if raw_text == "": # raw_text가 비어있는 경우 원본 텍스트로 대체
        raw_text = original_raw_text
    issues = extract_issues(parsed_content) if parsed_content else []
    sentiments = extract_sentiments(parsed_content) if parsed_content else {}
    sentiment_all = extract_sentiment_all(parsed_content) if parsed_content else ""

    for issue in issues:
        sentiment = sentiments.get(issue, 'Unknown')
        data_entry = {
            "raw_text": raw_text,
            "issue": issue,
            "sentiment": sentiment,
            "sentiment_all": sentiment_all
        }
        data_list.append(data_entry)

result_s1 = pd.DataFrame(data_list)

# result 폴더 없을 경우 생성
if not os.path.exists('result'):
    os.makedirs('result')

output_name_s1 = f"S1_감성분석_{args.output}"
output_name_s2 = f"S2_감성테마_{args.output}"
output_name_s3 = f"S3_기회영역값_{args.output}"

# 결과 중간 저장
result_s1.to_pickle(f"result/{output_name_s1}.pkl")
result_s1.to_excel(f"result/{output_name_s1}.xlsx", index=False)

####################################################
## Step 2) 군집 분석(Clustering Analysis)
####################################################

# issue에서 중복 제거
unique_issues = result_s1['issue'].drop_duplicates().tolist()

# ### Batch 100

# 유니크한 이슈들을 GPT API로 분류
themes = []
batch_size = 100  # 한번에 너무 많은 데이터를 보내지 않기 위해 배치 처리
print("군집분석 진행 중...")
for i in tqdm(range(0, len(unique_issues), batch_size)):
    batch_issues = unique_issues[i:i+batch_size]
    themes.append(classify_issues(client, theme_instructions, ', '.join(batch_issues), theme_few_shots))

# 각 theme의 key를 추출하여 총 길이를 계산
total_keys_length = sum(len(json.loads(theme).keys()) for theme in themes)
merged_themes = merge_themes(themes)
result_s2 = result_s1.copy()

# 'theme' 컬럼을 생성
result_s2['theme'] = result_s2['issue'].apply(lambda x: find_theme(merged_themes, x))

# tid 생성
# "raw_text" 값에 따른 고유 번호 생성 (0부터 시작).
unique_ids, _ = pd.factorize(result_s2['raw_text']) # 인덱스만 사용하므로 두 번째 반환값은 무시

# "tid" 값 생성 (0001, 0002 형태로 고유 번호 할당)
result_s2['tid'] = ['text' + str(i+1).zfill(4) for i in unique_ids]

# "tid" 컬럼을 "raw_text" 앞에 삽입
result_s2 = result_s2[['tid'] + [col for col in result_s2.columns if col != 'tid']]

# 중간 저장
result_s2.to_pickle(f"result/{output_name_s2}.pkl")
result_s2.to_excel(f"result/{output_name_s2}.xlsx", index=False)

####################################################
## Step 3) 기회영역값 도출(Opportunity Score Extraction)
####################################################
# 'issue'별 'sentiment' 개수 계산 및 'total' 컬럼 추가 후 내림차순 정렬

result_s3 = result_s2.groupby(['issue', 'theme', 'sentiment']).size().unstack(fill_value=0)
result_s3['total'] = result_s3.sum(axis=1)
result_s3 = result_s3.sort_values(by='total', ascending=False)
result_s3 = result_s3.reset_index()

# 엑셀 파일로 저장
result_s3.to_excel(f"result/{output_name_s3}.xlsx", index=False)

print("분석이 완료되었습니다.")
os.system('say "분석이 완료되었습니다."')