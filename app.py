import os
import pandas as pd
import streamlit as st

# 웹앱 레이아웃 설정
st.set_page_config(page_title="화학x약학 시뮬레이터", layout="wide")

st.title("🧪 pH에 따른 약물 이온화도 및 체내 흡수율 시뮬레이터")
st.markdown(
    "실험 데이터(pH)에 따른 **약물의 체내 흡수율(비이온화 비율)**을 실시간으로 시뮬레이션합니다."
)

file_name = "CSV.csv"

if not os.path.exists(file_name):
    st.error(
        f"❌ 폴더 안에 '{file_name}' 파일이 없습니다! 파일 위치를 확인해 주세요."
    )
else:
    # 데이터 읽기
    df = pd.read_csv(file_name, encoding="utf-8-sig")

    # 💡 왼쪽 사이드바에 약물 선택 기능
    st.sidebar.header("💊 시뮬레이션 약물 설정")
    drug_option = st.sidebar.selectbox(
        "약물을 선택하세요:",
        [
            "아스피린 (약산성, pKa 3.5)",
            "아세트아미노펜 (약산성, pKa 9.5)",
            "디아제팜 (약염기성, pKa 3.3)",
            "암페타민 (약염기성, pKa 9.9)",
            "직접 pKa 입력하기",
        ],
    )

    # 약물 유형별 설정
    if "아스피린" in drug_option:
        pKa, is_acid, drug_name = 3.5, True, "Aspirin (아스피린)"
    elif "아세트아미노펜" in drug_option:
        pKa, is_acid, drug_name = 9.5, True, "Acetaminophen (타이레놀 성분)"
    elif "디아제팜" in drug_option:
        pKa, is_acid, drug_name = 3.3, False, "Diazepam (신경안정제)"
    elif "암페타민" in drug_option:
        pKa, is_acid, drug_name = 9.9, False, "Amphetamine (각성제 성분)"
    else:
        pKa = st.sidebar.slider("고유 산해리상수(pKa) 선택", 0.0, 14.0, 7.0, 0.1)
        drug_type = st.sidebar.radio("약물 성격", ["약산성", "약염기성"])
        is_acid = drug_type == "약산성"
        drug_name = "커스텀 약물"

    # 헨더슨-하셀바흐 계산 함수
    def calculate_absorption(ph, pka, is_acid):
        if is_acid:
            return 1 / (1 + 10 ** (ph - pka)) * 100
        else:
            return 1 / (1 + 10 ** (pka - ph)) * 100

# 데이터 2 가공
    has_df2 = df.shape[1] >= 4
    if has_df2:
        df2 = pd.DataFrame()
        df2["시간(초)"] = df.iloc[:, 2].dropna().values
        # 💡 에러 방지를 위해 컬럼 이름의 콜론(:)을 대시(-)로 안전하게 변경합니다.
        df2["데이터2 - pH"] = df.iloc[:, 3].dropna().values
        df2["데이터2 - 약물 흡수율(%)"] = calculate_absorption(
            df2["데이터2 - pH"], pKa, is_acid
        )

    # 차트용 데이터 구성 (데이터 2 단독 플롯팅)
    ph_chart = pd.DataFrame()
    if has_df2:
        ph_chart["데이터2 - pH"] = df2["데이터2 - pH"]

    abs_chart = pd.DataFrame()
    if has_df2:
        abs_chart["데이터2 - 약물 흡수율(%)"] = df2["데이터2 - 약물 흡수율(%)"]
    # 🖥️ 화면 레이아웃 분할 배치
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 실험 데이터 (시간에 따른 pH 변화)")
        st.line_chart(ph_chart)

   # 💡 [교정 포인트] 그래프를 그리기 직전에, 사이드바에서 선택한 약물 이름으로 drug_name을 다시 확실하게 동기화합니다.
    with col2:
        # 💡 st.subheader 대신 st.write와 마크다운(###)을 쓰면 레이아웃에 갇히지 않고 실시간으로 바뀝니다!
        st.write(f"### 💊 약물 시뮬레이션 ({drug_name} 흡수율)")
        st.line_chart(abs_chart)

    # 하단 상태 요약 창 (기존 들여쓰기 공백 4칸 유지)
    st.subheader("📝 실시간 분석 요약")
    type_str = "약산성" if is_acid else "약염기성"
    info_msg = f"현재 선택된 약물: {drug_name} | 성격: {type_str} | 고유 pKa: {pKa}"
    st.info(info_msg)
