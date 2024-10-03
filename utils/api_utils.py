# api_utils.py

import requests

# 네이버 API에서 데이터를 가져오는 함수
def fetch_data(target, query, start, display, sort):
    url = api_address + target + "." + format
    params = {
        "query": query,
        "display": display,
        "sort": sort,
        "start": start
    }
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error Code: {response.status_code}")
        return None

# 텔레그램 봇 알림 전송 함수
def telegram_alert():
    try:
        # 텔레그램 bot으로 알림
        response = requests.get(f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text=완료", timeout=10)
        print("============================================")
        if response.status_code == 200:
            print('메시지가 성공적으로 전송되었습니다.')
        else:
            print('메시지 전송 실패:', response.text)
    except requests.exceptions.RequestException as e:
        print(f"에러 발생: {e}")

# GPT-4 모델을 통해 응답을 받는 함수
# todo: model, temperature, stream 등의 파라미터를 config.yaml 파일로 관리
def get_response(messages, model: str, temperature: , stream):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            # max_tokens=150,
            temperature=0.5,
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"An error occurred: {e}")
        return None