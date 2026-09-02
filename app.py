import json
import random
import time
import urllib.parse
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="벡터 작업대",
    page_icon="🎨",
    layout="wide",
)


def apply_theme():
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@400;600;700&display=swap');
html, body, [class*="css"] { font-family: "IBM Plex Sans KR", sans-serif; }
.stApp { background: #f4efe6; }
section[data-testid="stSidebar"] { background: #1f2a24; }
section[data-testid="stSidebar"] * { color: #f4efe6 !important; }
.hero {
  background: #1f2a24;
  color: #f4efe6;
  border-radius: 8px;
  padding: 20px 22px;
  margin-bottom: 16px;
}
.hero h1 { margin: 0; font-size: 1.45rem; letter-spacing: -.02em; color: #f4efe6; }
.hero p { margin: 6px 0 0; color: #c9d4cc; font-size: .92rem; }
div.stButton > button {
  border-radius: 4px;
  font-weight: 600;
  border: 1px solid #1f2a24;
}
div.stButton > button[kind="primary"] {
  background: #c45c26;
  color: #fff;
  border: 0;
}
</style>
        """,
        unsafe_allow_html=True,
    )

MANDATORY_GUIDE = (
    "미리캔버스 외 스톡요소로 사용될 이미지 스케치 참고용 이미지야, "
    "배경은 그리지 말아줘, 너무 복잡하게는 그리지 말아줘, "
    "키워드를 중심요소로 그려줘, 실사 이미지는 제외하고 "
    "손그림, 일러스트, 카툰, 라인드로잉 등 으로 그려줘, "
    "텍스트는 넣지 말아줘, 요소들끼리 서로 겹치지 않게 그려줘"
)

STYLES = [
    "라인아트", "지오메트릭", "아이소메트릭", "코퍼레이트", "수채화",
    "색연필", "판화", "페이퍼 컷아웃", "빈티지", "레트로",
    "보태니컬", "플로럴", "픽셀아트",
]
STYLE_EN = {
    "라인아트": "clean line art vector outline",
    "지오메트릭": "geometric flat shapes",
    "아이소메트릭": "isometric cute 3d illustration",
    "코퍼레이트": "corporate memphis flat vector",
    "수채화": "soft watercolor illustration",
    "색연필": "colored pencil sketch",
    "판화": "woodcut linocut print",
    "페이퍼 컷아웃": "layered paper cutout craft",
    "빈티지": "vintage nostalgic illustration",
    "레트로": "80s retro illustration",
    "보태니컬": "botanical illustration",
    "플로럴": "floral elegant illustration",
    "픽셀아트": "cute 16-bit pixel art",
}
MOODS = [
    "몽환적인", "아늑한", "동화 같은", "판타지", "감성적인",
    "미니멀", "사이버펑크", "초현실적인", "평화로운",
]
MOOD_EN = {
    "몽환적인": "dreamy ethereal",
    "아늑한": "cozy warm",
    "동화 같은": "whimsical fairy tale",
    "판타지": "magical fantasy",
    "감성적인": "emotional poetic",
    "미니멀": "clean minimal",
    "사이버펑크": "cyberpunk neon",
    "초현실적인": "surreal",
    "평화로운": "peaceful serene",
}
COLORS = ["파스텔", "뮤트", "레트로", "비비드", "네온", "모노톤"]
COLOR_EN = {
    "파스텔": "soft pastel colors",
    "뮤트": "muted low saturation colors",
    "레트로": "retro vintage colors",
    "비비드": "vivid bright colors",
    "네온": "neon colors",
    "모노톤": "monochrome",
}
SUGGEST_POOL = [
    "개나리", "진달래", "벚꽃", "나비", "새싹", "화분", "물뿌리개",
    "봄꽃 리스", "선글라스", "밀짚모자", "튜브", "비치백", "파도",
    "야자수", "아이스크림", "수박", "레몬", "할로윈", "유령",
    "단풍", "낙엽", "토끼", "고양이", "레트로라디오", "빈티지카메라",
    "스케치북", "핫초코", "도토리",
]
DAYS = {
    1: "개나리 가지 단품 / 흰 배경 누끼 / 노랑+초록",
    2: "진달래 가지 단품 / 분홍 꽃송이 단순화",
    3: "벚꽃 가지 단품 / 꽃+봉오리 혼합",
    4: "봄 나비 아이콘 2~4종",
    5: "작은 새 아이콘 앉은형+나는형",
    11: "봄꽃 리스 / 중앙 여백 확보",
    15: "봄 작은꽃 심리스 패턴",
    21: "선글라스 아이콘 3형태",
    25: "파도 아이콘 3단계",
    28: "아이스크림 콘+바 3종",
}
RATIO_SIZE = {
    "1:1": (768, 768),
    "16:9": (1024, 576),
    "9:16": (576, 1024),
    "4:3": (896, 672),
    "3:2": (960, 640),
}


def init_state():
    ss = st.session_state
    ss.setdefault("keyword", "")
    ss.setdefault("styles", [])
    ss.setdefault("moods", [])
    ss.setdefault("colors", [])
    ss.setdefault("combine", False)
    ss.setdefault("quality", True)
    ss.setdefault("model", "chatgpt")
    ss.setdefault("ratio", "1:1")
    ss.setdefault("chips", random.sample(SUGGEST_POOL, 5))
    ss.setdefault("preview_url", "")
    ss.setdefault("preview_prompt", "")
    ss.setdefault("last_gen", 0.0)


def sync_choices():
    styles = st.session_state.get("style_ms", st.session_state.styles)
    moods = st.session_state.get("mood_ms", st.session_state.moods)
    colors = st.session_state.get("color_ms", st.session_state.colors)
    st.session_state.styles = styles
    st.session_state.moods = moods
    st.session_state.colors = colors
    return styles, moods, colors


def build_prompt():
    keyword = st.session_state.keyword.strip()
    styles, moods, colors = sync_choices()
    if not keyword and not styles and not moods and not colors:
        return "", "키워드를 입력하거나 옵션을 선택해 주세요."

    main = keyword or "중심 포커스 요소"
    details = []
    if styles:
        details.append(", ".join(styles) + " 스타일")
    if moods:
        details.append(", ".join(moods) + " 분위기")
    if colors:
        details.append(", ".join(colors) + " 색감 팔레트")
    if st.session_state.quality:
        details.append("고화질 디테일, 완성도 높은 연출")
    details_str = ", ".join(details) if details else "손그림 및 일러스트 표현"
    ratio = st.session_state.ratio

    if st.session_state.combine:
        sub_chat = (
            f"\n- 이미지 기획: 내가 제시하는 [{main}]에 맞춰, "
            "스톡 플랫폼에서 활용도가 높은 일러스트 시안과 조합 요소들을 기획해줘, "
            "메인 오브젝트와 함께 배치하거나, 각각 개별 스톡 소스로 등록하기 좋은 서브 아이템들로 기획해줘."
        )
        sub_gem = (
            f"\n참고사항: 내가 제시하는 [{main}]에 맞춰, "
            "스톡 플랫폼에서 활용도가 높은 일러스트 시안과 조합 요소들을 기획해줘, "
            "메인 오브젝트와 함께 배치하거나, 각각 개별 스톡 소스로 등록하기 좋은 서브 아이템들로 기획해줘."
        )
    else:
        sub_chat = ""
        sub_gem = ""

    if st.session_state.model == "chatgpt":
        prompt = (
            "[스톡 요소 이미지 생성 요청]\n"
            f'"{main}" 중심의 이미지를 생성해줘.{sub_chat}\n'
            f"- 표현 스타일: {details_str}\n"
            f"- 종횡비: {ratio}\n\n"
            f"[필수 지침 사항]:\n{MANDATORY_GUIDE}"
        )
    else:
        prompt = (
            f'다음 지시사항에 따라 고품질 이미지 스톡 요소를 그려줘: "{main}".{sub_gem}\n'
            f"스타일: {details_str}, 비율: {ratio}.\n\n"
            f"[필수 지침 사항]: {MANDATORY_GUIDE}"
        )
    return prompt, ""


def build_image_prompt():
    keyword = st.session_state.keyword.strip() or "spring flower"
    styles, moods, colors = sync_choices()
    styles = styles[:1]
    moods = moods[:1]
    colors = colors[:1]
    style_en = STYLE_EN.get(styles[0], "simple stock illustration") if styles else "simple stock clipart icon"
    mood_en = MOOD_EN.get(moods[0], "") if moods else ""
    color_en = COLOR_EN.get(colors[0], "") if colors else ""
    return (
        f"stock vector clipart of a single {keyword}, "
        f"{style_en}, {mood_en}, {color_en}, "
        "only the object, centered, isolated on pure white background, "
        "no person, no girl, no character, no face, no glass box, no room, "
        "no scenery, no story scene, no text, no letters, no watermark, "
        "flat design, clean edges, product icon, not photorealistic"
    )


def copy_button(label, text, key):
    if st.button(label, key=key, use_container_width=True, disabled=not bool(text)):
        payload = json.dumps(text)
        components.html(
            f"""
<script>
const t = {payload};
navigator.clipboard.writeText(t).then(() => {{}}).catch(() => {{
  const el = document.createElement('textarea');
  el.value = t;
  document.body.appendChild(el);
  el.select();
  document.execCommand('copy');
  el.remove();
}});
</script>
            """,
            height=0,
        )
        st.success("클립보드에 복사했습니다. ChatGPT/Gemini에 붙여 넣으세요.")


def pollinations_url(img_prompt, ratio, seed):
    w, h = RATIO_SIZE.get(ratio, (768, 768))
    q = urllib.parse.quote(img_prompt)
    return (
        f"https://image.pollinations.ai/prompt/{q}"
        f"?width={w}&height={h}&nologo=true&model=flux&seed={seed}&enhance=true"
    )


def render_prompt_builder():
    st.markdown(
        """
<div class="hero">
  <h1>🎨 스톡 이미지 시안 프롬프트 생성기</h1>
  <p>키워드와 스타일을 고르면 참고용 시안과 복사용 프롬프트가 만들어집니다.</p>
</div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.15, 1], gap="large")

    with left:
        st.subheader("1. 중심 키워드 입력")
        st.session_state.keyword = st.text_input(
            "키워드",
            value=st.session_state.keyword,
            placeholder="예: 개나리 / 단일 키워드로만",
            label_visibility="collapsed",
        )
        c1, c2 = st.columns([6, 1])
        with c1:
            st.caption("추천 요소")
        with c2:
            if st.button("새로고침"):
                st.session_state.chips = random.sample(SUGGEST_POOL, 5)
                st.rerun()
        chip_cols = st.columns(len(st.session_state.chips))
        for i, chip in enumerate(st.session_state.chips):
            if chip_cols[i].button(chip, key=f"chip_{chip}_{i}"):
                st.session_state.keyword = chip
                st.rerun()

        st.session_state.combine = st.toggle(
            "연관 조합요소 추천 (3~4개 소품 함께 그리기)",
            value=st.session_state.combine,
        )

        st.subheader("2. 그림 스타일 (1개만 고르세요)")
        st.multiselect("스타일", STYLES, default=st.session_state.styles, max_selections=1, label_visibility="collapsed", key="style_ms")
        st.subheader("3. 컨셉 & 분위기 (1개만)")
        st.multiselect("분위기", MOODS, default=st.session_state.moods, max_selections=1, label_visibility="collapsed", key="mood_ms")
        st.subheader("4. 색감 (1개만)")
        st.multiselect("색감", COLORS, default=st.session_state.colors, max_selections=1, label_visibility="collapsed", key="color_ms")

        st.subheader("5. AI 모델 & 비율")
        m1, m2, m3 = st.columns(3)
        with m1:
            st.session_state.model = st.selectbox(
                "복사용 타겟",
                ["chatgpt", "gemini"],
                format_func=lambda x: "ChatGPT" if x == "chatgpt" else "Gemini",
                index=0 if st.session_state.model == "chatgpt" else 1,
            )
        with m2:
            ratios = ["1:1", "16:9", "9:16", "4:3", "3:2"]
            labels = {"1:1": "1:1", "16:9": "16:9", "9:16": "9:16", "4:3": "4:3", "3:2": "3:2"}
            st.session_state.ratio = st.selectbox(
                "종횡비",
                ratios,
                format_func=lambda x: labels[x],
                index=ratios.index(st.session_state.ratio) if st.session_state.ratio in ratios else 0,
            )
        with m3:
            st.session_state.quality = st.toggle("고품질 태그", value=st.session_state.quality)

        b1, b2 = st.columns(2)
        if b1.button("랜덤 조합", use_container_width=True):
            st.session_state.styles = [random.choice(STYLES)]
            st.session_state.moods = [random.choice(MOODS)]
            st.session_state.colors = [random.choice(COLORS)]
            st.rerun()
        if b2.button("전체 삭제", use_container_width=True):
            st.session_state.keyword = ""
            st.session_state.styles = []
            st.session_state.moods = []
            st.session_state.colors = []
            st.session_state.preview_url = ""
            st.rerun()

    prompt, empty_msg = build_prompt()
    img_prompt = build_image_prompt()

    with right:
        st.subheader("무료 시안 생성")
        st.caption("Pollinations 무료 API · 키 없음 · 15초 간격 권장 · 참고용 시안")

        wait_left = 15 - (time.time() - st.session_state.last_gen)
        if st.button("시안 생성하기", type="primary", use_container_width=True):
            if not st.session_state.keyword.strip():
                st.warning("키워드를 먼저 입력하세요.")
            elif wait_left > 0:
                st.warning(f"무료 API 제한입니다. {int(wait_left)+1}초 후 다시 눌러 주세요.")
            else:
                seed = random.randint(1, 999999)
                st.session_state.preview_url = pollinations_url(img_prompt, st.session_state.ratio, seed)
                st.session_state.preview_prompt = img_prompt
                st.session_state.last_gen = time.time()

        if st.session_state.preview_url:
            st.image(st.session_state.preview_url, caption="무료 시안 (스톡 원본으로 올리지 마세요)", use_container_width=True)
            st.link_button("시안 원본 열기", st.session_state.preview_url, use_container_width=True)
            if st.button("다른 구도로 다시 생성", use_container_width=True):
                if time.time() - st.session_state.last_gen < 15:
                    st.warning("15초 뒤에 다시 시도하세요.")
                else:
                    seed = random.randint(1, 999999)
                    st.session_state.preview_url = pollinations_url(img_prompt, st.session_state.ratio, seed)
                    st.session_state.last_gen = time.time()
                    st.rerun()
        else:
            st.info("키워드를 넣고 [시안 생성하기]를 누르면 그림이 나옵니다.")

        st.markdown("---")
        st.subheader("복사용 프롬프트")
        shown = empty_msg or prompt
        st.text_area("ChatGPT / Gemini용", shown, height=180)
        if prompt:
            copy_button("프롬프트 복사", prompt, "copy_prompt")
            st.code(prompt, language=None)
            c1, c2 = st.columns(2)
            with c1:
                st.link_button("ChatGPT 열기", "https://chatgpt.com/", use_container_width=True)
            with c2:
                st.link_button("Gemini 열기", "https://gemini.google.com/app", use_container_width=True)
        st.caption("복사한 뒤 ChatGPT/Gemini에 붙여 넣으세요. 텍스트 파일로 저장하지 않아도 됩니다.")


def render_calendar():
    st.header("100일 도안 캘린더")
    day = st.slider("Day", 1, 30, 1)
    st.success(DAYS.get(day, "같은 시즌 소품을 단품 → 세트 → 패턴 순으로 그리세요."))


def render_tags():
    st.header("메타데이터 생성기")
    desc = st.text_input("그린 요소", "봄 개나리 꽃가지 단품 벡터")
    extra = st.text_input("추가 키워드", "노랑, 가지, 누끼")
    if st.button("생성"):
        extras = [t.strip() for t in extra.split(",") if t.strip()]
        st.text_area("국내 제목", f"{desc} 디자인 소스 벡터")
        st.text_area("국내 태그", ", ".join([desc, "벡터", "일러스트", "디자인소스"] + extras))
        st.text_area("English Title", f"{desc} isolated vector illustration")
        st.text_area("English Keywords", ", ".join([desc, "vector", "illustration", "isolated"] + extras))


def render_strategy():
    st.header("업로드 전략")
    st.markdown(
        """
1. AI 시안은 참고만 하고, 스톡에는 직접 그린 벡터를 올리세요
2. 단품보다 같은 스타일 3~8개 세트
3. 영어 태그 먼저
4. 시즌 상품은 2~3개월 전 업로드
5. 투명 PNG + EPS/SVG
"""
    )


apply_theme()
init_state()
menu = st.sidebar.radio(
    "메뉴",
    ["시안 프롬프트 생성기", "100일 도안 캘린더", "메타데이터 생성기", "업로드 전략"],
)
if menu == "시안 프롬프트 생성기":
    render_prompt_builder()
elif menu == "100일 도안 캘린더":
    render_calendar()
elif menu == "메타데이터 생성기":
    render_tags()
else:
    render_strategy()
