# AI 브랜드 아이덴티티 생성기

AI를 활용해 브랜드 브리프를 바탕으로 브랜드 이름, 슬로건, 브랜드 스토리, 컬러 팔레트, 로고 컨셉 등을 생성하는 Python CLI 프로그램입니다.

## 프로젝트 소개

사용자가 JSON 형식의 브랜드 브리프를 입력하면 Codyssey API를 활용해 브랜드 아이덴티티를 생성합니다.

생성된 텍스트 결과와 이미지 결과는 `output/` 폴더에 저장하며, API 오류가 발생하더라도 가능한 다음 단계로 계속 진행하도록 구성했습니다.

## 🤖 AI 생성 기능

Codyssey API를 활용하여 다음과 같은 브랜드 아이덴티티 요소를 생성합니다.

- 브랜드 네이밍
  - 한국어 이름 3개
  - 영어 이름 3개
  - 각 이름의 의미
- 슬로건 3개
- 브랜드 스토리
  - 기원
  - 철학
  - 비전
- 경쟁사 분석
- 컬러 팔레트
  - 메인 컬러 1개
  - 서브 컬러 3개
- 로고 이미지 3개

## 실행 환경

- Python 3.10+
- Codyssey API Key

## 설치

저장소를 clone한 후 프로젝트 폴더로 이동합니다.

```bash
git clone https://github.com/bomigrace-byte/brand-identity-generator.git
cd brand-identity-generator
```

가상환경을 생성하고 활성화합니다.

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

필요한 패키지를 설치합니다.

```bash
python -m pip install -r requirements.txt
```

## 환경 변수 설정

프로젝트 루트에 `.env` 파일을 생성하고 Codyssey API Key와 API Base URL을 설정합니다.

```env
CODYSSEY_API_KEY=YOUR_API_KEY
CODYSSEY_BASE_URL=YOUR_BASE_URL
```

`.env` 파일은 API Key 보호를 위해 GitHub에 업로드하지 않습니다.

## 입력 브리프

프로그램은 JSON 형식의 브랜드 브리프 파일을 사용합니다.

예시:

```json
{
  "industry": "AI 업무 생산성 서비스",
  "target": "업무 효율을 높이고 싶은 20~40대 직장인",
  "keywords": ["자동화", "효율", "집중", "성장"],
  "tone": "깔끔하고 전문적이며 친근한",
  "competitors": ["Notion", "Todoist"],
  "notes": "AI 서비스답게 세련되면서도 누구나 쉽게 사용할 수 있는 브랜드 이미지를 원함"
}
```

### 필수 항목

- `industry`
- `target`
- `keywords`

### 선택 항목

- `tone`
- `competitors`
- `notes`

## 실행 방법

```bash
python brand_generator.py
```

실행하면 브리프 파일 경로와 출력 폴더 경로를 입력합니다.

```text
🎨 AI 브랜드 아이덴티티 생성기

브리프 파일 경로를 입력하세요: brief.json

출력 폴더 경로를 입력하세요 (엔터 시 ./output):
```

출력 폴더를 입력하지 않으면 기본값으로 `./output`을 사용합니다.

## 🔌 API 처리

### 텍스트 생성

Codyssey의 OpenAI 호환 Chat Completions API를 사용합니다.

`POST /v1/chat/completions`

AI 응답에서 생성된 JSON 문자열을 추출한 후 `json.loads()`와 Pydantic을 이용하여 결과 구조를 검증합니다.

텍스트 생성에는 다음 기능이 사용됩니다.

- 브랜드 네이밍
- 슬로건
- 브랜드 스토리
- 경쟁사 분석
- 컬러 팔레트

### 이미지 생성

Codyssey 이미지 API를 사용합니다.

`POST /api/v1/images`

이미지는 `b64_json` 형식으로 응답받아 Base64 디코딩 후 PNG 파일로 저장합니다.

## 📁 출력 결과

실행이 완료되면 `output/` 폴더에 다음 파일이 생성됩니다.

```text
output/
├── brand_result.json
├── color_palette.png
├── logo_1.png
├── logo_2.png
└── logo_3.png
```

`brand_result.json`에는 입력한 브랜드 브리프와 AI가 생성한 브랜드 아이덴티티 결과가 저장됩니다.

## 오류 처리

각 AI 생성 단계는 `safe_generate()`를 통해 예외를 처리합니다.

API 요청이 실패하면 오류 메시지를 출력하고 해당 결과를 `None`으로 처리한 뒤 다음 단계로 진행합니다.

예:

```text
⚠️ 슬로건 생성 실패: ...
⚠️ 브랜드 스토리 생성 실패: ...
```

이후에도 가능한 다음 단계가 계속 실행되며 최종 결과 JSON을 저장합니다.

또한 AI가 반환한 컬러 값이 정확한 HEX 형식이 아닐 수 있는 상황을 고려하여 컬러 팔레트 이미지 생성 전에 HEX 값을 검증하고 사용할 수 있는 HEX 코드를 추출합니다.

## 프로젝트 구조

```text
brand-identity-generator/
├── brand_generator.py
├── brief.json
├── requirements.txt
├── README.md
├── .env
├── .gitignore
└── output/
    ├── brand_result.json
    ├── color_palette.png
    ├── logo_1.png
    ├── logo_2.png
    └── logo_3.png
```

`.env`와 `.venv/`는 `.gitignore`를 통해 Git에서 제외합니다.

## 🛠 기술 스택

- Python 3.10+
- Codyssey API
- requests
- Pydantic
- Matplotlib
- python-dotenv

## 프로젝트를 통해 학습한 내용

- Python CLI의 기본적인 입력/출력 구조
- JSON 파일 읽기 및 저장
- 환경 변수를 이용한 API Key 관리
- 외부 API를 `requests`로 호출하는 방법
- OpenAI 호환 API의 요청 및 응답 구조 이해
- 구조화된 AI 응답 처리
- Pydantic을 이용한 응답 스키마 정의
- API 예외 처리
- AI 응답 데이터 검증
- Base64 이미지 응답 처리 및 PNG 파일 저장
- Git/GitHub를 이용한 프로젝트 버전 관리

## 참고

Codyssey API의 사용량 제한이나 API 오류에 따라 일부 생성 단계가 실패할 수 있습니다.

이 경우 프로그램은 오류 메시지를 출력하고 가능한 다음 단계로 계속 진행합니다.