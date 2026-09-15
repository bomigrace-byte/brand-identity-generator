# 🎨 AI 브랜드 아이덴티티 생성기

브랜드 브리프를 입력하면 Codyssey API의 LLM과 이미지 생성 API를 활용하여 **브랜드 네이밍, 슬로건, 브랜드 스토리, 경쟁사 분석, 컬러 팔레트, 로고**를 자동으로 생성하는 Python 기반 CLI 프로그램입니다.

생성된 텍스트 결과는 구조화된 JSON으로 검증하고, 컬러 팔레트는 이미지로 시각화하며, 로고 이미지는 PNG 파일로 저장합니다.

또한 각 생성 단계에서 발생한 오류와 성공/실패 상태를 `brand_result.json`에 기록하여 일부 단계에서 오류가 발생하더라도 전체 프로세스를 중단하지 않고 다음 단계로 계속 진행할 수 있도록 구성했습니다.

---

## 1. 주요 기능

### 🏷️ 브랜드 네이밍

* 한국어 브랜드명 3개 생성
* 영어 브랜드명 3개 생성
* 각 브랜드명의 의미 제공

### 💬 슬로건

* 브랜드의 핵심 가치와 타깃을 반영한 슬로건 3개 생성

### 📖 브랜드 스토리

* 브랜드 기원
* 브랜드 철학
* 브랜드 비전

### 🔎 경쟁사 분석

* 경쟁사의 주요 특징
* 경쟁사의 강점
* 우리 브랜드의 차별화 방향

※ 브리프에 경쟁사가 입력되지 않은 경우 해당 단계는 `skipped` 상태로 처리합니다.

### 🎨 컬러 팔레트

* 메인 컬러 1개
* 서브 컬러 3개
* 컬러명
* HEX 코드
* 컬러 선정 이유

### 🖼️ 컬러 팔레트 시각화

* 생성된 HEX 색상값을 검증
* Matplotlib을 이용하여 컬러 팔레트 이미지 생성
* `color_palette.png`로 저장

### 🖼️ 로고 생성

* 이미지 생성 API를 이용하여 로고 컨셉 3개 생성
* Base64 이미지 데이터를 PNG 파일로 변환
* `logo_1.png`, `logo_2.png`, `logo_3.png`로 저장

---

# 2. 전체 실행 흐름

프로그램은 **브랜드 브리프 → AI 생성 → 응답 검증 → 결과 저장 및 시각화** 순서로 동작합니다.

```text
브랜드 브리프 입력
        ↓
브리프 JSON 로드 및 필수 항목 검증
        ↓
────────────────────────────
   텍스트 생성 단계
────────────────────────────
        ↓
LLM API 호출
        ↓
JSON 응답 추출 및 파싱
        ↓
Pydantic 구조 검증
        ↓
검증 실패?
   ┌────┴────┐
   ↓         ↓
  YES        NO
   ↓         ↓
재질문 1회   결과 반환
   ↓
LLM 재응답
   ↓
JSON 파싱 및 재검증
        ↓
생성 결과 반환
        ↓
────────────────────────────
   후처리 단계
────────────────────────────
        ↓
컬러 HEX 값 검증
        ↓
컬러 팔레트 이미지 생성
        ↓
이미지 API 호출
        ↓
Base64 → PNG 변환
        ↓
각 단계의 status / errors 기록
        ↓
brand_result.json 저장
```

---

# 3. 생성 단계와 데이터 전달 구조

각 생성 단계는 하나의 거대한 프롬프트로 처리하지 않고 기능별 함수로 분리되어 있습니다.

```text
Brand Brief
    │
    ├──→ Naming
    │       │
    │       └──→ 대표 브랜드명
    │                  │
    │                  ├──→ Brand Story
    │                  │
    │                  └──→ Logo
    │
    ├──→ Slogan
    │
    ├──→ Competitor Analysis
    │
    └──→ Color Palette
                │
                └──→ Color Palette Image
```

브랜드 브리프는 각 생성 단계의 공통적인 입력 컨텍스트로 사용합니다.

특히 브랜드 스토리와 로고 생성에서는 앞 단계에서 생성된 **대표 브랜드명**을 다음 단계에 전달하여 브랜드 정체성이 일관되도록 구성했습니다.

---

# 4. 코드 구조와 각 함수의 책임

프로그램은 하나의 Python 파일로 구성되어 있지만, 기능별 책임을 함수 단위로 분리했습니다.

| 함수                               | 책임                             |
| -------------------------------- | ------------------------------ |
| `load_env()`                     | API Key와 Base URL 등 환경변수 확인    |
| `get_user_input()`               | 브리프 파일 경로와 출력 폴더 입력            |
| `load_brief()`                   | 브리프 JSON 로드 및 필수 항목 검증         |
| `call_codyssey_text()`           | Codyssey 텍스트 API 호출            |
| `parse_json_response()`          | LLM 응답에서 JSON 데이터 추출           |
| `generate_structured_result()`   | API 응답 파싱, Pydantic 검증, 재질문 처리 |
| `generate_naming()`              | 브랜드 네이밍 생성                     |
| `generate_slogans()`             | 슬로건 생성                         |
| `generate_brand_story()`         | 브랜드 스토리 생성                     |
| `generate_competitor_analysis()` | 경쟁사 분석 생성                      |
| `generate_color_palette()`       | 컬러 팔레트 생성                      |
| `palette_to_image()`             | 컬러 HEX 검증 및 이미지 시각화            |
| `generate_logos()`               | 이미지 API 호출 및 PNG 저장            |
| `safe_generate()`                | 각 단계의 오류 처리 및 상태 기록            |
| `save_result()`                  | 최종 결과 JSON 저장                  |

### 책임 분리 구조

```text
API 통신
└── call_codyssey_text()

응답 처리
└── parse_json_response()

구조 검증 및 재질문
└── generate_structured_result()

콘텐츠 생성
├── generate_naming()
├── generate_slogans()
├── generate_brand_story()
├── generate_competitor_analysis()
└── generate_color_palette()

후처리
├── palette_to_image()
└── generate_logos()

공통 오류 처리
└── safe_generate()

결과 저장
└── save_result()
```

이를 통해 **API 호출, Prompt 작성, 응답 파싱, 데이터 검증, 콘텐츠 생성, 시각화, 저장**의 역할을 구분했습니다.

---

# 5. Prompt 설계

각 AI 생성 단계에서는 해당 역할에 맞는 Prompt를 별도로 구성합니다.

Prompt는 크게 **Persona / 생성 목적 / Brand Brief / 제약 조건 / 출력 형식**으로 구성됩니다.

## 5-1. Persona

System Prompt에서 AI에게 해당 작업의 전문 역할을 부여합니다.

예:

```text
당신은 전문 브랜드 네이밍 전문가입니다.
```

또는

```text
당신은 브랜드 전략 및 스토리텔링 전문가입니다.
```

```text
당신은 브랜드 컬러 전략 전문가입니다.
```

이처럼 생성 작업에 따라 역할을 다르게 지정합니다.

---

## 5-2. Brand Brief

User Prompt에는 브랜드의 공통 정보를 전달합니다.

```text
산업
타깃
키워드
톤
경쟁사
추가사항
```

이를 통해 각각의 생성 단계가 동일한 브랜드 정보를 기반으로 결과를 생성하도록 합니다.

---

## 5-3. Tone & Manner

브랜드 브리프에 입력된 `tone` 정보를 각 생성 Prompt에 전달하여 브랜드가 원하는 분위기와 표현 방향을 반영합니다.

예를 들어 세련되고 친근한 브랜드라면 네이밍, 스토리, 컬러 등의 결과에서도 해당 방향성을 유지하도록 합니다.

---

## 5-4. 생성 조건 및 제약

각 단계에서 필요한 결과의 개수와 형식을 명확하게 지정합니다.

예:

```text
한국어 이름 3개와 영어 이름 3개를 제안하세요.
```

컬러 생성에서는:

```text
메인 컬러 1개와 서브 컬러 3개를 제안하세요.
```

또한 텍스트 생성 결과는 구조화된 JSON 형식으로 반환하도록 요구합니다.

---

## 5-5. JSON 출력 형식

LLM의 자유로운 텍스트 응답을 그대로 사용하지 않고, 각 결과에 맞는 JSON 구조를 Prompt에 명시합니다.

예:

```json
{
  "korean": [
    {
      "name": "이름",
      "meaning": "이름의 의미"
    }
  ],
  "english": [
    {
      "name": "Name",
      "meaning": "이름의 의미"
    }
  ]
}
```

이후 Python에서 JSON 파싱과 Pydantic 검증을 수행합니다.

---

# 6. Context 공유와 결과 일관성

각 AI 호출을 완전히 독립적으로 처리하지 않고, **브랜드 브리프와 앞 단계의 핵심 결과를 다음 단계에 전달**합니다.

대표적인 예가 브랜드 네이밍입니다.

```text
Brand Brief
    ↓
브랜드 네이밍 생성
    ↓
한국어 대표 브랜드명 선택
    ↓
브랜드 스토리 Prompt에 전달
    ↓
로고 Prompt에도 전달
```

예를 들어 네이밍 결과에서 `일플로우`가 대표 브랜드명으로 선택되면 브랜드 스토리 생성 시:

```text
대표 브랜드명:
일플로우
```

를 Prompt에 포함합니다.

로고 생성에서도 동일한 대표 브랜드명을 사용합니다.

이를 통해 네이밍, 브랜드 스토리, 로고가 서로 다른 브랜드처럼 생성되는 문제를 줄이고 **하나의 브랜드 아이덴티티를 유지**하도록 했습니다.

---

# 7. AI 응답 검증과 재질문

LLM 응답은 항상 원하는 형식으로 반환된다고 보장할 수 없기 때문에 단순히 API 응답을 사용하는 대신 검증 단계를 추가했습니다.

## 검증 과정

```text
LLM 응답
   ↓
JSON 파싱
   ↓
Pydantic 검증
   ↓
성공 → 결과 반환
```

JSON 파싱 또는 구조 검증에 실패하면 즉시 프로그램을 종료하지 않고 **재질문을 1회 수행**합니다.

```text
LLM 응답
   ↓
JSON 파싱 / Pydantic 검증
   ↓
❌ 실패
   ↓
오류 내용 확인
   ↓
"이전 응답의 문제를 수정하여
 올바른 JSON 형식으로 다시 작성"
   ↓
LLM 재요청
   ↓
재검증
   ↓
성공 또는 최종 실패
```

재질문에서는 이전 검증에서 발생한 오류 내용을 함께 전달하고, 기존 요청의 조건을 유지하도록 합니다.

재시도 횟수는 **최대 1회**로 제한하여 무한 반복을 방지합니다.

---

# 8. 오류 처리

각 생성 단계는 `safe_generate()`를 통해 공통적으로 오류를 처리합니다.

```text
생성 함수 실행
      ↓
   성공?
   ↙   ↘
 YES    NO
 ↓       ↓
success  failed
         ↓
       errors 기록
         ↓
       None 반환
         ↓
다음 단계 계속 실행
```

이를 통해 특정 단계의 API 오류가 발생하더라도 전체 프로그램이 중단되지 않습니다.

예를 들어 브랜드 네이밍 API 호출에 실패하더라도 슬로건, 컬러 등 다음 단계는 계속 실행할 수 있습니다.

---

# 9. 오류 이력 저장

각 단계의 성공/실패 상태는 `status`에 저장하고, 발생한 오류는 `errors` 배열에 저장합니다.

예:

```json
{
  "status": {
    "브랜드 네이밍": "success",
    "슬로건": "success",
    "브랜드 스토리": "failed",
    "컬러 팔레트": "success"
  },
  "errors": [
    {
      "step": "브랜드 스토리",
      "type": "HTTPError",
      "message": "HTTP 429"
    }
  ]
}
```

이를 통해 최종 결과 파일만 확인해도 **어느 단계가 성공했는지와 어떤 오류가 발생했는지 확인**할 수 있습니다.

---

# 10. 단계 상태 관리

각 생성 단계는 다음과 같은 상태로 관리합니다.

```text
success
failed
skipped
```

### success

해당 단계가 정상적으로 결과를 생성한 경우입니다.

### failed

API 오류, JSON 파싱 오류, 데이터 구조 검증 오류 등의 이유로 생성에 실패한 경우입니다.

### skipped

해당 단계에 필요한 입력이 없는 경우입니다.

예를 들어 경쟁사가 브리프에 입력되지 않았다면 경쟁사 분석 API를 호출하지 않고 해당 단계를 `skipped`로 처리합니다.

---

# 11. 컬러 데이터 검증 및 시각화

LLM이 생성한 HEX 색상값은 그대로 이미지 생성에 사용하지 않고 Python에서 한 번 더 검증합니다.

```text
LLM 컬러 결과
      ↓
HEX 형식 검사
      ↓
유효한 색상값 확인
      ↓
Matplotlib
      ↓
color_palette.png
```

정규표현식을 이용하여 `#`으로 시작하는 6자리 HEX 색상 코드를 확인합니다.

유효하지 않은 색상값이 들어오면 오류를 발생시키고 `safe_generate()`를 통해 해당 단계의 실패 상태를 기록합니다.

---

# 12. 이미지 생성 처리

로고는 텍스트 생성 API와 별도의 이미지 API를 사용합니다.

```text
브랜드명 + 브랜드 Brief
          ↓
    이미지 Prompt 생성
          ↓
   POST /api/v1/images
          ↓
      Base64 이미지
          ↓
      Base64 Decode
          ↓
       PNG 저장
```

생성된 로고는 다음과 같이 저장됩니다.

```text
output/
├── logo_1.png
├── logo_2.png
└── logo_3.png
```

---

# 13. 최종 결과 저장

모든 생성 단계가 끝나면 결과를 `brand_result.json`에 저장합니다.

```text
output/
├── brand_result.json
├── color_palette.png
├── logo_1.png
├── logo_2.png
└── logo_3.png
```

`brand_result.json`에는 다음 정보가 포함됩니다.

```text
brief
naming
slogans
brand_story
competitor_analysis
color_palette
color_palette_image
logos
status
errors
```

따라서 정상적으로 생성된 결과뿐만 아니라 **각 단계의 처리 상태와 오류 이력까지 하나의 결과 파일에서 확인**할 수 있습니다.

---

# 14. 설치 방법

## Python 환경

Python 3.x 환경에서 실행합니다.

가상환경 사용을 권장합니다.

```bash
python -m venv .venv
```

### Windows

```powershell
.venv\Scripts\activate
```

### 필요한 패키지 설치

```bash
pip install -r requirements.txt
```

`requirements.txt`에는 프로젝트 실행에 필요한 외부 Python 패키지를 기록합니다.

예:

```text
requests
matplotlib
python-dotenv
pydantic
```

---

# 15. 환경변수 설정

프로젝트 루트에 `.env` 파일을 생성합니다.

```env
CODYSSEY_API_KEY=your_api_key
CODYSSEY_BASE_URL=your_base_url
```

API Key는 코드에 직접 작성하지 않고 환경변수로 관리합니다.

---

# 16. 입력 브리프

프로그램 실행 시 브랜드 브리프 JSON 파일의 경로를 입력합니다.

필수 항목:

```json
{
  "industry": "AI 업무 생산성",
  "target": "20~40대 직장인",
  "keywords": [
    "자동화",
    "효율",
    "집중",
    "성장"
  ]
}
```

선택 항목:

```json
{
  "tone": "세련되고 친근한",
  "competitors": [
    "Notion",
    "Todoist"
  ],
  "notes": "AI 기반 업무 자동화 서비스"
}
```

---

# 17. 실행 방법

```bash
python brand_generator.py
```

실행하면:

```text
🎨 AI 브랜드 아이덴티티 생성기

브리프 파일 경로를 입력하세요:
출력 폴더 경로를 입력하세요 (엔터 시 ./output):
```

순서로 입력합니다.

생성이 완료되면 결과가 지정한 출력 폴더에 저장됩니다.

---

# 18. API 처리 방식

## 텍스트 생성 API

Codyssey의 OpenAI 호환 텍스트 API를 사용합니다.

```text
POST /v1/chat/completions
```

Python의 `requests` 라이브러리를 사용하여 API 요청을 보냅니다.

```python
response = requests.post(
    url,
    headers=headers,
    json=payload,
    timeout=120,
)
```

응답을 받은 후:

```text
API Response
    ↓
JSON 추출
    ↓
json.loads()
    ↓
Pydantic model_validate()
    ↓
model_dump()
```

순서로 구조화된 데이터로 변환합니다.

---

## 이미지 생성 API

로고 생성에는 이미지 API를 사용합니다.

```text
POST /api/v1/images
```

API에서 반환된 Base64 데이터를 디코딩하여 PNG 파일로 저장합니다.

---

# 19. 프로젝트 구조

```text
brand-identity-generator/
│
├── brand_generator.py
├── requirements.txt
├── .env
├── README.md
├── input/
│   └── brand_brief.json
│
└── output/
    ├── brand_result.json
    ├── color_palette.png
    ├── logo_1.png
    ├── logo_2.png
    └── logo_3.png
```

---

# 20. 사용 기술

* Python
* Requests
* Pydantic
* Matplotlib
* python-dotenv
* Codyssey Text API
* Codyssey Image API
* JSON
* REST API
* Base64

---

# 21. 주요 학습 내용

이 프로젝트를 통해 다음 내용을 학습하고 적용했습니다.

### Python

* 함수 분리
* 예외 처리
* JSON 파일 처리
* 파일 저장
* 정규표현식
* Base64 디코딩

### API

* REST API 호출
* HTTP POST 요청
* Request Header 구성
* JSON Payload 구성
* API Response 처리
* HTTP 오류 처리

### LLM 활용

* System Prompt와 User Prompt 분리
* Persona 설정
* Brand Brief 전달
* Tone & Manner 적용
* 구조화된 JSON 응답 유도
* JSON 파싱 및 구조 검증
* 검증 실패 시 재질문
* 생성 단계 간 Context 공유

### 데이터 검증

* Pydantic 모델 정의
* LLM 응답 구조 검증
* HEX 색상 데이터 검증

### 오류 처리

* API 오류 처리
* JSON 파싱 오류 처리
* Schema 검증 오류 처리
* 단계별 성공/실패 상태 관리
* 오류 이력 저장
* 일부 단계 실패 후 다음 단계 계속 실행

### 이미지 처리

* Base64 이미지 데이터 처리
* PNG 파일 저장
* Matplotlib을 이용한 컬러 팔레트 시각화

---

# 22. 오류 발생 시 처리 원칙

이 프로그램은 하나의 AI 생성 단계가 실패했다고 해서 전체 작업을 중단하지 않습니다.

```text
네이밍 ❌
   ↓
슬로건 → 계속 실행
   ↓
스토리 → 계속 실행
   ↓
컬러 → 계속 실행
   ↓
로고 → 계속 실행
   ↓
최종 결과 저장
```

단, 특정 단계의 결과가 다음 단계에 반드시 필요한 경우에는 해당 의존성을 고려합니다.

예를 들어 대표 브랜드명이 없는 경우 로고 생성에 사용할 브랜드명이 없으므로 해당 단계에서 오류를 기록합니다.

최종적으로 사용자는 `brand_result.json`의 `status`와 `errors`를 통해 전체 처리 결과를 확인할 수 있습니다.

---

# 23. API 사용량 및 주의사항

이 프로그램은 텍스트 생성 및 이미지 생성 API를 사용하므로 API 사용량이 발생합니다.

특히 로고 생성은 3개의 이미지를 생성하므로 실행 시 이미지 API가 여러 번 호출됩니다.

API 오류 또는 사용량 제한이 발생할 경우 `safe_generate()`가 해당 오류를 처리하고 다음 단계로 진행하며, 최종 오류 내용은 `brand_result.json`의 `errors`에 기록됩니다.

---

# 24. 결과 예시

실행 결과 예시:

```text
🏷️ 브랜드 네이밍
  - 일플로우
  - 집중엔진
  - 효율이음
  - FlowForge
  - Focusly
  - AutoGrow

💬 슬로건
  - 집중을 자동화하다
  - 간단한 자동화, 더 깊은 집중
  - AI로 효율을 켜고 성장을 앞당기다

📖 브랜드 스토리
  기원: ...
  철학: ...
  비전: ...

🎨 컬러 팔레트
  메인: 클래리티 블루 (#2563EB)
  서브: ...

🖼️ 로고
  logo_1.png
  logo_2.png
  logo_3.png
```

---

# 25. 프로젝트 핵심 구조 요약

```text
[Input]
Brand Brief JSON
      ↓
[Generation]
LLM / Image API
      ↓
[Validation]
JSON Parse
      ↓
Pydantic Validation
      ↓
Retry / Re-question
      ↓
[Context]
대표 브랜드명 공유
      ↓
[Post Processing]
HEX 검증 / 컬러 시각화
      ↓
[Error Handling]
status / errors
      ↓
[Output]
brand_result.json
+ PNG 이미지
```

이 구조를 통해 **AI에게 단순히 결과를 요청하는 프로그램을 넘어, AI 응답을 검증하고 오류를 처리하며 생성 단계 간 Context를 연결하는 AI 활용 프로그램**을 구현했습니다.
