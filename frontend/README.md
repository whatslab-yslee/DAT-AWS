# DAT-web 웹 애플리케이션 (Streamlit)

## 1. 개요

이 문서는 DAT-web 프로젝트의 프론트엔드 웹 애플리케이션에 대한 기술적인 내용을 상세히 설명합니다. 이 애플리케이션은 의사 및 의료진을 위한 관리 도구로, Streamlit 프레임워크를 사용하여 구축되었습니다.

주요 기능은 다음과 같습니다:
- **사용자 인증**: 백엔드 API와 연동하여 안전한 로그인, 로그아웃 및 토큰 기반 세션 관리를 제공합니다.
- **환자 관리**: 담당 환자를 등록, 조회, 수정, 삭제하는 기능을 제공합니다.
- **진단 수행 및 모니터링**: VR 장비를 착용한 환자의 진단을 시작하고, Server-Sent Events(SSE)를 통해 진단 상태를 실시간으로 모니터링합니다.
- **결과 조회 및 분석**: 완료된 진단의 상세 결과(메타데이터, 원본 CSV 데이터)를 조회하고, 그래프를 통해 시각적으로 분석합니다.

## 2. 기술 스택

- **프레임워크**: Streamlit
- **데이터 처리**: pandas
- **시각화**: Plotly, Altair
- **API 통신**: requests, httpx (for SSE)

## 3. 프로젝트 구조

```
frontend/
├── .streamlit/
│   └── config.toml         # Streamlit 앱 설정 (테마, 사이드바 등)
├── assets/                 # 정적 파일 (CSS, 테스트 데이터)
│   ├── css/                # UI 커스터마이징을 위한 CSS 파일
│   └── data/               # 테스트용 CSV 데이터
└── src/                    # 핵심 애플리케이션 소스 코드
    ├── main.py             # Streamlit 앱의 메인 진입점
    ├── pages/              # Streamlit 멀티페이지 앱 구조
    │   ├── 1_tutorial.py   # 사용 가이드 페이지
    │   ├── 2_database.py   # 진단 기록 조회 페이지
    │   └── 3_patient.py    # 환자 관리 페이지
    ├── api_clients/        # 백엔드 API 통신 클라이언트
    │   ├── schemas/        # API 요청/응답 데이터 검증을 위한 Pydantic 스키마
    │   ├── auth_client.py
    │   ├── base_client.py
    │   ├── diagnosis_client.py
    │   ├── diagnosis_record_client.py
    │   ├── patient_client.py
    │   └── sse_client.py   # SSE 통신 전용 클라이언트
    ├── components/         # 재사용 가능한 UI 컴포넌트
    │   ├── date_selector.py # 날짜 범위 선택 UI
    │   ├── graphic.py      # 데이터 시각화(그래프, 리포트) 로직
    │   ├── sidebar_navigation.py # 커스텀 사이드바 내비게이션
    │   ├── sse_renderer.py # SSE 이벤트 수신 및 UI 렌더링
    │   └── timer.py        # HTML/JS 기반 클라이언트 사이드 타이머
    ├── constants/          # 전역 상수 (경로, 텍스트, 콘텐츠 정보 등)
    ├── services/           # UI와 API 클라이언트 사이의 비즈니스 로직
    │   ├── auth_service.py
    │   ├── examination_service.py
    │   └── patient_service.py
    ├── state.py            # Streamlit 세션 상태(session_state) 관리
    └── utils/              # 범용 유틸리티 함수 (JWT, 시간 변환, 쿠키 관리 등)
```

## 4. 코드 구성

### 설정 파일

| 파일                                          | 설명                             |
|-----------------------------------------------|----------------------------------|
| `.streamlit/config.toml`                      | Streamlit 기본 설정               |
| `src/config.py`                               | API 엔드포인트, 토큰 키 등 정의   |

### API 클라이언트

> 백엔드와 HTTP/WS 통신 담당

| 파일                                      | 역할                                   |
|-------------------------------------------|----------------------------------------|
| `api_clients/base_client.py`              | 공통 HTTP 클라이언트(Configuration)    |
| `api_clients/auth_client.py`              | `/auth` 관련 호출                      |
| `api_clients/patient_client.py`           | `/patients` 관련 호출                  |
| `api_clients/diagnosis_client.py`         | `/diagnosis` 관련 호출                 |
| `api_clients/diagnosis_record_client.py`  | `/diagnosis_records` 및 SSE 처리       |
| `api_clients/sse_client.py`               | SSE 이벤트 수신                         |
| `api_clients/vr_mock_client.py`           | WebSocket 연결 관리                    |
| `api_clients/schemas/*.py`                | 요청·응답 데이터 모델                  |

### 컴포넌트 (Components)

| 파일                               | 설명                                       |
|------------------------------------|--------------------------------------------|
| `components/sidebar_navigation.py` | 사이드바 메뉴                              |
| `components/date_selector.py`      | 날짜 선택 위젯                              |
| `components/graphic.py`            | 진단 결과 그래픽 렌더링                    |
| `components/sse_renderer.py`       | SSE 이벤트 실시간 렌더링                   |
| `components/vr_mock_renderer.py`   | VR 모의 실험 화면                          |
| `components/timer.py`              | 카운트다운/스톱워치 기능                    |

### 페이지 (Pages)

| 파일                             | 설명                   |
|----------------------------------|------------------------|
| `pages/1_tutorial.py`            | 튜토리얼 페이지        |
| `pages/2_database.py`            | 데이터베이스 뷰         |
| `pages/3_patient.py`             | 환자 정보 관리 페이지    |

### 서비스 (Services)

| 파일                             | 기능                                    |
|----------------------------------|-----------------------------------------|
| `services/auth_service.py`       | 로그인·토큰 관리                        |
| `services/patient_service.py`    | 환자 데이터 CRUD                        |
| `services/examination_service.py`| 진단 워크플로우                          |
| `services/analysis_service.py`   | 진단 결과 데이터 분석                   |

### 유틸리티 (Utils)

| 파일                              | 설명                                     |
|-----------------------------------|------------------------------------------|
| `utils/js_eval.py`                | 사용자 입력 JavaScript 평가              |
| `utils/jwt.py`                    | JWT 토큰 인코딩/디코딩                   |
| `utils/time.py`                   | 시간 포맷 변환                           |

---

## 5. 핵심 기능 및 아키텍처

### 상태 관리 (State Management)
Streamlit의 `st.session_state`를 사용하여 사용자 로그인 상태, 선택된 환자, 진단 진행 상태 등 모든 클라이언트 측 상태를 관리합니다. `src/state.py`의 `init_all_states()` 함수가 앱 실행 시 모든 세션 변수를 안전하게 초기화하여 일관성을 유지합니다.

### API 통신 및 서비스 계층
- **`api_clients`**: 각 API 엔드포인트 그룹(auth, patient 등)에 맞춰 클래스로 분리되어 있습니다. HTTP 요청/응답 처리, 데이터 직렬화/역직렬화 등 저수준의 통신 로직을 담당합니다.
- **`services`**: `api_clients`를 호출하고, 그 결과를 `st.session_state`에 저장하거나 UI 렌더링에 필요한 데이터로 가공하는 등 애플리케이션의 비즈니스 로직을 처리합니다. 예를 들어, `auth_service.py`는 로그인 API 호출 후 성공 시 토큰 정보를 세션에 저장하고 로그인 상태 플래그를 `True`로 설정합니다.

### 페이지 라우팅
Streamlit의 내장 멀티페이지 기능을 사용합니다. `src/pages/` 디렉토리 내의 파일들이 자동으로 페이지로 인식됩니다. `.streamlit/config.toml`에서 기본 사이드바 내비게이션을 비활성화(`showSidebarNavigation = false`)하고, `components/sidebar_navigation.py`에서 `st.page_link`를 사용하여 커스텀 내비게이션 UI를 구현합니다.

### 실시간 진단 모니터링 (SSE)
- **`sse_client.py`**: `httpx` 라이브러리를 사용하여 백그라운드 스레드에서 SSE 엔드포인트에 연결하고, 수신된 이벤트를 `queue`에 담습니다.
- **`sse_renderer.py`**: 메인 스레드에서 주기적으로 큐를 확인하여 이벤트를 가져오고, `st.session_state`를 업데이트한 후 `st.rerun()`을 호출하여 UI를 실시간으로 갱신합니다. 이를 통해 진단 상태, 타이머 등을 동적으로 표시합니다.

### 인증 흐름
1.  **로그인**: 사용자가 ID/PW를 입력하면 `auth_service`가 `auth_client.login()`을 호출합니다.
2.  **토큰 저장**: 로그인 성공 시, 백엔드로부터 받은 `access_token`은 `st.session_state`에, `refresh_token`은 `streamlit-js-eval` 유틸리티를 통해 브라우저의 HttpOnly 쿠키에 저장됩니다.
3.  **세션 유지**: 페이지 이동 시 `init_auth_states` 함수가 쿠키의 `refresh_token`을 확인하여 자동으로 로그인을 연장하거나, `access_token`의 유효성을 검증합니다.
4.  **로그아웃**: 로그아웃 시 서버에 토큰 만료를 요청하고, 세션과 쿠키를 모두 정리합니다.

## 6. UI 커스터마이징

애플리케이션의 전반적인 스타일은 `assets/css/` 디렉토리의 CSS 파일들을 통해 커스터마이징됩니다. `components/graphic.py`의 `local_css` 함수를 통해 각 페이지에 필요한 CSS가 주입됩니다.

## 7. 로컬 개발 환경 실행

Streamlit 앱을 로컬에서 실행하려면 다음 명령어를 사용하세요.

```bash
streamlit run src/main.py
```

앱이 실행되면 브라우저에서 `http://localhost:8501` 주소로 접속할 수 있습니다.
