# 🎨 AI 브랜드 아이덴티티 생성 CLI

Gemini API를 활용하여 하나의 브랜드 브리프를 기반으로
**브랜드 네이밍, 슬로건, 브랜드 스토리, 경쟁사 분석, 컬러 팔레트, 로고 콘셉트**를 자동으로 생성하는 Python CLI 프로그램입니다.

## 📌 프로젝트 소개

브랜드 기획에 필요한 여러 요소를 하나씩 직접 작성하는 대신,
JSON 형식의 브랜드 브리프를 입력하면 Gemini API를 활용하여 브랜드 아이덴티티 구성 요소를 생성합니다.

생성된 텍스트 결과는 JSON으로 저장하고, 컬러 팔레트와 로고는 PNG 이미지로 저장합니다.

### 주요 기능

* 🇰🇷 한글 브랜드명 3개 생성
* 🌍 영문 브랜드명 3개 생성
* 💬 슬로건 3개 생성
* 📖 브랜드 스토리 생성

  * Origin
  * Philosophy
  * Vision
* 🔎 경쟁사 분석
* 🎨 브랜드 컬러 팔레트 생성

  * 메인 컬러 1개
  * 서브 컬러 2~3개
  * HEX 코드
* 🖼️ 컬러 팔레트 PNG 생성
* ✨ 로고 콘셉트 이미지 3개 생성
* 📦 전체 결과를 `brand_result.json`으로 저장
* ⚠️ API 오류 발생 시 오류 메시지를 출력하고 다음 단계 계속 진행

---

## 🛠️ 사용 기술

* Python 3.10+
* Google Gemini API
* `google-genai`
* Pydantic
* python-dotenv
* Matplotlib

### 사용 모델

* 텍스트 생성: `gemini-3.6-flash`
* 이미지 생성: `gemini-3.1-flash-image`

---

## 📁 프로젝트 구조

```text
brand_generator/
├── brand_generator.py
├── brief.json
├── .env
├── .gitignore
├── requirements.txt
└── output/
```

### 주요 파일

| 파일                   | 설명                   |
| -------------------- | -------------------- |
| `brand_generator.py` | 브랜드 아이덴티티 생성 프로그램    |
| `brief.json`         | 브랜드 생성에 필요한 입력 정보    |
| `.env`               | Gemini API Key 저장    |
| `.gitignore`         | API Key 및 불필요한 파일 제외 |
| `requirements.txt`   | Python 패키지 의존성       |
| `output/`            | 생성 결과 저장 폴더          |

---

## 📋 입력 데이터

`brief.json`에 브랜드 정보를 작성합니다.

```json
{
  "industry": "AI 업무 생산성 서비스",
  "target": "업무 효율을 높이고 싶은 20~40대 직장인",
  "keywords": [
    "자동화",
    "효율",
    "집중",
    "성장"
  ],
  "tone": "깔끔하고 전문적이며 친근한",
  "competitors": [
    "Notion",
    "Todoist"
  ],
  "notes": "AI 서비스답게 세련되면서도 누구나 쉽게 사용할 수 있는 브랜드 이미지를 원함"
}
```

### 필수 항목

* `industry`
* `target`
* `keywords`

### 선택 항목

* `tone`
* `competitors`
* `notes`

---

## 🔑 API Key 설정

프로젝트 폴더에 `.env` 파일을 만들고 Gemini API Key를 설정합니다.

```text
GEMINI_API_KEY=YOUR_API_KEY
```

API Key는 코드에 직접 작성하지 않으며 `.gitignore`를 통해 Git에 포함되지 않도록 설정합니다.

---

## 📦 설치

Python 3.10 이상 환경에서 다음 명령어를 실행합니다.

```bash
pip install -r requirements.txt
```

---

## ▶️ 실행 방법

프로그램을 실행합니다.

```bash
python brand_generator.py
```

실행 후 브리프 파일 경로를 입력합니다.

```text
🎨 AI 브랜드 아이덴티티 생성기

브리프 파일 경로를 입력하세요: brief.json
출력 폴더 경로를 입력하세요 (엔터 시 ./output):
```

출력 폴더를 입력하지 않으면 기본값으로 `./output`을 사용합니다.

---

## 🔄 실행 흐름

```text
brief.json
    ↓
브랜드 정보 입력
    ↓
┌─────────────────────┐
│ Gemini API           │
├─────────────────────┤
│ 한글/영문 네이밍     │
│ 슬로건               │
│ 브랜드 스토리        │
│ 경쟁사 분석          │
│ 컬러 팔레트          │
└─────────────────────┘
    ↓
컬러 팔레트 이미지 생성
    ↓
로고 이미지 3개 생성
    ↓
brand_result.json 저장
```

---

## 📤 출력 결과

정상적으로 실행되면 `output/` 폴더에 다음과 같은 결과가 생성됩니다.

```text
output/
├── brand_result.json
├── color_palette.png
├── logo_1.png
├── logo_2.png
└── logo_3.png
```

### `brand_result.json`

텍스트 기반 결과를 하나의 JSON 파일로 저장합니다.

```text
naming
slogans
brand_story
competitor_analysis
color_palette
logos
```

---

## ⭐ 보너스 기능

### 1. 경쟁사 분석

브리프에 경쟁사를 입력하면 Gemini API를 통해 경쟁사의 특징과 강점을 분석하고, 이를 바탕으로 브랜드 차별화 방향을 제안합니다.

예:

```text
경쟁사
├── Notion
└── Todoist

        ↓

경쟁사 특징 및 강점 분석
        ↓
우리 브랜드 차별화 방향 제안
```

경쟁사가 입력되지 않은 경우 경쟁사 분석 API를 호출하지 않습니다.

### 2. 한글 + 영문 네이밍

하나의 네이밍 생성 과정에서 한글 브랜드명 3개와 영문 브랜드명 3개를 동시에 생성합니다.

각 브랜드명에는 이름의 의미와 작명 의도를 함께 제공합니다.

---

## ⚠️ 오류 처리

Gemini API 호출 중 오류가 발생하더라도 프로그램 전체가 종료되지 않도록 `safe_generate()` 함수를 사용합니다.

```text
API 호출
   ↓
성공 ─────────→ 결과 반환
   │
실패
   ↓
오류 메시지 출력
   ↓
None 반환
   ↓
다음 단계 계속 실행
```

예를 들어 특정 API에서 `503` 또는 `429` 오류가 발생하더라도 이후 단계의 실행과 최종 JSON 저장을 계속 시도합니다.

---

## 💡 프로젝트에서 적용한 AI 활용 방식

이 프로젝트에서 Gemini API는 브랜드 아이덴티티에 필요한 **콘텐츠 생성과 분석**을 담당합니다.

Python은 다음과 같은 작업을 담당합니다.

* 사용자 입력 처리
* JSON 파일 읽기
* Gemini API 호출
* API 응답 구조화
* 오류 처리
* 컬러 팔레트 이미지 생성
* 로고 이미지 파일 저장
* 최종 결과 JSON 저장

즉,

```text
Gemini
→ 생각하고 생성하는 역할

Python
→ API를 연결하고 결과를 처리·저장하는 역할
```

로 역할을 분리했습니다.

---

## 🎯 프로젝트 목표

AI API를 단순히 호출하는 것에 그치지 않고,

**입력 → AI 생성 → 결과 처리 → 이미지 생성 → 파일 저장**

으로 이어지는 하나의 자동화된 CLI 애플리케이션을 구현하는 것을 목표로 했습니다.
