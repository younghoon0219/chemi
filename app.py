import os
import pandas as pd
import streamlit as st

# 웹앱 레이아웃 설정
st.set_page_config(page_title="pH에 따른 약물 이온화도 및 체내 흡수율 시뮬레이터", layout="wide")

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

    import numpy as np
    import plotly.graph_objects as go

# 💡 [해결] 커스텀 반감기를 직접 입력받는 슬라이더 변수를 먼저 선언해 줍니다.
    # (최소 1시간 ~ 최대 50시간, 기본값 4.0시간)
    custom_t_half = st.sidebar.slider("⚙️ 커스텀 약물 반감기 설정 (시간)", 1.0, 50.0, 4.0, 0.5)

    # [약물별 실제 반감기 데이터 설정]
    half_life_dict = {
        "Aspirin (아스피린)": 3.0,
        "Acetaminophen (타이레놀 성분)": 2.0,
        "Diazepam (신경안정제)": 40.0,
        "Amphetamine (각성제 성분)": 10.0,
        "커스텀 약물": 4.0,
    }
    
    t_half = half_life_dict.get(drug_name, 4.0)

    # 이제 컴퓨터가 custom_t_half를 알아보고 정상 작동합니다!
    if drug_name == "커스텀 약물":
        t_half = custom_t_half

# 🖥️ 화면 레이아웃 분할 배치
    col1, col2 = st.columns(2)

    with col1:
        st.write("### 📊 시간에 따른 pH 변화 및 소화기관 영역")

        fig_ph = go.Figure()

        # [왼쪽] pH 수치 기준 가로 음영 배치
        fig_ph.add_hrect(
            y0=1.5,
            y1=3.5,
            line_width=0,
            fillcolor="rgba(255, 0, 0, 0.08)",
        )
        fig_ph.add_annotation(
            x=0.05,
            y=2.5,
            xref="paper",
            yref="y",
            text="😋 위 (pH 1.5-3.5)",
            showarrow=False,
            font=dict(
                color="rgba(255, 0, 0, 0.8)", size=12, family="Malgun Gothic"
            ),
            align="left",
        )

        fig_ph.add_hrect(
            y0=6.0,
            y1=7.4,
            line_width=0,
            fillcolor="rgba(0, 255, 0, 0.08)",
        )
        fig_ph.add_annotation(
            x=0.05,
            y=6.7,
            xref="paper",
            yref="y",
            text="🥦 소장 (pH 6.0-7.4)",
            showarrow=False,
            font=dict(
                color="rgba(0, 150, 0, 0.8)", size=12, family="Malgun Gothic"
            ),
            align="left",
        )

        # pH 측정 데이터 선
        fig_ph.add_trace(
            go.Scatter(
                x=df2["시간(초)"],
                y=df2["데이터2 - pH"],
                mode="lines",
                name="측정 pH",
                line=dict(color="#4B0082", width=3),
                hovertemplate="⏱️ <b>시간</b>: %{x}초<br>🧪 <b>수치</b>: pH %{y}<extra></extra>",
            )
        )

        fig_ph.update_layout(
            xaxis_title="시간 (초)",
            yaxis_title="pH 수치",
            yaxis=dict(range=[0, 14]),
            margin=dict(l=20, r=20, t=20, b=20),
            height=380,
            hovermode="x unified",
        )
        st.plotly_chart(fig_ph, use_container_width=True)

    with col2:
        st.write(f"### 💊 약물 시뮬레이션 ({drug_name} 흡수율)")

        fig_abs = go.Figure()

        # 💡 [안전장치 1] 데이터가 비어있지 않은지 먼저 체크
        if len(df2) > 0:
            # 💡 [안전장치 2] 기준점을 3.5로 낮추어 위 영역을 벗어나는 순간을 정확히 잡습니다.
            boundary_condition = df2["데이터2 - pH"] > 3.5

            if boundary_condition.any():
                change_time = df2.loc[boundary_condition, "시간(초)"].iloc[0]
            else:
                change_time = df2["시간(초)"].max() / 2
            max_time = df2["시간(초)"].max()
        else:
            change_time = 180
            max_time = 360

        # 💡 [안전장치 3] 혹시 모를 에러 방지를 위해 값이 유효할 때만 vrect를 그립니다.
        if change_time > 0:
            # 위 영역 흡수 환경 (연한 빨강)
            fig_abs.add_vrect(
                x0=0,
                x1=change_time,
                line_width=0,
                fillcolor="rgba(255, 0, 0, 0.04)",
                annotation_text="위 흡수 환경",
                annotation_position="top left",
            )
        if max_time > change_time:
            # 소장 영역 흡수 환경 (연한 녹색)
            fig_abs.add_vrect(
                x0=change_time,
                x1=max_time,
                line_width=0,
                fillcolor="rgba(0, 255, 0, 0.04)",
                annotation_text="소장 흡수 환경",
                annotation_position="top left",
            )

        # 약물 흡수율 데이터 선
        fig_abs.add_trace(
            go.Scatter(
                x=df2["시간(초)"],
                y=df2["데이터2 - 약물 흡수율(%)"],
                mode="lines",
                name="비이온화 비율(흡수율)",
                line=dict(color="#FF4B4B", width=3),
                hovertemplate="⏱️ <b>시간</b>: %{x}초<br>🩸 <b>흡수율</b>: %{y:.1f}%<extra></extra>",
            )
        )

        fig_abs.update_layout(
            xaxis_title="시간 (초)",
            yaxis_title="흡수율 (%)",
            yaxis=dict(range=[0, 105]),
            margin=dict(l=20, r=20, t=30, b=20),
            height=380,
            hovermode="x unified",
        )
        st.plotly_chart(fig_abs, use_container_width=True)

   # ⏳ [기능 2] 하단 반감기 차트 구역 (공백 4칸으로 시작 라인을 맞췄습니다)
    st.markdown("---")
    st.write(
        f"### ⏳ 의학·수학 융합 시뮬레이션: 시간 경과에 따른 체내 {drug_name} 잔류 농도 추이"
    )
    st.caption(
        f"지수함수 모델 $C(t) = C_0 \\times e^{{-k_e t}}$ 및 반감기($t_{{1/2}}$ = {t_half}시간)를 적용한 약동학적 농도 감소 시뮬레이션입니다."
    )

    max_sec = df2["시간(초)"].max() if len(df2) > 0 else 360
    time_hours = (df2["시간(초)"] / max_sec) * (t_half * 3)

    avg_absorption = (
        df2["데이터2 - 약물 흡수율(%)"].mean() if len(df2) > 0 else 50.0
    )
    c_0 = float(avg_absorption)

    k_elim = np.log(2) / t_half
    remaining_concentration = c_0 * np.exp(-k_elim * time_hours)

    fig_decay = go.Figure()

    # 💡 왼쪽 공백을 8칸에서 8칸 미만인 4칸 정배율로 정렬한 add_trace입니다.
    fig_decay.add_trace(
        go.Scatter(
            x=time_hours,
            y=remaining_concentration,
            mode="lines",
            name="체내 약물 농도",
            line=dict(color="#1f77b4", width=3, dash="dash"),
            hovertemplate="⏳ <b>경과 시간</b>: %{x:.1f}시간<br>📉 <b>잔류 농도</b>: %{y:.1f}%<extra></extra>",
        )
    )
    fig_decay.add_vline(
        x=t_half,
        line_width=1.5,
        line_dash="dot",
        line_color="orange",
        annotation_text="1차 반감기",
    )

    fig_decay.update_layout(
        xaxis_title="시간 (Hours)",
        yaxis_title="체내 약물 농도 (Relative %)",
        yaxis=dict(range=[0, 105]),
        margin=dict(l=20, r=20, t=30, b=20),
        height=300,
        hovermode="x unified",
    )
    st.plotly_chart(fig_decay, use_container_width=True)

    # 하단 상태 요약 창 (기존 들여쓰기 공백 4칸 유지)
    st.subheader("📝 실시간 분석 요약")
    type_str = "약산성" if is_acid else "약염기성"
    info_msg = f"현재 선택된 약물: {drug_name} | 성격: {type_str} | 고유 pKa: {pKa}"
    st.info(info_msg)
