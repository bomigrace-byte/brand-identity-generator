import os
import json
import base64
import re

import matplotlib.pyplot as plt
import requests
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError
from matplotlib.patches import Rectangle


# =========================
# 결과 데이터 구조
# =========================

class BrandName(BaseModel):
    name: str
    meaning: str


class NamingResult(BaseModel):
    korean: list[BrandName]
    english: list[BrandName]


class SloganResult(BaseModel):
    slogans: list[str]


class BrandStoryResult(BaseModel):
    origin: str
    philosophy: str
    vision: str


class ColorInfo(BaseModel):
    name: str
    hex: str
    meaning: str


class ColorPaletteResult(BaseModel):
    main_color: ColorInfo
    sub_colors: list[ColorInfo]


class CompetitorAnalysis(BaseModel):
    competitor: str
    characteristics: str
    strengths: str


class CompetitorAnalysisResult(BaseModel):
    competitors: list[CompetitorAnalysis]
    differentiation: str


# =========================
# API 설정
# =========================

TEXT_MODEL = "gpt-5-mini"
IMAGE_MODEL = "gpt-image-1-mini"


def load_env():
    load_dotenv()

    api_key = os.getenv("CODYSSEY_API_KEY")
    base_url = os.getenv("CODYSSEY_BASE_URL")

    if not api_key:
        raise ValueError("CODYSSEY_API_KEY가 설정되지 않았습니다.")

    if not base_url:
        raise ValueError("CODYSSEY_BASE_URL이 설정되지 않았습니다.")

    return api_key, base_url.rstrip("/")


# =========================
# 사용자 입력
# =========================

def get_user_input():
    print("🎨 AI 브랜드 아이덴티티 생성기")
    print()

    brief_path = input("브리프 파일 경로를 입력하세요: ")

    output_dir = input(
        "출력 폴더 경로를 입력하세요 (엔터 시 ./output): "
    )

    if not output_dir:
        output_dir = "./output"

    os.makedirs(output_dir, exist_ok=True)

    return brief_path, output_dir


def load_brief(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        brief = json.load(f)

    required_fields = [
        "industry",
        "target",
        "keywords",
    ]

    missing_fields = [
        field
        for field in required_fields
        if field not in brief
    ]

    if missing_fields:
        raise ValueError(
            "브리프에 필수 항목이 없습니다: "
            + ", ".join(missing_fields)
        )

    return brief


# =========================
# Codyssey 텍스트 API
# =========================

def call_codyssey_text(
    api_key,
    base_url,
    system_prompt,
    user_prompt
):
    """
    Codyssey OpenAI 호환 텍스트 API 호출

    POST /v1/chat/completions
    """

    url = f"{base_url}/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": TEXT_MODEL,
        "messages": [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        "max_tokens": 2000,
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=120,
    )

    response.raise_for_status()

    data = response.json()

    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as e:
        raise ValueError(
            f"텍스트 API 응답 형식이 예상과 다릅니다: {data}"
        ) from e


def parse_json_response(text):
    """
    LLM 응답에서 JSON을 추출한다.
    """

    text = text.strip()

    # ```json ... ``` 제거
    if text.startswith("```"):
        text = re.sub(
            r"^```(?:json)?\s*",
            "",
            text
        )
        text = re.sub(
            r"\s*```$",
            "",
            text
        )

    try:
        return json.loads(text)

    except json.JSONDecodeError:
        # 응답 앞뒤에 설명이 붙은 경우
        start = text.find("{")
        end = text.rfind("}")

        if start != -1 and end > start:
            return json.loads(
                text[start:end + 1]
            )

        raise ValueError(
            f"JSON 응답을 파싱할 수 없습니다: {text}"
        )


def generate_structured_result(
    api_key,
    base_url,
    system_prompt,
    user_prompt,
    result_model,
):
    """
    API 호출
    → JSON 파싱
    → Pydantic 검증
    → 실패 시 1회 재질문
    """

    max_retries = 1
    last_error = None

    for attempt in range(max_retries + 1):

        try:
            text = call_codyssey_text(
                api_key,
                base_url,
                system_prompt,
                user_prompt,
            )

            data = parse_json_response(text)

            result = result_model.model_validate(data)

            return result.model_dump()

        except ValidationError as e:

            last_error = (
                f"AI 응답 구조 검증 실패: {e}"
            )

        except ValueError as e:

            last_error = str(e)

        except Exception as e:

            last_error = str(e)

        if attempt < max_retries:

            print(
                "⚠️ AI 응답 검증에 실패했습니다."
            )

            print(
                "🔄 올바른 형식으로 재질문합니다."
            )

            user_prompt = f"""
이전 AI 응답이 요구된 형식 또는 데이터 구조를
만족하지 못했습니다.

발생한 문제:
{last_error}

이전 요청의 조건을 모두 유지하면서
잘못된 부분을 수정하여 다시 작성하세요.

반드시 다음 조건을 지키세요.

1. 유효한 JSON 객체만 반환하세요.
2. Markdown 코드 블록을 사용하지 마세요.
3. JSON 앞뒤에 설명 문장을 추가하지 마세요.
4. 필수 필드를 모두 포함하세요.
5. 이전 요청에서 요구한 개수와 형식을 정확히 지키세요.

원래 요청:
{user_prompt}
"""

    raise ValueError(
        f"AI 응답 생성에 최종 실패했습니다: "
        f"{last_error}"
    )


# =========================
# 브랜드 네이밍
# =========================

def generate_naming(
    api_key,
    base_url,
    brief
):
    system_prompt = """
당신은 전문 브랜드 네이밍 전문가입니다.

브랜드 브리프를 바탕으로 기억하기 쉽고
차별화된 브랜드 이름을 제안하세요.

반드시 JSON 객체만 반환하세요.
Markdown이나 설명 문장은 포함하지 마세요.

JSON 형식:

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
"""

    user_prompt = f"""
다음 브랜드 브리프를 분석하세요.

산업:
{brief["industry"]}

타깃:
{brief["target"]}

키워드:
{brief["keywords"]}

톤:
{brief.get("tone", "")}

경쟁사:
{brief.get("competitors", [])}

추가사항:
{brief.get("notes", "")}

한국어 이름 3개와 영어 이름 3개를 제안하세요.

각 이름에는 이름의 의미를 작성하세요.

반드시 위에서 제시한 JSON 형식만 반환하세요.
"""

    return generate_structured_result(
    api_key,
    base_url,
    system_prompt,
    user_prompt,
    NamingResult,
)


# =========================
# 슬로건
# =========================

def generate_slogans(
    api_key,
    base_url,
    brief
):
    system_prompt = """
당신은 전문 브랜드 카피라이터입니다.

브랜드의 핵심 가치와 타깃을 반영하여
짧고 기억하기 쉬운 슬로건을 만드세요.

반드시 JSON 객체만 반환하세요.

JSON 형식:

{
  "slogans": [
    "슬로건 1",
    "슬로건 2",
    "슬로건 3"
  ]
}
"""

    user_prompt = f"""
다음 브랜드 브리프를 바탕으로
슬로건 3개를 작성하세요.

산업:
{brief["industry"]}

타깃:
{brief["target"]}

키워드:
{brief["keywords"]}

톤:
{brief.get("tone", "")}

추가사항:
{brief.get("notes", "")}
"""

    return generate_structured_result(
        api_key,
        base_url,
        system_prompt,
        user_prompt,
        SloganResult,
    )


# =========================
# 브랜드 스토리
# =========================


def generate_brand_story(
    api_key,
    base_url,
    brief,
    naming
):
    system_prompt = """
당신은 브랜드 전략 및 스토리텔링 전문가입니다.

선택된 대표 브랜드명을 중심으로
브랜드의 기원, 철학, 비전을 자연스럽게 연결하세요.

반드시 JSON 객체만 반환하세요.

JSON 형식:

{
  "origin": "브랜드의 기원",
  "philosophy": "브랜드 철학",
  "vision": "브랜드 비전"
}
"""

    # 대표 브랜드명 선택
    representative_name = ""

    if naming:
        korean_names = naming.get("korean", [])

        if korean_names:
            representative_name = korean_names[0]["name"]

    user_prompt = f"""
다음 브랜드 브리프와 대표 브랜드명을 바탕으로
브랜드 스토리를 작성하세요.

대표 브랜드명:
{representative_name}

산업:
{brief["industry"]}

타깃:
{brief["target"]}

키워드:
{brief["keywords"]}

톤:
{brief.get("tone", "")}

추가사항:
{brief.get("notes", "")}

origin:
대표 브랜드명이 탄생한 배경과
브랜드가 왜 시작되었는지 작성하세요.

philosophy:
브랜드가 중요하게 생각하는 가치와
대표 브랜드명이 전달하는 의미를 연결하여 작성하세요.

vision:
대표 브랜드명이 앞으로 어떤 브랜드로 성장하고 싶은지
구체적으로 작성하세요.

세 부분을 합쳐 약 300자 내외가 되도록 작성하세요.

반드시 위에서 제시한 JSON 형식만 반환하세요.
"""

    return generate_structured_result(
        api_key,
        base_url,
        system_prompt,
        user_prompt,
        BrandStoryResult,
    )


# =========================
# 경쟁사 분석
# =========================

def generate_competitor_analysis(
    api_key,
    base_url,
    brief
):
    competitors = brief.get("competitors", [])

    if not competitors:
        return None

    system_prompt = """
당신은 브랜드 전략 및 경쟁사 분석 전문가입니다.

경쟁사의 특징과 강점을 분석하고
우리 브랜드의 차별화 방향을 제안하세요.

반드시 JSON 객체만 반환하세요.

JSON 형식:

{
  "competitors": [
    {
      "competitor": "경쟁사명",
      "characteristics": "주요 특징",
      "strengths": "주요 강점"
    }
  ],
  "differentiation": "우리 브랜드의 차별화 방향"
}
"""

    user_prompt = f"""
다음 브랜드와 경쟁사를 분석하세요.

산업:
{brief["industry"]}

타깃:
{brief["target"]}

키워드:
{brief["keywords"]}

경쟁사:
{competitors}

톤:
{brief.get("tone", "")}

추가사항:
{brief.get("notes", "")}

각 경쟁사의 특징과 강점을 분석하세요.

마지막으로 우리 브랜드가
어떤 방향으로 차별화하면 좋을지 작성하세요.
"""

    return generate_structured_result(
        api_key,
        base_url,
        system_prompt,
        user_prompt,
        CompetitorAnalysisResult,
    )


# =========================
# 컬러 팔레트
# =========================

def generate_color_palette(
    api_key,
    base_url,
    brief
):
    system_prompt = """
당신은 브랜드 컬러 전략 전문가입니다.

브랜드의 산업, 타깃, 키워드와 톤을 고려하여
브랜드 컬러 팔레트를 제안하세요.

메인 컬러 1개와 서브 컬러 3개를 제안하세요.

각 컬러에는 다음 정보를 포함하세요.

- name: 컬러 이름
- hex: HEX 6자리 색상 코드
- meaning: 브랜드에서 이 컬러를 사용하는 이유

중요:
- hex는 반드시 #으로 시작하는 6자리 HEX 코드만 작성하세요.
- 색상명이나 설명을 hex 값에 붙이지 마세요.

예:

{
  "name": "Ocean Teal",
  "hex": "#0EA5A9",
  "meaning": "신뢰감과 혁신적인 이미지를 전달"
}

반드시 JSON 객체만 반환하세요.

JSON 형식:

{
  "main_color": {
    "name": "메인 컬러 이름",
    "hex": "#2563EB",
    "meaning": "메인 컬러 선정 이유"
  },
  "sub_colors": [
    {
      "name": "서브 컬러 이름",
      "hex": "#DBEAFE",
      "meaning": "서브 컬러 선정 이유"
    },
    {
      "name": "서브 컬러 이름",
      "hex": "#1E3A8A",
      "meaning": "서브 컬러 선정 이유"
    },
    {
      "name": "서브 컬러 이름",
      "hex": "#F8FAFC",
      "meaning": "서브 컬러 선정 이유"
    }
  ]
}
"""

    user_prompt = f"""
다음 브랜드 브리프를 바탕으로
브랜드 컬러 팔레트를 제안하세요.

산업:
{brief["industry"]}

타깃:
{brief["target"]}

키워드:
{brief["keywords"]}

톤:
{brief.get("tone", "")}

추가사항:
{brief.get("notes", "")}

메인 컬러 1개와
서브 컬러 3개를 제안하세요.

각 컬러의 이름과 HEX 코드,
그리고 브랜드 관점에서의 선정 이유를 작성하세요.

반드시 위에서 제시한 JSON 형식만 반환하세요.
"""

    return generate_structured_result(
        api_key,
        base_url,
        system_prompt,
        user_prompt,
        ColorPaletteResult,
    )


# =========================
# 컬러 팔레트 이미지
# =========================

def palette_to_image(
    color_palette,
    output_dir
):
    colors = [
        color_palette["main_color"],
        *color_palette["sub_colors"],
    ]

    valid_colors = []

    for color in colors:
        hex_color = color["hex"]

        match = re.search(
            r"#[0-9A-Fa-f]{6}",
            hex_color
        )

        if not match:
            raise ValueError(
                f"유효하지 않은 HEX 색상값: {hex_color}"
            )

        valid_colors.append({
            "name": color["name"],
            "hex": match.group().upper(),
            "meaning": color["meaning"],
        })

    plt.rcParams["font.family"] = "Malgun Gothic"
    plt.rcParams["axes.unicode_minus"] = False

    fig, ax = plt.subplots(
        figsize=(10, 3)
    )

    for i, color in enumerate(valid_colors):
        ax.add_patch(
            Rectangle(
                (i, 0),
                1,
                1,
                color=color["hex"],
            )
        )

        ax.text(
            i + 0.5,
            0.5,
            f"{color['name']}\n{color['hex']}",
            ha="center",
            va="center",
            fontsize=10,
            color="black",
        )

    ax.set_xlim(
        0,
        len(valid_colors)
    )

    ax.set_ylim(0, 1)

    ax.axis("off")

    output_dir = os.path.abspath(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.normpath(
        os.path.join(
            output_dir,
            "color_palette.png"
        )
    )

    fig.savefig(
        output_path,
        bbox_inches="tight",
        pad_inches=0,
    )

    plt.close(fig)

    return output_path



# =========================
# 로고 이미지 생성
# =========================

def generate_logos(
    api_key,
    base_url,
    brief,
    output_dir,
    naming
):
    """
    Codyssey 이미지 API

    POST /api/v1/images
    response_format = b64_json
    """

    url = f"{base_url}/api/v1/images"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    representative_name = ""

    if naming:
        korean_names = naming.get("korean", [])

        if korean_names:
            representative_name = korean_names[0]["name"]

    if not representative_name:
        raise ValueError(
            "대표 브랜드명이 없어 로고를 생성할 수 없습니다."
        )    

    base_prompt = f"""
    Create a professional brand logo concept.

Brand name:
{representative_name}

Industry:
{brief["industry"]}

Target:
{brief["target"]}

Keywords:
{brief["keywords"]}

Tone:
{brief.get("tone", "")}

Notes:
{brief.get("notes", "")}

Requirements:
- Reflect the brand name and brand identity
- Clean and modern
- Simple and memorable
- Suitable for a digital brand
- Professional visual identity
- Avoid excessive detail
- Clean background
- Focus on the logo concept
"""

    logo_paths = []

    for i in range(1, 4):
        prompt = (
            base_prompt
            + f"""
This is logo concept #{i}.
Make this concept visually distinct from the others.
"""
        )

        payload = {
            "model": IMAGE_MODEL,
            "prompt": prompt,
            "size": "1024x1024",
            "response_format": "b64_json",
        }

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=180,
        )

        response.raise_for_status()

        data = response.json()

        try:
            image_b64 = (
                data["result"]["images"][0]["b64_json"]
            )

        except (
            KeyError,
            IndexError,
            TypeError
        ) as e:
            raise ValueError(
                f"이미지 API 응답 형식이 예상과 다릅니다: {data}"
            ) from e

        # data:image/png;base64,... 형태 대응
        if image_b64.startswith("data:"):
            image_b64 = image_b64.split(
                ",",
                1
            )[1]

        image_data = base64.b64decode(
            image_b64
        )

        output_path = os.path.join(
            output_dir,
            f"logo_{i}.png"
        )

        with open(
            output_path,
            "wb"
        ) as f:
            f.write(image_data)

        logo_paths.append(
            output_path
        )

    return logo_paths


# =========================
# 공통 오류 처리
# =========================

def safe_generate(
    step_name,
    generate_func,
    status,
    errors,
    *args
):
    try:
        result = generate_func(*args)

        if result is None:
            status[step_name] = "skipped"
        else:
            status[step_name] = "success"

        return result
   

    except requests.HTTPError as e:
        response = e.response

        error_message = f"HTTP {response.status_code}"

        print(
            f"⚠️ {step_name} 생성 실패: "
            f"{error_message}"
        )

        try:
            print(
                f"   API 응답: {response.json()}"
            )
        except ValueError:
            print(
                f"   API 응답: {response.text}"
            )

        status[step_name] = "failed"

        errors.append({
            "step": step_name,
            "type": "HTTPError",
            "message": error_message,
        })

        return None

    except Exception as e:

        print(
            f"⚠️ {step_name} 생성 실패: {e}"
        )

        status[step_name] = "failed"

        errors.append({
            "step": step_name,
            "type": type(e).__name__,
            "message": str(e),
        })

        return None

# =========================
# 결과 저장
# =========================

def save_result(
    result,
    output_dir
):
    output_path = os.path.join(
        output_dir,
        "brand_result.json"
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            result,
            f,
            ensure_ascii=False,
            indent=2,
        )

    return output_path


# =========================
# 프로그램 실행
# =========================

if __name__ == "__main__":

    status = {}
    errors = []

    try:
        api_key, base_url = load_env()

        brief_path, output_dir = (
            get_user_input()
        )

        brief = load_brief(
            brief_path
        )

    except Exception as e:
        print(
            f"❌ 프로그램을 시작할 수 없습니다: {e}"
        )
        raise SystemExit(1)

    print()
    print(
        "🚀 브랜드 아이덴티티 생성을 시작합니다."
    )
    print()

    naming = safe_generate(
        "브랜드 네이밍",
        generate_naming,
        status,
        errors,
        api_key,
        base_url,
        brief,
    )

    slogans = safe_generate(
        "슬로건",
        generate_slogans,
        status,
        errors,
        api_key,
        base_url,
        brief,
    )

    brand_story = safe_generate(
        "브랜드 스토리",
        generate_brand_story,
        status,
        errors,
        api_key,
        base_url,
        brief,
        naming,
)

    competitor_analysis = safe_generate(
        "경쟁사 분석",
        generate_competitor_analysis,
        status,
        errors,
        api_key,
        base_url,
        brief,
    )

    color_palette = safe_generate(
        "컬러 팔레트",
        generate_color_palette,
        status,
        errors,
        api_key,
        base_url,
        brief,
    )

    palette_path = None

    if color_palette:
        palette_path = safe_generate(
            "컬러 팔레트 이미지",
            palette_to_image,
            status,
            errors,
            color_palette,
            output_dir,
        )

    logo_paths = safe_generate(
        "로고",
        generate_logos,
        status,
        errors,
        api_key,
        base_url,
        brief,
        output_dir,
        naming,
    )

    if logo_paths is None:
        logo_paths = []

    result = {
        "brief": brief,
        "naming": naming,
        "slogans": slogans,
        "brand_story": brand_story,
        "competitor_analysis": competitor_analysis,
        "color_palette": color_palette,
        "color_palette_image": palette_path,
        "logos": logo_paths,
        "status": status,
        "errors": errors,
    }

    result_path = save_result(
        result,
        output_dir
    )

    print()
    print("=" * 50)

    steps = {
        "브랜드 네이밍": naming is not None,
        "슬로건": slogans is not None,
        "브랜드 스토리": brand_story is not None,
        "경쟁사 분석": competitor_analysis is not None,
        "컬러 팔레트": color_palette is not None,
        "컬러 팔레트 이미지": palette_path is not None,
        "로고": bool(logo_paths),
    }

    success_count = sum(steps.values())
    total_count = len(steps)

    if success_count == total_count:
        print("🎉 브랜드 아이덴티티 생성이 완료되었습니다.")
    else:
        print(
            f"⚠️ 브랜드 아이덴티티 생성이 일부 완료되었습니다. "
            f"({success_count}/{total_count})"
        )

        print()
        print("생성 결과:")

        for step_name, success in steps.items():
            display_status = "✅ 성공" if success else "❌ 실패"
            print(f"  {display_status} {step_name}")

    print("=" * 50)

    if naming:
        print()
        print("🏷️ 브랜드 네이밍")

        for item in naming["korean"]:
            print(
                f"  - {item['name']}: "
                f"{item['meaning']}"
            )

        for item in naming["english"]:
            print(
                f"  - {item['name']}: "
                f"{item['meaning']}"
            )

    if slogans:
        print()
        print("💬 슬로건")

        for slogan in slogans["slogans"]:
            print(f"  - {slogan}")

    if brand_story:
        print()
        print("📖 브랜드 스토리")
        print(
            f"  기원: {brand_story['origin']}"
        )
        print(
            f"  철학: {brand_story['philosophy']}"
        )
        print(
            f"  비전: {brand_story['vision']}"
        )

    if competitor_analysis:
        print()
        print("🔎 경쟁사 분석")

        for competitor in competitor_analysis[
            "competitors"
        ]:
            print(
                f"  - {competitor['competitor']}"
            )
            print(
                f"    특징: "
                f"{competitor['characteristics']}"
            )
            print(
                f"    강점: "
                f"{competitor['strengths']}"
            )

        print(
            f"  차별화: "
            f"{competitor_analysis['differentiation']}"
        )

    if color_palette:
        print()
        print("🎨 컬러 팔레트")

        main_color = color_palette["main_color"]

        print(
            f"  메인: "
            f"{main_color['name']} "
            f"({main_color['hex']})"
        )

        print(
            f"    의미: "
            f"{main_color['meaning']}"
        )

        print("  서브:")

        for color in color_palette["sub_colors"]:
            print(
                f"    - {color['name']} "
                f"({color['hex']})"
            )
            print(
                f"      의미: "
                f"{color['meaning']}"
            )

        print()
        print(
            f"📁 최종 결과 저장: {result_path}"
        )

    if palette_path:
        print(
            f"🖼️ 컬러 팔레트 이미지: "
            f"{palette_path}"
        )

    for logo_path in logo_paths:
        print(
            f"🖼️ 로고: {logo_path}"
        )