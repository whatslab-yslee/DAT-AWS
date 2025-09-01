import os

import altair as alt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st


def print_clustering_result():
    # _, contents_name, contents_level, _ = file_name.split("_")
    # 스크리닝 결과 :  {clustering_result(contents_name,contents_level,extract_corr(df))}
    text = """
            ```
            스크리닝 결과 : 일단 비워둠

            (해당 결과는 정상 비정상을 나타낸 것이 아닌 군집을 나타낸 숫자입니다.)

            현재 군집 분류 모델은 Test용 모델로 추후 개선 계획이 있습니다.

            아래의 도표는 분류 기준을 나타냅니다.

            왼쪽 그래프는 분류하는 기준 값을 나타내고 오른쪽 그래프는 환자 데이터를 나타냅니다.

            왼쪽 그래프의 빨간 볼드 항목이 주요 분류 기준입니다.
            빨간 볼드 항목의 값이 가까운쪽으로 환자 데이터를 분류합니다.
            ```
            """
    return text


def print_profile(file_name, patient_name, score, time_spent, fps):
    _, content, level, timestr = file_name.split("_")
    timestr = timestr.split(".")[0]
    text = f"""
            ```json
            "환자 이름" : {patient_name}
            "콘텐트 이름" : {content}
            "난이도" : {level}
            "파일 번호" : {timestr}
            "점수" : {score}
            "운동시간 (초)" : {round(time_spent, 2)}
            "정보량 (fps)" : {round(fps, 2)}
            ```
            """
    return text


def report(df: pd.DataFrame, file_name: str, content_type: str, fps: float) -> None:
    # st.caption("환자 프로필")
    # st.markdown(print_profile(file_name, patient_name, score, time_spent, fps))
    # st.write("")

    st.caption("환자 HMD 데이터 분석 그래프 Rotation")
    st.plotly_chart(rotation_graph(df))

    if content_type == "TennisBall":
        st.caption("환자 컨트롤러 데이터 분석 그래프 Position")
        st.plotly_chart(position_graph_1(df))
        if st.checkbox("정규화된 position 데이터 보기"):
            st.caption("환자 컨트롤러 데이터 분석 그래프 Position (scaled)")
            st.plotly_chart(position_graph_2(df))

        if st.checkbox("위치 정보 애니메이션 생성"):
            st.plotly_chart(create_animation(df, int(fps)))

    # st.caption("과업 성공/실패 차트")
    # _display_events_chart(df)

    st.caption("환자 데이터 파일")
    st.dataframe(df)

    st.download_button("CSV 파일 다운로드", data=df.to_csv(index=False), file_name=file_name)

    # st.markdown(print_clustering_result())

    # st.caption('Clustering 근거 도표')
    # st.pyplot(draw_heatmap(df,file_name.split('_')[1],file_name.split('_')[2],
    #                        clustering_result(file_name.split('_')[1],file_name.split('_')[2],extract_corr(df))))


def _find_time_column(df: pd.DataFrame) -> str:
    """데이터프레임에서 시간 관련 컬럼을 찾습니다."""
    for col in df.columns:
        if "time" in col.lower() and df[col].dtype != "object":
            return col
    return None


def _find_state_column(df: pd.DataFrame) -> str:
    """데이터프레임에서 상태/점수 관련 컬럼을 찾습니다."""
    for col in df.columns:
        if "state" in col.lower() or "score" in col.lower():
            return col
    return None


def _display_events_chart(df: pd.DataFrame) -> None:
    """이벤트 발생 시점 차트를 표시합니다."""
    time_col = _find_time_column(df)
    state_col = _find_state_column(df)

    if not time_col or not state_col:
        return

    # 이벤트가 있는 데이터만 필터링
    events_df = df[df["event"].notnull() & (df["event"] != "")]

    if events_df.empty:
        return

    # 이벤트 타입별로 색상 지정
    color_scale = alt.Scale(domain=["Success", "Fail"], range=["#28a745", "#dc3545"])

    events_chart = (
        alt.Chart(events_df)
        .mark_circle(size=100)
        .encode(
            x=alt.X(f"{time_col}:Q", title="시간"),
            y=alt.Y(f"{state_col}:Q", title="상태/점수"),
            color=alt.Color("event:N", scale=color_scale),
            tooltip=["event", time_col, state_col, "spend_time"],
        )
        .properties(width=700, height=300)
        .interactive()
    )

    st.altair_chart(events_chart, use_container_width=True)


def position_graph_1(df):
    fig = px.line(
        df,
        x="current_time",
        y=["Position_X", "Position_Y", "Position_Z"],
        markers=False,
        line_shape="linear",
        render_mode="svg",
    )
    fig = draw_event(df, fig, ["Position_X", "Position_Y", "Position_Z"])
    return fig


def position_graph_2(df):
    fig = px.line(
        df,
        x="current_time",
        y=["Scaled_Position_X", "Scaled_Position_Y", "Scaled_Position_Z"],
        markers=False,
        line_shape="linear",
        render_mode="svg",
    )
    fig = draw_event(df, fig, ["Scaled_Position_X", "Scaled_Position_Y", "Scaled_Position_Z"])
    return fig


def rotation_graph(df):
    fig = px.line(
        df,
        x="current_time",
        y=["Rotation_X", "Rotation_Y", "Rotation_Z"],
        markers=False,
        line_shape="linear",
        render_mode="svg",
    )
    fig = draw_event(df, fig, ["Rotation_X", "Rotation_Y", "Rotation_Z"])
    return fig


def draw_event(df, fig, columns):
    score = df["Score"]
    dmax = df[columns].values.max()
    dmin = df[columns].values.min()
    cnt = 0

    for i in range(1, len(score)):
        if df["event"][i] == "Success":
            cnt += 1
            fig.add_trace(
                go.Scatter(
                    x=[df.iloc[i]["current_time"], df.iloc[i]["current_time"]],
                    y=[dmin, dmax],
                    mode="lines",
                    line={"color": "green", "width": 2, "dash": "dash"},
                    name=f"{cnt}번째 성공",
                )
            )
        if df["event"][i] == "Fail":
            fig.add_trace(
                go.Scatter(
                    x=[df.iloc[i]["current_time"], df.iloc[i]["current_time"]],
                    y=[dmin, dmax],
                    mode="lines",
                    line={"color": "yellow", "width": 2, "dash": "dash"},
                    name="실패",
                )
            )
    return fig


def create_animation(df, default=60):
    # Group data into 30 fps intervals
    df = df.copy()
    max = df.shape[0]
    if max < default:
        default = max
    gap = st.slider("fps 설정 (기본값: 1초에 재생되는 모든 프레임)", 1, max, default)
    df["frame"] = (df.index // gap).astype(int)

    fig = px.scatter_3d(
        df,
        x="Position_Z",
        y="Position_X",
        z="Position_Y",
        animation_frame="frame",
        range_x=[df["Position_Z"].min(), df["Position_Z"].max()],
        range_y=[df["Position_X"].min(), df["Position_X"].max()],
        range_z=[df["Position_Y"].min(), df["Position_Y"].max()],
        title="3D Position Tracking",
        opacity=0.8,
    )

    fig.add_trace(
        go.Scatter3d(
            x=df["Position_Z"],
            y=df["Position_X"],
            z=df["Position_Y"],
            mode="lines",
            line={"color": "black", "width": 2},
            name="전체 궤적",
        )
    )

    fig.update_layout(
        scene={
            "xaxis_title": "Position Z",
            "yaxis_title": "Position X",
            "zaxis_title": "Position Y",
            "aspectmode": "cube",
        },
        margin={"l": 0, "r": 0, "t": 30, "b": 0},
        height=600,
        width=800,
        sliders=[
            {
                "steps": [
                    {
                        "args": [
                            [f.name],
                            {
                                "frame": {"duration": 10, "redraw": True},
                                "mode": "immediate",
                            },
                        ],
                        "label": f.name,
                        "method": "animate",
                    }
                    for f in fig.frames
                ],
                "transition": {"duration": 0},
            }
        ],
        updatemenus=[
            {
                "buttons": [
                    {
                        "args": [
                            None,
                            {
                                "frame": {"duration": 100, "redraw": True},
                                "fromcurrent": True,
                                "mode": "immediate",
                            },
                        ],
                        "label": "재생",
                        "method": "animate",
                    },
                    {
                        "args": [
                            [None],
                            {
                                "frame": {"duration": 0, "redraw": True},
                                "mode": "immediate",
                            },
                        ],
                        "label": "정지",
                        "method": "animate",
                    },
                ],
                "showactive": True,
                "type": "buttons",
            }
        ],
    )

    fig.update_traces(
        marker={
            "size": 3,
            "color": "blue",
            "opacity": 0.6,
            "symbol": "circle",
        }
    )

    df = df.drop(["frame"], axis=1)

    return fig


def local_css(file_path: str) -> None:
    """로컬 CSS 파일을 페이지에 삽입합니다."""
    if os.path.exists(file_path):
        with open(file_path, encoding="utf8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning(f"CSS 파일을 찾을 수 없습니다: {file_path}")


def web_css(file_path: str) -> None:
    """웹에서 CSS 파일을 가져옵니다."""
    try:
        response = requests.get(file_path)
        response.raise_for_status()  # HTTP 오류가 발생하면 예외를 발생시킵니다.
        st.markdown(f"<style>{response.text}</style>", unsafe_allow_html=True)
    except requests.exceptions.RequestException as e:
        st.error(f"CSS 파일을 불러오는 데 실패했습니다: {e}")
