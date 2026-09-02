import json
import random
import re
import time
import urllib.parse
import urllib.request
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
    "플랫아이콘", "라인아트", "지오메트릭", "아이소메트릭", "코퍼레이트", "수채화",
    "색연필", "판화", "페이퍼 컷아웃", "빈티지", "레트로",
    "보태니컬", "플로럴", "픽셀아트",
]
STYLE_EN = {
    "플랫아이콘": "flat vector icon, solid colors, simple shapes, few details",
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
KEYWORD_EN = {
    "개나리": "forsythia flower branch",
    "진달래": "azalea flower branch",
    "벚꽃": "cherry blossom branch",
    "나비": "butterfly",
    "새싹": "green sprout",
    "화분": "potted plant",
    "물뿌리개": "watering can",
    "봄꽃 리스": "spring flower wreath",
    "선글라스": "sunglasses",
    "밀짚모자": "straw hat",
    "튜브": "colorful inflatable pool swim ring toy",
    "수영튜브": "colorful inflatable pool swim ring toy",
    "물놀이튜브": "colorful inflatable pool swim ring toy",
    "비치백": "beach bag",
    "파도": "simple ocean wave",
    "야자수": "palm tree",
    "아이스크림": "ice cream cone",
    "수박": "watermelon slice",
    "레몬": "lemon fruit",
    "할로윈": "jack-o-lantern pumpkin",
    "유령": "cute ghost",
    "단풍": "maple leaf",
    "낙엽": "fallen autumn leaf",
    "토끼": "rabbit",
    "고양이": "cat",
    "레트로라디오": "vintage radio",
    "빈티지카메라": "vintage camera",
    "스케치북": "sketchbook",
    "핫초코": "hot chocolate mug",
    "도토리": "acorn",
}
MOOD_IMAGE_EN = {
    "몽환적인": "soft gentle colors",
    "아늑한": "warm cozy colors",
    "동화 같은": "cute simple",
    "판타지": "clean simple",
    "감성적인": "soft colors",
    "미니멀": "minimal clean",
    "사이버펑크": "simple graphic",
    "초현실적인": "clean simple",
    "평화로운": "calm simple",
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
    ss.setdefault("preview_bytes", b"")
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

    extra = ""
    if st.session_state.combine:
        extra = (
            f" {main}과 잘 어울리는 소품을 두세 개만 옆에 두되, "
            "서로 겹치지 않게 떨어뜨려 그리고, 나중에 하나씩 따로 써도 될 정도로 단순하게 구성해 주세요."
        )

    ratio_ko = {
        "1:1": "정사각형",
        "16:9": "가로로 긴 화면",
        "9:16": "세로로 긴 화면",
        "4:3": "조금 가로로 넓은 화면",
        "3:2": "사진처럼 가로로 넓은 화면",
    }.get(ratio, ratio)

    prompt = (
        f"{main}만 중심이 되게 {details_str}로 그려 주세요. "
        f"미리캔버스 같은 곳에서 쓸 스톡 요소 시안이라 배경은 그리지 말고, "
        f"너무 복잡하게 만들지 마세요. "
        f"실사 사진이 아니라 손그림, 일러스트, 카툰, 라인드로잉처럼 보이게 하고, "
        f"글자나 워터마크는 넣지 마세요. "
        f"요소끼리 겹치지 않게 {ratio_ko} 비율로 잡아 주세요."
        f"{extra}"
    )
    return prompt, ""


def keyword_en():
    raw = st.session_state.keyword.strip()
    if not raw:
        return "object"
    return KEYWORD_EN.get(raw, raw)


def build_image_prompt():
    subject = keyword_en()
    styles, moods, colors = sync_choices()
    styles = styles[:1]
    moods = moods[:1]
    colors = colors[:1]
    style_en = STYLE_EN.get(styles[0], STYLE_EN["플랫아이콘"]) if styles else STYLE_EN["플랫아이콘"]
    mood_en = MOOD_IMAGE_EN.get(moods[0], "simple") if moods else "simple"
    color_en = COLOR_EN.get(colors[0], "2 or 3 solid colors") if colors else "2 or 3 solid colors"
    return (
        f"simple flat vector icon of one {subject}, "
        f"recognizable {subject}, "
        f"{style_en}, {mood_en}, {color_en}, "
        "bold simple silhouette, smooth edges, no texture, no shading, "
        "white background, easy to trace, "
        f"only one {subject}"
    )


def copy_button(label, text, key):
    if not text:
        st.button(label, disabled=True, use_container_width=True, key=f"{key}_off")
        return
    payload = json.dumps(text)
    label_js = json.dumps(label)
    components.html(
        f"""
<div style="font-family:sans-serif;">
  <button id="btn_{key}" style="width:100%;height:42px;border:0;border-radius:6px;
    background:#c45c26;color:#fff;font-weight:700;cursor:pointer;">{label}</button>
  <div id="msg_{key}" style="margin-top:6px;font-size:13px;color:#1f2a24;"></div>
</div>
<script>
const text = {payload};
const btn = document.getElementById("btn_{key}");
const msg = document.getElementById("msg_{key}");
btn.addEventListener("click", async () => {{
  try {{
    await navigator.clipboard.writeText(text);
    msg.innerText = "복사됨. 붙여넣기 하세요.";
  }} catch (e) {{
    const el = document.createElement("textarea");
    el.value = text;
    el.style.position = "fixed";
    el.style.left = "-9999px";
    document.body.appendChild(el);
    el.focus();
    el.select();
    const ok = document.execCommand("copy");
    el.remove();
    msg.innerText = ok ? "복사됨. 붙여넣기 하세요." : "아래 글상자를 길게 눌러 복사하세요.";
  }}
}});
</script>
        """,
        height=72,
    )


NEGATIVE_FRAME = (
    "picture frame, square frame, ornate border, vignette, badge emblem, "
    "text, letters, watermark, person, girl, fairy"
)
NEGATIVE_CIRCLE = (
    "circular frame, round badge, button badge, plate, medallion, "
    "enamel pin, sticker border"
)
ROUND_SUBJECTS = (
    "swim ring", "watermelon", "lemon", "donut", "tube", "ring",
    "pumpkin", "ball",
)


def pollinations_url(img_prompt, ratio, seed):
    w, h = RATIO_SIZE.get(ratio, (768, 768))
    q = urllib.parse.quote(img_prompt)
    subj = keyword_en().lower()
    neg = NEGATIVE_FRAME
    if not any(word in subj for word in ROUND_SUBJECTS):
        neg = NEGATIVE_FRAME + ", " + NEGATIVE_CIRCLE
    neg_q = urllib.parse.quote(neg)
    return (
        f"https://image.pollinations.ai/prompt/{q}"
        f"?width={w}&height={h}&nologo=true&model=gptimage"
        f"&seed={seed}&enhance=false&safe=true"
        f"&negativePrompt={neg_q}"
    )


def fetch_image(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=90) as resp:
        return resp.read()


def generate_preview(img_prompt):
    seed = random.randint(1, 999999)
    url = pollinations_url(img_prompt, st.session_state.ratio, seed)
    with st.spinner("시안을 가져오는 중..."):
        data = fetch_image(url)
    st.session_state.preview_url = url
    st.session_state.preview_bytes = data
    st.session_state.preview_prompt = img_prompt
    st.session_state.last_gen = time.time()


def preview_filename():
    raw = st.session_state.keyword.strip() or "sian"
    safe = re.sub(r"[^\w가-힣]+", "_", raw).strip("_") or "sian"
    return f"{safe}_sian.jpg"


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
            st.session_state.preview_bytes = b""
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
                try:
                    generate_preview(img_prompt)
                except Exception as e:
                    st.error(f"시안을 받지 못했습니다. 잠시 후 다시 시도하세요. ({e})")

        if st.session_state.preview_bytes:
            st.image(st.session_state.preview_bytes, caption="무료 시안 (스톡 원본으로 올리지 마세요)", use_container_width=True)
            st.download_button(
                "시안 이미지 저장",
                data=st.session_state.preview_bytes,
                file_name=preview_filename(),
                mime="image/jpeg",
                use_container_width=True,
            )
            if st.session_state.preview_url:
                st.link_button("시안 원본 열기", st.session_state.preview_url, use_container_width=True)
            if st.button("다른 구도로 다시 생성", use_container_width=True):
                if time.time() - st.session_state.last_gen < 15:
                    st.warning("15초 뒤에 다시 시도하세요.")
                else:
                    try:
                        generate_preview(img_prompt)
                        st.rerun()
                    except Exception as e:
                        st.error(f"시안을 받지 못했습니다. ({e})")
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
