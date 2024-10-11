# data_utils.py

import json

# JSON 응답에서 raw_text 항목을 추출하는 함수
def extract_raw_text(content):
    try:
        return content.get('raw_text', '')
    except Exception as e:
        print(f"Error extracting raw_text: {e}")
    return ""

# JSON 응답에서 issue 항목을 추출하는 함수
def extract_issues(content):
    try:
        return content.get('issues', [])
    except Exception as e:
        print(f"Error extracting issues: {e}")
    return []

# JSON 응답에서 각 issue에 대한 sentiment 값을 추출하는 함수
def extract_sentiments(content):
    try:
        return content.get('sentiments', {})
    except Exception as e:
        print(f"Error extracting sentiments: {e}")
    return {}

# JSON 응답에서 sentiment_all 값을 추출하는 함수
def extract_sentiment_all(content):
    try:
        return content.get('sentiment_all', '')
    except Exception as e:
        print(f"Error extracting sentiment(all): {e}")
    return ""

# 문자열을 딕셔너리로 변환하는 함수
def convert_to_dict(content):
    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None

# 리스트, 딕셔너리 형태를 문자열로 변환하는 후처리 함수
def clean_format(value):
    if isinstance(value, list):
        return ', '.join(value)
    if isinstance(value, dict):
        return ', '.join([f"{k}: {v}" for k, v in value.items()])
    return value  # 이미 문자열인 경우는 그대로 반환

# 텍스트에 특정 구문이나 해시태그가 포함되어 있는지 확인하는 함수
def contains_exclude_terms(description, phrases, hashtags):
    for phrase in phrases:
        if phrase in description:
            return True
    for hashtag in hashtags:
        if hashtag in description:
            return True
    return False