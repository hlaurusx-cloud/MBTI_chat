import streamlit as st
import hashlib
import hmac
import secrets
from datetime import datetime

# ==========================
# 1. 페이지 설정 및 디자인
# ==========================

st.set_page_config(
    page_title="MindType",
    page_icon="🌷",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background-color: #F9F7FC;
}

.block-container {
    max-width: 1300px;
    padding: 3.5rem 3rem 2rem;
}

.logo {
    color: #8268B6;
    font-size: 30px;
    font-weight: bold;
}

.hero {
    text-align: center;
    padding: 35px 20px;
}

.hero h1 {
    color: #55436E;
    font-size: 42px;
}

.hero p {
    color: #81778D;
    font-size: 18px;
    line-height: 1.8;
}

.feature {
    text-align: center;
    padding: 25px;
    background: #EEE8F8;
    border-radius: 20px;
}

.feature h2 {
    color: #7359A4;
}

.feature p {
    color: #81778D;
}

.question-card {
    background-color: white;
    border-radius: 24px;
    padding: 45px 30px;
    text-align: center;
    margin: 20px 0;
    color: #55436E;
}

.question-card h2 {
    font-size: 26px;
    line-height: 1.6;
}

[data-testid="stRadio"] label {
    background: white;
    padding: 18px;
    border-radius: 14px;
    margin-bottom: 8px;
}

button[kind="primary"],
button[kind="primaryFormSubmit"] {
    background-color: #9476C5 !important;
    color: white !important;
    border: none;
    border-radius: 14px;
    min-height: 48px;
}

.result-type {
    text-align: center;
    color: #8268B6;
    font-size: 85px;
    font-weight: bold;
    letter-spacing: 12px;
}

.footer {
    text-align: center;
    color: #9992A3;
    font-size: 13px;
    padding: 20px;
}

@media (max-width: 700px) {
    .block-container {
        padding: 3rem 1rem 1rem;
    }

    .hero h1 {
        font-size: 28px;
    }

    .result-type {
        font-size: 55px;
    }
}
</style>
""", unsafe_allow_html=True)


# ==========================
# 2. 세션 상태 초기화
# ==========================

defaults = {
    "authenticated": False,
    "username": None,
    "users": {},
    "records": {},
    "answers": [None] * 12,
    "question_index": 0,
    "test_id": 0,
    "result": None,
    "result_saved": False,
    "pending_save": False
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# 이전 버전 데이터 초기화
if len(st.session_state.answers) != 12:
    st.session_state.answers = [None] * 12
    st.session_state.question_index = 0


# ==========================
# 3. MBTI 질문
# ==========================

questions = [
    (
        "주말에 자유 시간이 생긴다면 무엇을 하고 싶으신가요?",
        "친구들과 만나 즐거운 시간을 보내요.",
        "혼자만의 시간을 보내며 휴식해요.",
        "E", "I"
    ),
    (
        "새로운 것을 배울 때 어떤 방식이 더 편한가요?",
        "구체적인 사례를 통해 이해해요.",
        "전체적인 개념과 가능성을 생각해요.",
        "S", "N"
    ),
    (
        "친구가 고민을 이야기할 때 어떻게 반응하시나요?",
        "현실적인 해결 방법을 제안해요.",
        "친구의 마음에 공감하고 위로해요.",
        "T", "F"
    ),
    (
        "여행을 준비할 때 어떤 방식이 더 편한가요?",
        "미리 일정을 계획해요.",
        "상황에 따라 자유롭게 결정해요.",
        "J", "P"
    ),
    (
        "처음 만나는 사람들이 많은 자리에서는 어떤 편인가요?",
        "먼저 말을 걸며 대화를 시작해요.",
        "상대방이 말을 걸어주기를 기다려요.",
        "E", "I"
    ),
    (
        "영화를 볼 때 어떤 부분에 더 관심이 가나요?",
        "구체적인 사건과 장면에 관심이 가요.",
        "숨겨진 의미와 상징에 관심이 가요.",
        "S", "N"
    ),
    (
        "중요한 결정을 내릴 때 무엇을 더 중요하게 생각하나요?",
        "논리와 객관적인 근거를 중요하게 생각해요.",
        "사람들의 감정과 가치관을 중요하게 생각해요.",
        "T", "F"
    ),
    (
        "해야 할 일이 많을 때 어떻게 행동하시나요?",
        "할 일 목록을 작성하고 순서대로 처리해요.",
        "상황에 맞게 유연하게 처리해요.",
        "J", "P"
    ),
    (
        "힘든 하루를 보낸 후 어떻게 에너지를 회복하시나요?",
        "다른 사람들과 이야기하며 에너지를 얻어요.",
        "혼자 조용히 쉬면서 에너지를 얻어요.",
        "E", "I"
    ),
    (
        "문제를 해결할 때 어떤 방식에 더 끌리나요?",
        "경험을 바탕으로 현실적인 방법을 찾아요.",
        "새로운 아이디어와 가능성을 생각해요.",
        "S", "N"
    ),
    (
        "의견 충돌이 발생하면 어떻게 해결하고 싶으신가요?",
        "논리적으로 가장 합리적인 결론을 찾아요.",
        "서로의 감정을 이해하고 조화를 이루고 싶어요.",
        "T", "F"
    ),
    (
        "갑자기 약속이 변경되면 어떤 기분이 드나요?",
        "계획이 바뀌어서 불편해요.",
        "새로운 상황도 자연스럽게 받아들여요.",
        "J", "P"
    )
]


# ==========================
# 4. 성격 유형 정보
# ==========================

personalities = {
    "INTJ": ("전략적인 계획가",
             "독립적으로 사고하며 장기적인 목표를 추구합니다."),
    "INTP": ("호기심 많은 탐구자",
             "논리적 사고와 새로운 아이디어를 즐깁니다."),
    "ENTJ": ("결단력 있는 리더",
             "목표를 설정하고 효율적으로 실행합니다."),
    "ENTP": ("창의적인 도전자",
             "새로운 가능성과 다양한 관점을 탐색합니다."),
    "INFJ": ("통찰력 있는 조언자",
             "깊은 통찰력과 공감 능력을 가지고 있습니다."),
    "INFP": ("상상력이 풍부한 이상주의자",
             "자신만의 가치관과 창의성을 소중히 여깁니다."),
    "ENFJ": ("따뜻한 리더",
             "다른 사람의 성장과 행복을 중요하게 생각합니다."),
    "ENFP": ("열정적인 탐험가",
             "새로운 경험과 사람들과의 교류를 즐깁니다."),
    "ISTJ": ("책임감 있는 실천가",
             "규칙과 책임을 중요하게 생각합니다."),
    "ISFJ": ("세심한 조력자",
             "주변 사람들을 따뜻하게 배려합니다."),
    "ESTJ": ("효율적인 관리자",
             "체계적인 계획과 실행을 중요하게 생각합니다."),
    "ESFJ": ("다정한 협력자",
             "사람들과의 조화로운 관계를 소중히 여깁니다."),
    "ISTP": ("실용적인 해결사",
             "현실적인 문제 해결과 독립적인 활동을 즐깁니다."),
    "ISFP": ("감성적인 예술가",
             "자유로운 표현과 개인적인 가치를 소중히 여깁니다."),
    "ESTP": ("활동적인 도전자",
             "새로운 경험과 즉각적인 행동을 즐깁니다."),
    "ESFP": ("즐거운 분위기 메이커",
             "사람들과 즐거운 순간을 공유합니다.")
}


# ==========================
# 5. 주요 함수
# ==========================

def hash_password(password, salt):
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        bytes.fromhex(salt),
        600000
    ).hex()


def start_test():
    st.session_state.answers = [None] * 12
    st.session_state.question_index = 0
    st.session_state.test_id += 1
    st.session_state.result = None
    st.session_state.result_saved = False
    st.session_state.pending_save = False

    st.switch_page(test_page)


def calculate_result():

    scores = {letter: 0 for letter in "EISNTFJP"}

    for answer in st.session_state.answers:
        if answer is not None:
            scores[answer] += 1

    result = ""

    for first, second in [
        ("E", "I"),
        ("S", "N"),
        ("T", "F"),
        ("J", "P")
    ]:
        result += first if scores[first] > scores[second] else second

    return result, scores


def save_result():

    username = st.session_state.username

    if username and not st.session_state.result_saved:

        if username not in st.session_state.records:
            st.session_state.records[username] = []

        st.session_state.records[username].append({
            "검사 날짜": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "MBTI 유형": st.session_state.result
        })

        st.session_state.result_saved = True


# ==========================
# 6. 홈페이지
# ==========================

def home():

    st.markdown("""
    <div class="hero">
        <div style="font-size:75px;">🌷 🧸 🌿</div>
        <h1>나를 알아가는 작은 여행</h1>
        <p>
        나는 어떤 사람일까요?<br>
        간단한 대화형 질문을 통해<br>
        나만의 성격 유형을 발견해 보세요.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    col1.markdown("""
    <div class="feature">
        ⏱️
        <h2>3분</h2>
        <p>소요 시간</p>
    </div>
    """, unsafe_allow_html=True)

    col2.markdown("""
    <div class="feature" style="background:#E5F1E9;">
        💬
        <h2>12문항</h2>
        <p>대화형 질문</p>
    </div>
    """, unsafe_allow_html=True)

    col3.markdown("""
    <div class="feature" style="background:#F8E8EE;">
        ✨
        <h2>16가지</h2>
        <p>성격 유형</p>
    </div>
    """, unsafe_allow_html=True)

    st.write("")

    if st.button(
        "무료 테스트 시작하기 →",
        type="primary",
        use_container_width=True
    ):
        start_test()

    st.markdown("""
    <div class="footer">
        로그인 없이도 테스트를 이용할 수 있습니다.<br>
        본 테스트는 재미와 자기 이해를 위한 간이 검사입니다.
    </div>
    """, unsafe_allow_html=True)


def test():

    index = st.session_state.question_index
    q = questions[index]

    left, center, right = st.columns([1, 4, 1])

    with center:

        st.markdown(
            "<h2 style='text-align:center;color:#55436E;'>"
            "나를 알아가는 시간</h2>",
            unsafe_allow_html=True
        )

        st.write(f"테스트 진행률: {index + 1} / 12")
        st.progress((index + 1) / 12)

        st.markdown(f"""
        <div class="question-card">
            <div style="font-size:45px;">🌷</div>
            <h2>{q[0]}</h2>
        </div>
        """, unsafe_allow_html=True)

        saved_answer = st.session_state.answers[index]

        if saved_answer == q[3]:
            selected_index = 0
        elif saved_answer == q[4]:
            selected_index = 1
        else:
            selected_index = None

        selected = st.radio(
            "답변",
            options=[q[1], q[2]],
            index=selected_index,
            label_visibility="collapsed",
            key=f"question_{st.session_state.test_id}_{index}"
        )

        # 선택한 답변 확인
        new_answer = None

        if selected == q[1]:
            new_answer = q[3]

        elif selected == q[2]:
            new_answer = q[4]

        # 새로운 답변 선택 시 자동 이동
        if new_answer is not None and new_answer != saved_answer:

            st.session_state.answers[index] = new_answer
            st.session_state.result = None
            st.session_state.result_saved = False

            if index < 11:
                st.session_state.question_index += 1
                st.rerun()

            elif all(st.session_state.answers):
                result, scores = calculate_result()
                st.session_state.result = result
                st.switch_page(result_page)

        st.write("")

        # 이전 및 다음 문항 버튼
        prev_col, next_col = st.columns(2)

        with prev_col:

            if st.button(
                "← 이전 문항",
                disabled=(index == 0),
                use_container_width=True
            ):
                st.session_state.question_index -= 1
                st.rerun()

        with next_col:

            button_text = (
                "다음 문항 →"
                if index < 11
                else "결과 확인하기 →"
            )

            if st.button(
                button_text,
                type="primary",
                disabled=(
                    st.session_state.answers[index] is None
                ),
                use_container_width=True
            ):

                if index < 11:
                    st.session_state.question_index += 1
                    st.rerun()

                elif all(st.session_state.answers):
                    result, scores = calculate_result()
                    st.session_state.result = result
                    st.switch_page(result_page)

# ==========================
# 8. 결과 페이지
# ==========================

def result():

    if not all(st.session_state.answers):
        st.info("먼저 테스트를 완료해 주세요.")

        if st.button("테스트 시작하기"):
            st.switch_page(test_page)

        return

    mbti, scores = calculate_result()
    st.session_state.result = mbti

    title, description = personalities[mbti]

    st.markdown("""
    <div class="hero">
        <p>당신의 성격 유형은</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        f'<div class="result-type">{mbti}</div>',
        unsafe_allow_html=True
    )

    st.markdown(f"""
    <div class="hero">
        <div style="font-size:60px;">🌿</div>
        <h1>{title}</h1>
        <p>{description}</p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("나의 성격 유형 분석")

    dimensions = [
        ("외향형 E", "내향형 I", "E", "I"),
        ("감각형 S", "직관형 N", "S", "N"),
        ("사고형 T", "감정형 F", "T", "F"),
        ("판단형 J", "인식형 P", "J", "P")
    ]

    for label1, label2, first, second in dimensions:

        percent1 = round(scores[first] / 3 * 100)
        percent2 = 100 - percent1

        st.write(
            f"{label1} {percent1}%  ｜  {percent2}% {label2}"
        )

        st.progress(scores[first] / 3)

    st.caption("각 영역의 3개 문항에 대한 응답 비율입니다.")

    st.divider()

    if st.session_state.result_saved:
        st.success("테스트 결과가 저장되었습니다.")

    elif st.button(
        "결과 저장하기",
        type="primary",
        use_container_width=True
    ):

        if st.session_state.username:
            save_result()
            st.rerun()

        else:
            st.session_state.pending_save = True
            st.switch_page(login_page)

    col1, col2 = st.columns(2)

    if col1.button(
        "다시 테스트하기",
        use_container_width=True
    ):
        start_test()

    if col2.button(
        "메인 페이지",
        use_container_width=True
    ):
        st.switch_page(home_page)

    st.caption(
        "본 결과는 공식 MBTI 검사가 아닌 간이 테스트 결과입니다."
    )


# ==========================
# 9. 로그인 및 회원가입
# ==========================

def login():

    st.title("🌷 로그인 및 회원가입")

    st.info("회원 정보와 기록은 현재 접속 세션에서만 유지됩니다.")

    login_tab, signup_tab = st.tabs(
        ["로그인", "회원가입"]
    )

    with login_tab:

        with st.form("login_form"):

            username = st.text_input("아이디").strip()

            password = st.text_input(
                "비밀번호",
                type="password"
            )

            submitted = st.form_submit_button(
                "로그인",
                type="primary",
                use_container_width=True
            )

        if submitted:

            user = st.session_state.users.get(username)

            if user and hmac.compare_digest(
                user["password"],
                hash_password(password, user["salt"])
            ):
                st.session_state.username = username

                if st.session_state.pending_save:
                    save_result()
                    st.session_state.pending_save = False
                    st.switch_page(result_page)

                st.switch_page(profile_page)

            else:
                st.error("아이디 또는 비밀번호가 올바르지 않습니다.")

    with signup_tab:

        with st.form("signup_form"):

            username = st.text_input("아이디").strip()

            password = st.text_input(
                "비밀번호",
                type="password"
            )

            confirm = st.text_input(
                "비밀번호 확인",
                type="password"
            )

            registered = st.form_submit_button(
                "회원가입",
                type="primary",
                use_container_width=True
            )

        if registered:

            if not username or not password:
                st.warning("아이디와 비밀번호를 입력해 주세요.")

            elif len(password) < 8:
                st.warning("비밀번호는 8자 이상 입력해 주세요.")

            elif username in st.session_state.users:
                st.error("이미 사용 중인 아이디입니다.")

            elif password != confirm:
                st.error("비밀번호가 일치하지 않습니다.")

            else:
                salt = secrets.token_hex(16)

                st.session_state.users[username] = {
                    "salt": salt,
                    "password": hash_password(password, salt)
                }

                st.success("회원가입이 완료되었습니다. 로그인해 주세요!")


# ==========================
# 10. 마이페이지
# ==========================

def profile():

    if not st.session_state.username:
        st.switch_page(login_page)

    username = st.session_state.username

    st.title("👤 마이페이지")
    st.write(f"{username}님, 환영합니다!")

    st.subheader("나의 테스트 기록")

    records = st.session_state.records.get(username, [])

    if records:

        st.dataframe(
            records,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("아직 저장된 테스트 결과가 없습니다.")

    if st.button("로그아웃"):
        st.session_state.username = None
        st.session_state.answers = [None] * 12
        st.session_state.question_index = 0
        st.session_state.test_id += 1
        st.session_state.result = None
        st.session_state.result_saved = False
        st.session_state.pending_save = False

        st.switch_page(home_page)


# ==========================
# 11. 고객센터
# ==========================

def help_center():

    st.title("💌 고객센터")
    st.subheader("자주 묻는 질문")

    faq = [
        (
            "로그인 없이 테스트할 수 있나요?",
            "네. 회원가입 없이도 테스트에 참여할 수 있습니다."
        ),
        (
            "테스트는 얼마나 걸리나요?",
            "총 12문항으로 약 3분 정도 소요됩니다."
        ),
        (
            "이전 문항으로 돌아갈 수 있나요?",
            "네. 이전 문항 버튼을 이용하여 응답을 수정할 수 있습니다."
        ),
        (
            "공식 MBTI 검사인가요?",
            "아닙니다. 자기 이해와 재미를 위한 간이 검사입니다."
        ),
        (
            "테스트 결과는 어떻게 저장하나요?",
            "로그인 후 결과 페이지에서 결과 저장하기를 선택하면 됩니다."
        )
    ]

    for question, answer in faq:

        with st.expander(question):
            st.write(answer)


# ==========================
# 12. 페이지 등록
# ==========================

home_page = st.Page(
    home,
    title="홈",
    default=True
)

test_page = st.Page(
    test,
    title="성격 유형 테스트",
    url_path="test"
)

result_page = st.Page(
    result,
    title="테스트 결과",
    url_path="result"
)

login_page = st.Page(
    login,
    title="로그인",
    url_path="login"
)

profile_page = st.Page(
    profile,
    title="마이페이지",
    url_path="mypage"
)

help_page = st.Page(
    help_center,
    title="고객센터",
    url_path="help"
)

current_page = st.navigation(
    [
        home_page,
        test_page,
        result_page,
        login_page,
        profile_page,
        help_page
    ],
    position="hidden"
)


# ==========================
# 13. 서비스 접속 인증
# ==========================

if not st.session_state.authenticated:

    st.markdown("""
    <div class="hero">
        <div style="font-size:65px;">🌷</div>
        <h1>Welcome to MindType</h1>
        <p>나를 알아가는 작은 여행</p>
    </div>
    """, unsafe_allow_html=True)

    left, center, right = st.columns([1, 2, 1])

    with center:

        with st.form("access_form"):

            password = st.text_input(
                "서비스 접속 비밀번호",
                type="password"
            )

            submitted = st.form_submit_button(
                "입장하기 →",
                type="primary",
                use_container_width=True
            )

        if submitted:

            if password == "pnumis":
                st.session_state.authenticated = True
                st.rerun()

            else:
                st.error("비밀번호가 올바르지 않습니다.")

    st.stop()


# ==========================
# 14. 공통 상단 메뉴
# ==========================

logo, menu1, menu2, menu3 = st.columns(
    [7, 1, 1.5, 1.5]
)

with logo:

    st.markdown(
        '<div class="logo">✦ MindType</div>',
        unsafe_allow_html=True
    )

with menu1:
    st.page_link(home_page, label="홈")

with menu2:
    st.page_link(help_page, label="고객센터")

with menu3:

    if st.session_state.username:
        st.page_link(profile_page, label="마이페이지")

    else:
        st.page_link(login_page, label="로그인")

st.divider()


# ==========================
# 15. 현재 페이지 실행
# ==========================

current_page.run()


# ==========================
# 16. 하단 정보
# ==========================

st.divider()

st.markdown("""
<div class="footer">
    © 2026 MindType · 나를 알아가는 작은 여행
</div>
""", unsafe_allow_html=True)