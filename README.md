# 고객 경험(CX) 분석 솔루션 개발을 위한 데이터 가공 및 분석
이 프로젝트는 2024 데이터바우처 사업을 통해 진행되었습니다. LLM을 이용하여 텍스트 분석을 수행하는 것이 목적입니다.
## 수행 내용
- 핵심 구문 추출(Key Phrase Extraction)
  - 결과물: issue
- 감성 분석(Sentiment Analysis)
  - 결과물: sentiment, sentiment_all
- 군집 분석(Clustering Analysis)
  - 결과물: theme, tid
- 기회영역값 도출(Opportunity Score Extraction)
  - 결과물: issue별 긍정, 부정, 중립 개수

## 공개여부
private 프로젝트로 공개되지 않았습니다. 공급기업과 수요기업에만 공개합니다.

## 설치 방법
1. python 3.10.13버전
2. git clone 또는 zip 파일 형태 다운로드
3. poetry install

## 사용 방법
```bash
python integ_gpt_analysis.py [파일경로] [컬럼명] [결과파일명]
```
![image](https://github.com/user-attachments/assets/af936d89-5678-4b93-84ae-02ce40eb8ce2)

폴더 내 result 폴더가 생성되며 결과파일명으로 저장됩니다.

## 기타
- csv 타입의 텍스트 데이터에 적용 가능합니다.
- openai chat gpt api와 통신합니다.
- 새로운 도메인/데이터 적용 시 prompt는 새롭게 작성해야 합니다.
