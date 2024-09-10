# 파일 설명
- **pyproject.toml**: 프로젝트의 메타데이터(프로젝트 이름, 버전, 설명, 작성자 등)와 의존성(필요한 패키지의 버전 범위 등) 정의
- **poetry.lock**: 프로젝트가 실제로 사용하는 패키지 버전과 그 패키지가 의존하는 하위 패키지 버전 정보(requirements.txt와 동일)
- **.python-version**: 프로젝트 python 가상환경 정보
- **.env**: Naver Open API, Chat GPT API 사용을 위한 key값을 담은 환경변수 파일(불변, 민감 정보)
- **config.yaml**: Naver Open API, Chat GPT API에서 사용하는 검색어, 데이터 필터 정보, 프롬프트 등의 정보를 담은 파일(가변 정보)