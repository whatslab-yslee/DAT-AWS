import json
import queue
import threading
import time
import traceback
from typing import Callable, Dict, List, Optional

import httpx
import pandas as pd
import streamlit as st


class SSEClient:
    """
    SSE 클라이언트 클래스
    서버로부터 Server-Sent Events를 수신하는 기능을 제공합니다.
    """

    def __init__(self):
        # 세션 상태 초기화
        if "sse_queue" not in st.session_state:
            st.session_state.sse_queue = queue.Queue()
        if "sse_events" not in st.session_state:
            st.session_state.sse_events = []
        if "sse_connected" not in st.session_state:
            st.session_state.sse_connected = False
        if "sse_error" not in st.session_state:
            st.session_state.sse_error = None

    def start_sse_connection(self, endpoint_url: str, headers: Optional[Dict] = None, on_event: Optional[Callable] = None) -> bool:
        """
        SSE 연결을 시작합니다.

        Args:
            endpoint_url: SSE 엔드포인트 URL
            headers: HTTP 요청 헤더
            on_event: 이벤트 수신 시 호출될 콜백 함수

        Returns:
            bool: 연결 시작 성공 여부
        """

        # 상태 초기화
        st.session_state.sse_events = []
        st.session_state.sse_connected = True
        st.session_state.sse_error = None

        # 큐 비우기 (이전 연결의 잔여 데이터 제거)
        while not st.session_state.sse_queue.empty():
            try:
                st.session_state.sse_queue.get_nowait()
            except queue.Empty:
                break

        # 기본 헤더 설정 (Accept: text/event-stream)
        if headers is None:
            headers = {}
        if "Accept" not in headers:
            headers["Accept"] = "text/event-stream"

        # 백그라운드 스레드에서 SSE 리스너 시작
        thread = threading.Thread(target=self._sse_listener, args=(endpoint_url, headers, st.session_state.sse_queue, on_event), daemon=True)
        thread.start()

        return True

    def stop_sse_connection(self) -> bool:
        """
        SSE 연결을 종료합니다.

        Returns:
            bool: 연결 종료 요청 성공 여부
        """
        if not st.session_state.get("sse_connected", False):
            print("활성화된 SSE 연결이 없습니다.")
            return False

        # 종료 플래그 설정 (리스너 스레드가 확인)
        st.session_state.sse_connected = False

        # 큐 비우기
        while not st.session_state.sse_queue.empty():
            try:
                st.session_state.sse_queue.get_nowait()
            except queue.Empty:
                break

        # 이벤트 목록 초기화
        st.session_state.sse_events = []

        print("SSE 연결 종료 요청 완료")
        return True

    def get_events(self) -> List[Dict]:
        """
        수신된 SSE 이벤트 목록을 반환합니다.

        Returns:
            List[Dict]: 수신된 이벤트 목록
        """
        self._process_queue()  # 큐에서 이벤트 처리
        return st.session_state.get("sse_events", [])

    def get_events_dataframe(self) -> Optional[pd.DataFrame]:
        """
        수신된 SSE 이벤트를 DataFrame으로 변환하여 반환합니다.

        Returns:
            Optional[pd.DataFrame]: 이벤트 DataFrame 또는 None (이벤트가 없는 경우)
        """
        events = self.get_events()
        if not events:
            return None

        # 이벤트 데이터 추출
        events_df_data = {"시간": [], "이벤트 타입": [], "상태": [], "메시지": []}
        for event in events:
            # event가 딕셔너리인지 확인
            if isinstance(event, dict):
                events_df_data["시간"].append(event.get("timestamp", time.strftime("%Y-%m-%d %H:%M:%S")))
                events_df_data["이벤트 타입"].append(event.get("event", "message"))
                events_df_data["상태"].append(event.get("state", "-"))
                events_df_data["메시지"].append(str(event.get("data", event)))
            else:
                # 딕셔너리가 아닌 경우 (예: 단순 문자열) 처리
                events_df_data["시간"].append(time.strftime("%Y-%m-%d %H:%M:%S"))
                events_df_data["이벤트 타입"].append("unknown")
                events_df_data["상태"].append("-")
                events_df_data["메시지"].append(str(event))

        try:
            return pd.DataFrame(events_df_data)
        except Exception as e:
            print(f"DataFrame 생성 오류: {e}")
            return None

    def is_connected(self) -> bool:
        """
        SSE 연결 상태를 확인합니다.

        Returns:
            bool: 연결 활성화 여부
        """
        return st.session_state.get("sse_connected", False)

    def get_error(self) -> Optional[str]:
        """
        SSE 연결 오류 메시지를 반환합니다.

        Returns:
            Optional[str]: 오류 메시지 또는 None (오류 없는 경우)
        """
        return st.session_state.get("sse_error")

    def _process_queue(self) -> bool:
        """
        이벤트 큐를 처리하여 session_state.sse_events에 추가합니다.

        Returns:
            bool: 새 이벤트가 추가되었는지 여부
        """
        new_events_added = False
        while not st.session_state.sse_queue.empty():
            try:
                event_data = st.session_state.sse_queue.get_nowait()
                if event_data == "STOP":  # 종료 시그널
                    st.session_state.sse_connected = False
                    print("Stop signal received from queue")
                    break
                elif isinstance(event_data, Exception):  # 에러
                    st.session_state.sse_error = f"SSE 오류: {event_data}"
                    st.session_state.sse_connected = False
                    print(f"Error signal received from queue: {event_data}")
                    break
                else:
                    # 이벤트를 session_state.sse_events에 추가
                    current_events = st.session_state.sse_events
                    st.session_state.sse_events = current_events + [event_data]
                    new_events_added = True
                    st.session_state.sse_error = None  # 성공적으로 받으면 에러 메시지 초기화
            except queue.Empty:
                break
            except Exception as e:
                print(f"Error processing queue: {e}")
                st.session_state.sse_error = f"Queue 처리 오류: {e}"

        return new_events_added

    def _parse_and_process_event(self, current_event: Dict, event_queue: queue.Queue, on_event: Optional[Callable] = None) -> None:
        """이벤트 데이터를 파싱하고 처리합니다.

        Args:
            current_event: 현재 처리할 이벤트 데이터
            event_queue: 이벤트를 전달할 큐
            on_event: 이벤트 수신 시 호출될 콜백 함수
        """
        try:
            data_str = current_event.get("data", "").strip()
            try:
                # 데이터가 여러 줄일 수 있으므로 마지막 개행 제거 후 파싱
                parsed_data = json.loads(data_str.rstrip("\n"))
            except json.JSONDecodeError:
                parsed_data = {"raw_data": data_str.rstrip("\n")}

            # 백엔드 응답 형식에 맞춰 이벤트 구성
            final_event = {
                "id": parsed_data.get("id"),
                "state": parsed_data.get("state"),
                "timestamp": parsed_data.get("timestamp"),
                "event": current_event.get("event", "message"),
            }

            # 에러 응답 처리
            if "error" in parsed_data:
                final_event["error"] = parsed_data["error"]

            # 큐에 이벤트 추가
            event_queue.put(final_event)

            # 상태에 따라 리스너 종료
            if final_event.get("state") not in ["READY", "STARTED"]:
                print(f"[SSEClient] 상태 '{final_event.get('state')}' 감지. 리스너 종료 시도.")
                event_queue.put("STOP")

            # 콜백 함수가 있으면 호출
            if on_event is not None:
                try:
                    on_event(final_event)
                except Exception as callback_err:
                    print(f"[SSEClient] 콜백 함수 호출 오류: {callback_err}")

        except Exception as parse_err:
            print(f"[SSEClient] SSE 이벤트 데이터 처리 중 오류: {parse_err}")
            error_message = f"Event processing error: {parse_err}\nData: {current_event.get('data', '')}"
            event_queue.put(Exception(error_message))

    def _process_sse_line(self, line: str, current_event: Dict) -> None:
        """SSE 라인을 처리하여 현재 이벤트에 추가합니다.

        Args:
            line: 처리할 SSE 라인 바이트
            current_event: 현재 구성 중인 이벤트

        Returns:
            Dict: 업데이트된 현재 이벤트
        """
        # 주석 라인 무시
        if line.startswith(":"):
            return

        try:
            # 필드와 값 분리
            if ":" in line:
                field, value = line.split(":", 1)
                value = value.strip()

                # data 필드는 여러 줄에 걸쳐 올 수 있음
                if field == "data":
                    current_event["data"] = current_event.get("data", "") + value + "\n"
                elif field == "event":
                    current_event["event"] = value
                elif field == "id":
                    current_event["id"] = value
                # retry 필드는 필요시 처리
            else:
                print(f"Ignoring non-standard SSE line: {line}")
        except ValueError:
            print(f"잘못된 형식의 SSE 라인 무시: {line}")

    def _sse_listener(self, url: str, headers: Dict, event_queue: queue.Queue, on_event: Optional[Callable] = None):
        """
        SSE 이벤트를 수신하는 리스너 함수 (스레드에서 실행됨)

        Args:
            url: SSE 엔드포인트 URL
            headers: HTTP 요청 헤더
            event_queue: 이벤트를 전달할 큐
            on_event: 이벤트 수신 시 호출될 콜백 함수
        """
        try:
            timeout = httpx.Timeout(5.0, read=None, pool=None)
            verify_ssl = False

            with httpx.Client(timeout=timeout, verify=verify_ssl) as client:
                with client.stream("GET", url, headers=headers) as response:
                    print(f"SSE 스트림 응답 상태 코드: {response.status_code}")
                    response.raise_for_status()
                    print("SSE 스트림 시작됨. 이벤트 수신 대기...")

                    current_event = {}
                    for line in response.iter_lines():
                        # 종료 플래그 확인
                        if not st.session_state.get("sse_connected", True):
                            print("SSE 연결 중단 플래그 감지됨")
                            break

                        line = line.strip()

                        if not line:  # 빈 라인 (이벤트 구분자)
                            if current_event.get("data"):
                                self._parse_and_process_event(current_event, event_queue, on_event)
                            current_event = {}
                            continue

                        # 라인 처리
                        self._process_sse_line(line, current_event)

                    print("SSE 스트림 종료됨.")

        except httpx.RequestError as exc:
            print(f"SSE 연결 요청 실패: {exc}")
            traceback.print_exc()
            error_message = f"SSE Connection Request Failed: {type(exc).__name__}: {exc}"
            event_queue.put(Exception(error_message))
        except httpx.HTTPStatusError as exc:
            print(f"SSE 연결 실패 (HTTP Status Error): {exc.response.status_code} - {exc}")
            traceback.print_exc()
            error_message = f"SSE Connection Failed (HTTP Status): {exc.response.status_code}"
            event_queue.put(Exception(error_message))
        except Exception as e:
            print(f"SSE 리스너 스레드에서 예상치 못한 오류 발생: {str(e)}")
            traceback.print_exc()
            error_message = f"Unexpected Error in SSE Listener: {type(e).__name__}: {e}"
            event_queue.put(Exception(error_message))
        finally:
            print("SSE 리스너 스레드 종료 처리 완료.")


def get_sse_client() -> SSEClient:
    """
    SSE 클라이언트 인스턴스를 반환합니다.

    Returns:
        SSEClient: SSE 클라이언트 인스턴스
    """
    return SSEClient()
