import os
import json
import matplotlib.pyplot as plt
import base64

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel
from matplotlib.patches import Rectangle

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

class ColorPaletteResult(BaseModel):
    main_color: str
    sub_colors: list[str]

class CompetitorAnalysis(BaseModel):
    competitor: str
    characteristics: str
    strengths: str

class CompetitorAnalysisResult(BaseModel):
    competitors: list[CompetitorAnalysis]
    differentiation: str


def load_env():
    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다.")

    return genai.Client(api_key=api_key)


def get_user_input():
    print("🎨 AI 브랜드 아이덴티티 생성기")
    print()

    brief_path = input("브리프 파일 경로를 입력하세요: ")
    output_dir = input("출력 폴더 경로를 입력하세요 (엔터 시 ./output): ")

    if not output_dir:
        output_dir = "./output"

    os.makedirs(output_dir, exist_ok=True)

    return brief_path, output_dir


def load_brief(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        brief = json.load(f)

    return brief

def safe_generate(step_name, generate_func, *args):
    try:
        return generate_func(*args)
    except Exception as e:
        print(f"⚠️ {step_name} 생성 실패: {e}")
        return None

def generate_competitor_analysis(client, brief):
    competitors = brief.get("competitors", [])

    if not competitors:
        return None

    prompt = f"""
당신은 전문 브랜드 전략 컨설턴트입니다.

다음 브랜드 정보를 바탕으로 경쟁사 분석을 수행해주세요.

업종: {brief["industry"]}
타겟: {brief["target"]}
키워드: {", ".join(brief["keywords"])}
경쟁사: {", ".join(competitors)}
톤앤매너: {brief.get("tone", "자유롭게 제안")}
추가 요청사항: {brief.get("notes", "없음")}

각 경쟁사에 대해 다음 내용을 분석하세요.

1. 주요 특징과 기능
2. 경쟁사의 강점

그리고 모든 경쟁사 분석을 바탕으로
우리 브랜드가 가져갈 수 있는 차별화 방향을 제안하세요.

분석은 실제 브랜드 전략 수립에 도움이 되도록
구체적이고 이해하기 쉽게 작성하세요.

반드시 지정된 JSON 구조로만 응답하세요.
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=CompetitorAnalysisResult
        )
    )

    return json.loads(response.text)

def generate_naming(client, brief):
    prompt = f"""
당신은 전문 브랜드 네이밍 전문가입니다.

다음 브랜드 정보를 바탕으로 브랜드 이름을 만들어주세요.

업종: {brief["industry"]}
타겟: {brief["target"]}
키워드: {", ".join(brief["keywords"])}
톤앤매너: {brief.get("tone", "자유롭게 제안")}
추가 요청사항: {brief.get("notes", "없음")}

한글 브랜드명 3개와 영문 브랜드명 3개를 제안하고,
각 이름의 의미와 작명 의도를 설명해주세요.

브랜드의 업종, 타겟, 키워드, 톤앤매너를 고려하여
기억하기 쉽고 실제 브랜드로 사용할 수 있는 이름을 제안하세요.

반드시 지정된 JSON 구조로만 응답하세요.
"""

    response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents=prompt,
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=NamingResult
    )
)

    return json.loads(response.text)

def generate_slogans(client, brief):
    prompt = f"""
당신은 전문 브랜드 카피라이터입니다.

다음 브랜드 정보를 바탕으로 브랜드 슬로건을 만들어주세요.

업종: {brief["industry"]}
타겟: {brief["target"]}
키워드: {", ".join(brief["keywords"])}
톤앤매너: {brief.get("tone", "자유롭게 제안")}
추가 요청사항: {brief.get("notes", "없음")}

다음 조건을 반드시 지켜주세요.

1. 브랜드의 핵심 가치를 잘 표현하는 슬로건을 3개 생성하세요.
2. 짧고 기억하기 쉬운 문장으로 작성하세요.
3. 타겟 고객이 서비스의 가치를 쉽게 이해할 수 있도록 작성하세요.
4. 서로 다른 방향의 슬로건을 제안하세요.

반드시 지정된 JSON 구조로만 응답하세요.
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=SloganResult
        )
    )

    return json.loads(response.text)



def generate_brand_story(client, brief):
    prompt = f"""
당신은 전문 브랜드 스토리텔러입니다.

다음 브랜드 정보를 바탕으로 브랜드 스토리를 작성해주세요.

업종: {brief["industry"]}
타겟: {brief["target"]}
키워드: {", ".join(brief["keywords"])}
톤앤매너: {brief.get("tone", "자유롭게 제안")}
추가 요청사항: {brief.get("notes", "없음")}

다음 조건을 반드시 지켜주세요.

1. 브랜드 탄생 배경(Origin)을 작성하세요.
2. 브랜드 철학(Philosophy)을 작성하세요.
3. 브랜드가 추구하는 미래와 비전(Vision)을 작성하세요.
4. 세 내용을 합쳐 약 300자 분량의 자연스러운 브랜드 스토리가 되도록 작성하세요.
5. 브랜드의 업종, 타겟, 키워드가 자연스럽게 반영되어야 합니다.
6. 홍보 문구처럼 과장하지 말고 실제 브랜드 소개에 사용할 수 있는 문체로 작성하세요.

반드시 지정된 JSON 구조로만 응답하세요.
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=BrandStoryResult
        )
    )

    return json.loads(response.text)

def generate_color_palette(client, brief):
    prompt = f"""
당신은 전문 브랜드 아이덴티티 디자이너입니다.

다음 브랜드 정보를 바탕으로 브랜드 컬러 팔레트를 제안해주세요.

업종: {brief["industry"]}
타겟: {brief["target"]}
키워드: {", ".join(brief["keywords"])}
톤앤매너: {brief.get("tone", "자유롭게 제안")}
추가 요청사항: {brief.get("notes", "없음")}

다음 조건을 반드시 지켜주세요.

1. 브랜드를 대표하는 메인 컬러를 1개 선정하세요.
2. 메인 컬러와 조화를 이루는 서브 컬러를 2~3개 선정하세요.
3. 모든 색상은 정확한 HEX 코드로 작성하세요.
4. 브랜드의 업종, 타겟, 키워드, 톤앤매너를 고려하세요.
5. 실제 웹 서비스나 브랜드 아이덴티티에 사용할 수 있는 조화로운 색상 조합을 제안하세요.

반드시 지정된 JSON 구조로만 응답하세요.
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ColorPaletteResult
        )
    )

    return json.loads(response.text)

def palette_to_image(color_palette, output_dir):
    colors = [
        color_palette["main_color"],
        *color_palette["sub_colors"]
    ]

    fig, ax = plt.subplots()

    for i, color in enumerate(colors):
        ax.add_patch(
            Rectangle((i, 0), 1, 1, color=color)
        )
    ax.set_xlim(0, len(colors))
    ax.set_ylim(0, 1)
    ax.axis("off")    

    output_path = os.path.join(output_dir, "color_palette.png")
    fig.savefig(output_path, bbox_inches="tight", pad_inches=0)
    plt.close(fig)

    return output_path

def generate_logos(client, brief, output_dir):
    prompt = f"""
AI 업무 생산성 서비스의 브랜드 로고 컨셉을 디자인해주세요.

업종: {brief["industry"]}
타겟: {brief["target"]}
키워드: {", ".join(brief["keywords"])}
톤앤매너: {brief.get("tone", "자유롭게 제안")}
추가 요청사항: {brief.get("notes", "없음")}

깔끔하고 현대적이며 전문적인 브랜드 로고를 만들어주세요.
AI, 자동화, 효율성, 집중과 성장의 이미지를 시각적으로 표현하세요.
심플하고 기억하기 쉬운 형태로 디자인하세요.
실제 웹 서비스의 브랜드 로고로 사용할 수 있는 수준으로 제작하세요.
텍스트나 글자는 포함하지 마세요.
흰색 또는 투명한 배경을 사용하세요.
"""

    logo_paths = []

    for i in range(1, 4):
        interaction = client.interactions.create(
            model="gemini-3.1-flash-image",
            input=prompt
        )

        image_data = interaction.output_image.data

        output_path = os.path.join(
            output_dir,
            f"logo_{i}.png"
        )

        with open(output_path, "wb") as f:
            f.write(base64.b64decode(image_data))

        logo_paths.append(output_path)

    return logo_paths

def save_result(result, output_dir):
    output_path = os.path.join(output_dir, "brand_result.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    return output_path

if __name__ == "__main__":
    client = load_env()

    brief_path, output_dir = get_user_input()
    brief = load_brief(brief_path)

    naming = safe_generate(
        "브랜드 네이밍",
        generate_naming,
        client,
        brief
    )

    slogans = safe_generate(
        "슬로건",
        generate_slogans,
        client,
        brief
    )

    brand_story = safe_generate(
        "브랜드 스토리",
        generate_brand_story,
        client,
        brief
    )

    competitor_analysis = safe_generate(
    "경쟁사 분석",
    generate_competitor_analysis,
    client,
    brief
    )

    color_palette = safe_generate(
        "컬러 팔레트",
        generate_color_palette,
        client,
        brief
    )

    if color_palette:
        palette_path = palette_to_image(color_palette, output_dir)
    else:
        palette_path = None

    logo_paths = safe_generate(
        "로고",
        generate_logos,
        client,
        brief,
        output_dir
    )

    if logo_paths is None:
        logo_paths = []

    result = {
        "naming": naming,
        "slogans": slogans,
        "brand_story": brand_story,
        "competitor_analysis": competitor_analysis,
        "color_palette": color_palette,
        "logos": logo_paths
    }

    result_path = save_result(result, output_dir)
       

    if naming:
        print()
        print("✅ 브랜드 네이밍 생성 완료")
        print()
        print("🇰🇷 한글 네이밍")

        for item in naming["korean"]:
            print(f"- {item['name']}: {item['meaning']}")

        print()
        print("🌍 영문 네이밍")

        for item in naming["english"]:
            print(f"- {item['name']}: {item['meaning']}")
    else:
        print()
        print("⚠️ 브랜드 네이밍 결과가 없습니다.")

    if slogans:
        print()
        print("💬 슬로건")

        for slogan in slogans["slogans"]:
            print(f"- {slogan}")
    else:
        print()
        print("⚠️ 슬로건 결과가 없습니다.")

    if brand_story:
        print()
        print("📖 브랜드 스토리")
        print(f"- 탄생 배경: {brand_story['origin']}")
        print(f"- 브랜드 철학: {brand_story['philosophy']}")
        print(f"- 브랜드 비전: {brand_story['vision']}")
    else:
        print()
        print("⚠️ 브랜드 스토리 결과가 없습니다.")

    if competitor_analysis:
        print()
        print("🔎 경쟁사 분석")

        for competitor in competitor_analysis["competitors"]:
            print(f"- 경쟁사: {competitor['competitor']}")
            print(f"  특징: {competitor['characteristics']}")
            print(f"  강점: {competitor['strengths']}")

        print()
        print(f"- 차별화 방향: {competitor_analysis['differentiation']}")
    else:
        print()
        print("⚠️ 경쟁사 분석 결과가 없습니다.")

    if color_palette:
        print()
        print("🎨 컬러 팔레트")
        print(f"- 메인 컬러: {color_palette['main_color']}")

        print("- 서브 컬러:")
        for color in color_palette["sub_colors"]:
            print(f"  - {color}")
    else:
        print()
        print("⚠️ 컬러 팔레트 결과가 없습니다.")

    print()
    print("📦 최종 결과 저장 완료")
    print(f"- {result_path}")