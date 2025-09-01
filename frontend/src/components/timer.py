import streamlit.components.v1 as components


def client_side_timer(total_seconds: int = 60, key: str = "default", height: int = 56):
    timer_id = f"timer_{key}"
    wrapper_id = f"timer_wrapper_{key}"

    # Streamlit alert에 사용되는 색상

    # 파란색 (정보성)
    blue_bg_color = "rgba(28, 131, 225, 0.1)"
    blue_text_color = "rgb(0, 66, 128)"

    # 초록색 (성공/완료)
    # green_bg_color = "rgba(33, 195, 84, 0.1)"
    # green_text_color = "rgb(23, 114, 51)"

    # 빨간색 (실패/오류)
    red_bg_color = "rgba(255, 43, 43, 0.09)"
    red_text_color = "rgb(125, 53, 59)"

    if total_seconds < 0:
        components.html(
            f"""
            <style>
                body {{
                    margin: 0;
                }}
                #{wrapper_id} {{
                    padding: 1rem;
                    border-radius: 0.5rem;
                    display: flex;
                    align-items: center;
                    font-family: "Source Sans Pro", sans-serif;
                    box-sizing: border-box;
                    width: 100%;
                    background-color: {red_bg_color};
                }}
                .timer-ended-message {{
                    font-size: 16px;
                    font-weight: normal;
                    color: {red_text_color};
                }}
            </style>

            <div id="{wrapper_id}">
                <div class="timer-ended-message">
                    세션 유효시간이 종료되었습니다. 새로운 진단을 시작해주세요.
                </div>
            </div>
            """,
            height=height,
        )
        return

    minutes = total_seconds // 60
    seconds = total_seconds % 60

    components.html(
        f"""
        <style>
            /* HTML body의 기본 마진 제거 */
            body {{
                margin: 0;
            }}
            /* 전체 wrapper div의 Streamlit alert 스타일 */
            #{wrapper_id} {{
                padding: 1rem; /* alert와 유사한 패딩 */
                border-radius: 0.5rem; /* 둥근 모서리 */
                display: flex;
                align-items: center;
                font-family: "Source Sans Pro", sans-serif;
                box-sizing: border-box; /* 패딩이 width에 포함되도록 */
                width: 100%; /* 부모 컨테이너에 꽉 차게 */

                /* 초기 상태: 파란색 배경 */
                background-color: {blue_bg_color};
                color: {blue_text_color};
            }}
            /* "세션 유효시간:" 라벨 스타일 */
            #{wrapper_id} > div:first-child {{
                font-size: 16px; /* 이미지의 alert 폰트 크기와 유사하게 */
            }}
            /* 타이머 숫자 스타일 */
            #{timer_id} {{
                font-size: 16px;
                color: {blue_text_color}; /* 초기 상태 글씨색 */
            }}
            /* 종료 메시지 스타일 (자바스크립트에서 innerHTML로 대체될 때 적용) */
            .timer-ended-message {{
                font-size: 16px;
                font-weight: normal; /* 종료 메시지는 굵게 하지 않음 */
                color: {red_text_color}; /* 종료 메시지 글씨색 */
            }}
        </style>

        <div id="{wrapper_id}">
            <div>진단 세션 유효시간:</div>
            <div id="{timer_id}">{minutes:02d}:{seconds:02d}</div>
        </div>

        <script>
        let time_{key} = {total_seconds};
        let interval_{key} = setInterval(function() {{
            if (time_{key} < 0) {{
                clearInterval(interval_{key});

                const wrapper = document.getElementById('{wrapper_id}');
                // 종료 메시지로 내용 교체
                wrapper.innerHTML = `
                    <div class="timer-ended-message">
                        세션 유효시간이 종료되었습니다. 새로운 진단을 시작해주세요.
                    </div>
                `;
                // 배경색을 빨간색으로 변경
                wrapper.style.backgroundColor = "{red_bg_color}";
                return;
            }}
            let minutes = String(Math.floor(time_{key} / 60)).padStart(2, '0');
            let seconds = String(time_{key} % 60).padStart(2, '0');
            document.getElementById('{timer_id}').innerText = minutes + ":" + seconds;
            time_{key}--;
        }}, 1000);
        </script>
        """,
        height=height,
    )
