# DAT-web 프로젝트

> Data Analysis Tool

## 프로젝트 개요

이 프로젝트는 FastAPI를 사용한 백엔드 API 서버와 Streamlit을 사용한 웹 인터페이스로 구성된 풀스택 애플리케이션입니다. Docker와 Docker Compose를 통해 개발 및 배포 환경을 구성합니다.

## 기술 스택

- **백엔드**: FastAPI
- **프론트엔드**: Streamlit
- **컨테이너화**: Docker, Docker Compose
- **웹 서버**: Nginx
- **프로세스 관리**: Supervisor
- **스토리지**: AWS S3 (개발 환경에서는 LocalStack)

## 프로젝트 구조

```
.
├── backend/                  # FastAPI 백엔드 서버
├── frontend/                    # Streamlit 웹 애플리케이션
├── dockerfiles/                 # 서비스별 Dockerfile
├── .env.example                 # 환경 변수 예제
├── docker-compose.yml           # Docker Compose 설정
├── Dockerfile                   # 프로덕션용 Dockerfile
├── requirements.txt             # Python 패키지 의존성
├── nginx.conf                   # Nginx 설정
└── supervisord.conf             # Supervisor 설정
```

## 스크립트 & 인프라 (Scripts & Infra)

| 파일/설정                        | 설명                               |
|---------------------------------|------------------------------------|
| `scripts/rds-connect.sh`        | RDS 터널링 연결 스크립트           |
| `scripts/rds-disconnect.sh`     | RDS 터널링 해제 스크립트           |
| `Dockerfile`                    | 백엔드·프론트엔드 컨테이너 정의      |
| `docker-compose.yml`            | 멀티 컨테이너 오케스트레이션       |
| `nginx.conf`                    | 리버스 프록시 설정                  |
| `supervisord.conf`              | 프로세스 관리 설정                 |
| `Makefile`                      | 빌드·테스트·마이그레이션 자동화     |
| `pyproject.toml`, `apt-packages.txt` | 의존성 및 패키지 목록               |


## 서브 프로젝트 문서

프로젝트의 각 구성 요소에 대한 자세한 내용은 다음 문서를 참조하세요:

- [백엔드 문서](backend/README.md) - 백엔드 구성 및 개발 가이드
- [프프론트엔드 문서](frontend/README.md) - 프론트엔드 구성 및 개발 가이드

## 개발 환경 설정

### 필수 요구사항

- Docker 및 Docker Compose 설치
- git
- make (optional)

### 로컬 개발 환경 설정

1. 저장소 클론:

   ```bash
   git clone <저장소 URL>
   cd <프로젝트 디렉토리>
   ```

2. 환경 변수 설정:

   ```bash
   cp .env.example .env
   # .env 파일을 적절히 수정하세요
   ```

3. Docker Compose로 서비스 실행:

   ```bash
   docker-compose up
   ```

   또는 Makefile을 사용하여 실행:

   ```bash
   make dev
   ```

4. 서비스 접근:
   - **애플리케이션 (Nginx)**: http://localhost:8000
     - **FastAPI (API 서버)**: http://localhost:8000/api
     - **Streamlit (웹)**: http://localhost:8000/ (별도 경로 없음)
   - **PostgreSQL 데이터베이스**: `localhost:5433`
   - **LocalStack (S3)**: http://localhost:4566

### Makefile 주요 명령어

`Makefile`을 사용하여 개발 환경을 더 쉽게 관리할 수 있습니다.

- **개발 환경 시작**:
  ```bash
  make dev
  ```
- **개발 환경 중지**:
  ```bash
  make dev-down
  ```
- **이미지 다시 빌드**:
  ```bash
  make dev-build
  ```
- **라이브러리 설치**:
  `requirements.txt`에 라이브러리를 추가한 후, 아래 명령어로 이미지를 다시 빌드합니다.
  ```bash
  make install lib=라이브러리명
  ```
- **데이터베이스 마이그레이션**:
  - 새 마이그레이션 생성: `make revision-db msg="Your message"`
  - 마이그레이션 적용: `make upgrade-db`
  - 데이터베이스 초기화: `make reset-db`

## 코드 컨벤션 및 스타일 가이드

이 프로젝트는 일관된 코드 품질과 스타일을 유지하기 위해 **Ruff**를 사용합니다.

- **스타일 검사 및 포맷팅 적용**:
  ```bash
  make style
  ```
- **스타일 검사만 수행**:
  ```bash
  make check-quality
  ```

## 개발 환경 특징

- **로컬 환경 (`ENV=local`)**:
  - LocalStack을 사용하여 S3 서비스 에뮬레이션
  - 데이터베이스는 Docker 컨테이너 내 PostgreSQL 사용
  - 모든 서비스는 Docker 네트워크 내에서 통신
- **프로덕션 환경 (`ENV=production`)**:
  - 실제 AWS S3 사용
  - 동일한 코드베이스로 원활하게 전환 가능

### 로컬 환경 안내

과거에는 FastAPI와 Streamlit이 별도의 컨테이너로 구성했지만, 현재는 프로덕션 환경과 동일하게 단일 컨테이너로 동작합니다.  
Nginx, Supervisor, FastAPI, Streamlit가 포함된 단일 컨테이너와 PostgreSQL, LocalStack 3개의 컨테이너를 Compose하여 빌드하고 실행합니다.  

## 프로덕션 환경 안내

프로덕션 환경은 단일 컨테이너(`Dockerfile`)로 빌드되며, Nginx, Supervisor, FastAPI, Streamlit이 모두 포함됩니다.

### Nginx 라우팅 설정

프로덕션 환경의 Nginx는 다음과 같이 요청을 라우팅합니다:
- `http://localhost/api/*` -> **FastAPI 서버**
- `http://localhost/*` -> **Streamlit 앱**

### 프로덕션 환경 구성

프로덕션 환경에서는 다음과 같은 구성으로 작동합니다:

1. **Nginx**: 외부에서 들어오는 요청을 처리하며, 정적 파일 제공 및 FastAPI와 Streamlit 서비스로 트래픽을 라우팅합니다.

   - 포트 80에서 수신
   - `/api/*` 요청은 FastAPI 서버(8000 포트)로 프록시
   - `/` 경로의 요청은 Streamlit 앱(8501 포트)으로 프록시

2. **Supervisor**: 다음 세 개의 프로세스를 관리합니다:
   - Nginx 웹 서버
   - FastAPI 백엔드 서버
   - Streamlit 웹 애플리케이션

### Nginx 설정

프로덕션 환경의 Nginx는 다음과 같은 설정으로 구성되어 있습니다:

- 웹 서버 포트: 80
- FastAPI 서버 프록시 경로: `/api`
- Streamlit 앱 프록시 경로: `/`
- 정적 파일 캐싱 및 gzip 압축 적용

`nginx.conf` 파일에서 이러한 설정을 확인하고 필요에 따라 수정할 수 있습니다.

# Gitea -> Github 코드 미러링 가이드

Gitea → GitHub 미러링 가이드 (bot 계정 / PAT 갱신)

1. 배경
   Gitea를 내부 SCM(소스코드 관리) 서버로 사용 중이며, 소스 변경 사항을 GitHub에 자동으로 푸시 미러링 하고 있습니다.
   GitHub Actions를 이용하면 도커 빌드, AWS OIDC 인증 등을 간편하게 설정할 수 있으나, 현재 Gitea는 AWS OIDC 등 복잡한 CI 설정이 어려워 Actions를 활용하기 위해 미러링 방식을 선택했습니다.
   GitHub 쪽 저장소는 봇 계정(whatslab-corps 깃허브 계정)의 PAT(Personal Access Token)으로 인증하여 Force Push 동기화를 수행하고 있습니다.
   PAT는 만료 기한이 존재하므로, 만료 시점에 새로운 토큰을 발급받아 Gitea의 미러링 설정을 갱신해주어야 합니다.

2. 현재 구성 요약
   GitHub 봇 계정: whatslab@whatslab.co.kr 계정으로 로그인 된 깃허브 계정

Organization(또는 개인) 내 저장소 접근 권한 부여
만료되는 PAT를 주기적으로 갱신해야 함
깃허브 저장소 주소: https://github.com/whats-lab/DAT-mirror.git

Gitea: 내부에 있는 저장소
Settings > Repository > Mirror Settings에서 Push Mirror 설정 완료
Username: whatslab-corp
Password: (발급된 PAT)

3. PAT 만료 시나리오
   Fine-grained 토큰 또는 Classic 토큰 모두 일정 기간(예: 90일, 180일, 365일 등) 후에 만료될 수 있습니다.
   만료 직후부터는 Gitea가 GitHub로 푸시를 시도할 때 인증 오류가 발생하며, "Push Mirror"가 실패하게 됩니다.
   따라서 사전에 만료 알림(이메일 또는 GitHub 알림)을 확인하거나, 만료 직후 재발급 받는 방식을 택해야 합니다.

4. (봇 계정) 새 PAT 발급 절차
   whatslab-corp 계정으로 GitHub에 로그인
   오른쪽 상단 프로필 → Settings → Developer settings → Personal access tokens
   Fine-grained tokens 또는 Tokens (classic) 탭에서 Generate new token 클릭
   Fine-grained 토큰 권장 (필요한 레포 & 권한만 부여 가능)
   Permissions:
   Actions(선택) → Read & Write (워크플로 수정이 필요한 경우)
   Contents → Read & Write (푸시 권한)
   workflow -> Read & Write (워크플로 수정 권한)

만료 기한(Expiration) 설정 (GitHub 정책에 따라 최대 1년 등)

Generate token으로 토큰 생성
화면에 표시된 토큰 값을 복사 (한 번만 확인 가능)

5. Gitea Push Mirror 설정 갱신
   Gitea 웹 UI에 로그인
   이 저장소로 이동(미러링 대상 저장소)

상단 메뉴에서 설정 → 저장소 클릭

미러 설정 섹션 확인
기존에 등록된 Push Mirror 항목 삭제 -> PAT 만료되서 다시 등록해야함

Authorization 부분의 Password 필드에, 새로 발급받은 PAT(위 4단계에서 복사한 값)을 입력
변경사항이 저장되면, 하단의 Synchronize Now 버튼을 클릭하여 즉시 푸시 동작이 정상인지 확인
로그(또는 UI 메시지)에 에러 없이 푸시가 완료되면 성공

6. 유의사항 / 추가 팁
   이력(Force Push) 주의

기존에 GitHub 레포가 다른 이력을 가지고 있지 않다면 문제 없으나, 혹시 GitHub에서 수동 커밋이 발생하는 경우 Force Push로 덮어쓸 수 있음.
팀 내부에서 GitHub 쪽에 직접 푸시하지 않고, 모든 코드는 Gitea 원본 → GitHub 미러 흐름을 유지하는 것이 안전.

만료 시점 관리
GitHub에서 PAT 만료가 다가오면 발급 계정(깃허브봇계정)에 알림(이메일 등)이 갈 수 있으니, 계정 메일함을 체크하거나 별도 관리가 필요
만료 전 토큰 재발급이 가능하면 미리 바꿔두면 좋음

7. 요약
   봇 계정(깃허브봇계정)이 발급한 PAT를 이용해, Gitea에서 GitHub로 푸시 미러링 중.
   PAT 만료 시, Gitea 미러링이 실패하므로, 새로운 PAT 발급 후 Gitea의 Mirror Settings에서 토큰을 갱신해야 함.
   GitHub Actions는 Gitea → GitHub 푸시 트리거로 자동 실행되어 도커 빌드/배포(AWS OIDC 등)를 수행.
   주기적으로 만료 알림을 모니터링하거나, 만료 날짜를 사내 달력 등에 관리하여 안정적인 배포 환경 유지.
   문의: 토큰 만료나 Actions 관련 에러 발생 시, DevOps 담당자 또는 사내 CI/CD 관리팀에 문의.

[GitHub](https://github.com/whats-lab/DAT-mirror)에서 Actions 파이프라인을 확인 후, 문제가 발생하면 즉시 공유 부탁드립니다.
