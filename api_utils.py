# api_utils.py
import json
import pandas as pd
from collections import defaultdict

def get_response(client, messages):
    """
    model: 모델 종류
    messages: 사용자의 입력과 모델의 출력을 교환하는 메시지 목록
    max_tokens: 생성될 응답의 최대 길이
    temperature: 생성될 응답의 다양성(0.0 ~ 1.0) 0.0은 가장 확실한 답변을, 1.0은 가장 다양한 답변을 생성
    stream: 응답을 한 번에 반환할지 여부. False로 설정하면 한 번에 반환
    """
    try:
        # client: OpenAI API 인스턴스
        response = client.chat.completions.create(
            model = "gpt-4o",
            messages = messages,
            # max_tokens = 150,
            temperature = 0.5,
            stream = False)
        return response.choices[0].message.content
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# JSON 응답에서 raw_text 항목을 추출하는 함수
def extract_raw_text(content):
    return content.get('raw_text', '')

# JSON 응답에서 issue 항목을 추출하는 함수
def extract_issues(content):
    return content.get('issue', [])

# JSON 응답에서 각 issue에 대한 sentiment 값을 추출하는 함수
def extract_sentiments(content):
    return content.get('sentiment', {})

# JSON 응답에서 sentiment_all 값을 추출하는 함수
def extract_sentiment_all(content):
    return content.get('sentiment_all', '')

# 문자열을 딕셔너리로 변환하는 함수
def convert_to_dict(content):
    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None
    
# JSON 데이터를 변환하고 추출된 데이터를 DataFrame으로 변환하는 함수
def convert_to_dataframe(content_list):
    data = []
    
    for content in content_list:
        if not content:
            continue  # content가 None이거나 비어 있을 때 건너뜀
        
        content_dict = convert_to_dict(content)
        if not content_dict:
            continue  # JSON 변환에 실패한 경우 건너뜀
        
        raw_text = extract_raw_text(content_dict)
        issues = extract_issues(content_dict)
        sentiments = extract_sentiments(content_dict)
        sentiment_all = extract_sentiment_all(content_dict)
        
        # 각 issue와 sentiment를 별도로 저장
        for issue, sentiment in sentiments.items():
            data.append({
                "raw_text": raw_text,
                "issue": issue,
                "sentiment": sentiment,
                "sentiment_all": sentiment_all
            })
    
    # 데이터가 있을 경우에만 DataFrame 생성
    if data:
        return pd.DataFrame(data)
    else:
        print("No valid data to create DataFrame.")
        return pd.DataFrame()  # 빈 DataFrame 반환
    
def map_issues_to_themes(issues_list, clustering_response):
    themes = []
    for issues in issues_list:
        issue_themes = set()  # 중복을 방지하기 위해 set 사용
        for issue in issues:
            for theme, issue_group in clustering_response.items():
                if issue in issue_group:
                    issue_themes.add(theme)
        themes.append(", ".join(issue_themes))  # 여러 테마가 있을 경우 ","로 결합
    return themes

# 후처리 함수 정의(리스트, 딕셔너리 형태를 문자열로 변환)
def clean_format(value):
    if isinstance(value, list):
        return ', '.join(value)  # 리스트의 경우 ,로 구분하여 문자열로 변환
    if isinstance(value, dict):
        return ', '.join([f"{k}: {v}" for k, v in value.items()])  # 딕셔너리의 경우 key: value 형식으로 변환
    return value  # 이미 문자열인 경우는 그대로 반환

def classify_issues(client, theme_instructions, issues, theme_few_shots):
    # 'instructions'는 모델의 행동 방침을 설정하므로 system 메시지에 포함
    messages = [
        {"role": "system", "content": theme_instructions},
        {"role": "user", "content": f"다음 이슈들을 의미적으로 비슷한 그룹으로 나누고, 각 그룹의 공통 테마를 도출해줘: {issues}"},
        {"role": "user", "content": f"예시: {theme_few_shots}"}
    ]
    
    return get_response(client, messages)

# themes 리스트의 각 JSON 문자열을 dict 형태로 변환하여 병합하는 함수
def merge_themes(themes):
    merged_dict = defaultdict(list)  # 리스트를 기본값으로 갖는 defaultdict 생성

    for theme in themes:
        # JSON 문자열을 Python dict로 변환
        theme_dict = json.loads(theme)
        
        # 각 key와 value를 병합
        for key, values in theme_dict.items():
            for value in values:
                if value not in merged_dict[key]:  # 중복된 value가 없을 경우만 추가
                    merged_dict[key].append(value)
    
    return dict(merged_dict)  # defaultdict을 일반 dict로 변환하여 반환

# 'theme' 컬럼을 생성하는 함수(이슈를 테마로 매핑)
def find_theme(merged_themes, issue):
    for theme, issues in merged_themes.items():
        if issue in issues:
            return theme
    return '기타'  # 해당하는 theme이 없을 경우 '기타'로 표시