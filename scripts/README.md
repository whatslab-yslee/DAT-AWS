## **Private RDS 원격 접속 최종 가이드 (자동화 스크립트)**

이 문서는 AWS Private Subnet에 위치한 RDS 데이터베이스에 로컬 PC에서 안전하고 편리하게 접속하기 위한 자동화 스크립트 사용법을 안내합니다.

### **✨ 어떻게 작동하나요?**

이 시스템은 AWS Systems Manager (SSM)를 이용하여 Private Subnet에 있는 '점프 호스트' EC2 인스턴스를 통해 RDS까지 안전한 터널을 생성합니다.

- **`rds-connect.sh` 실행 시:**

  1. 지정된 점프 호스트 EC2 인스턴스의 상태를 확인합니다.
  2. 꺼져있다면 점프 호스트 EC2를 시작시킵니다.
  3. SSM 터널을 생성하여 `localhost:54320`과 Private RDS를 연결합니다.
  4. Ctrl+C 입력 시 자동으로 터널을 종료하고 EC2를 중지합니다.

- **`rds-disconnect.sh` 실행 시:**
  1. 실행 중인 SSM 터널을 강제 종료합니다.
  2. 비용 절감을 위해 점프 호스트 EC2를 다시 중지시킵니다.

---

### **🚨 중요한 보안 경고**

**AWS 자격 증명 관리는 매우 중요합니다!**

- **절대로 하지 말아야 할 것들:**

  - `~/.aws/credentials` 파일을 Git에 커밋하지 마세요
  - AWS 액세스 키를 Slack, 이메일, 메모장 등에 저장하지 마세요
  - 다른 사람과 자격 증명을 공유하지 마세요
  - 스크린샷에 AWS 키가 노출되지 않도록 주의하세요

- **권장 사항:**
  - 정기적으로 액세스 키를 교체하세요
  - 사용하지 않는 키는 즉시 비활성화하세요
  - MFA(다중 인증)를 설정하세요

**⚠️ AWS 키 유출 시 즉시 키를 비활성화하세요!**

---

### **Part 1: 개발자 PC 설정 (각자 1회)**

모든 팀원은 RDS 접속을 위해 자신의 PC에서 아래 설정을 한 번만 수행해야 합니다.

#### **1. 필수 도구 설치**

**Windows 사용자:**

- [AWS CLI 설치 가이드](https://docs.aws.amazon.com/ko_kr/cli/latest/userguide/getting-started-install.html)
- [AWS SSM Plugin 설치 가이드](https://docs.aws.amazon.com/ko_kr/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html)
- [Git Bash 다운로드](https://git-scm.com/download/win) (Bash 스크립트 실행용)

**macOS/Linux 사용자:**

- [AWS CLI 설치 가이드](https://docs.aws.amazon.com/ko_kr/cli/latest/userguide/getting-started-install.html)
- [AWS SSM Plugin 설치 가이드](https://docs.aws.amazon.com/ko_kr/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html)

**설치 확인:**

```bash
aws --version
session-manager-plugin --version
```

#### **2. AWS 액세스 키 발급받기**

AWS 콘솔에서 직접 액세스 키를 발급받는 방법입니다:

1. **AWS 콘솔 로그인** → [AWS 콘솔](https://aws.amazon.com/console/)
2. **IAM 서비스로 이동** → 상단 검색창에 "IAM" 입력
3. **사용자 선택** → 왼쪽 메뉴 "사용자(Users)" → 본인 사용자명 클릭
4. **액세스 키 생성** → "보안 자격 증명" 탭 → "액세스 키 만들기" 버튼
   - 사용 사례: "Command Line Interface (CLI)" 선택
5. **키 정보 저장** → 🚨 **중요:** `Secret Access Key`는 이 화면에서만 확인 가능!
   - "CSV 파일 다운로드" 또는 안전한 곳에 복사 저장

#### **3. AWS 자격 증명 설정**

```bash
# AWS CLI 설정
aws configure

# 입력 정보:
# AWS Access Key ID: [발급받은_액세스_키_ID]
# AWS Secret Access Key: [발급받은_시크릿_키]
# Default region name: ap-northeast-2
# Default output format: json
```

**설정 확인:**

```bash
aws sts get-caller-identity
```

#### **4. 스크립트 권한 설정 (1회 실행해보고 안되면 설정하기 - 그냥 될수도 있으니)**

**Windows (Git Bash에서 실행):**

```bash
chmod +x rds-connect.sh rds-disconnect.sh
```

**macOS/Linux:**

```bash
chmod +x rds-connect.sh rds-disconnect.sh
```

---

### **Part 2: 실전 사용법 (일상적인 작업)**

#### **🎯 방법 1: Make 명령어 사용 (권장)**

프로젝트 루트 디렉토리에서:

```bash
# RDS 연결 시작
make rds-connect

# RDS 연결 종료
make rds-disconnect
```

#### **방법 2: 스크립트 직접 실행**

**Windows (Git Bash):**

```bash
# scripts 폴더로 이동
cd scripts

# RDS 연결 시작 - ctrl + c 하면 꺼지긴합니다.
./rds-connect.sh

# RDS 연결 종료 (별도 터미널에서)
./rds-disconnect.sh
```

**macOS/Linux:**

```bash
# scripts 폴더로 이동
cd scripts

# RDS 연결 시작
./rds-connect.sh

# RDS 연결 종료 (별도 터미널에서)
./rds-disconnect.sh
```

#### **DB 클라이언트 접속 정보**

`✅ SSM 터널이 생성되었습니다...` 메시지 확인 후:

- **Host:** `localhost`
- **Port:** `54320`
- **Database:** `[실제 DB 이름]`
- **Username/Password:** 기존 RDS 계정 정보 (문의 바람 혹은 ssm parameter store 에서 조회 가능)

#### **연결 종료 방법**

1. **자동 종료 (권장):** `rds-connect.sh` 실행 중인 터미널에서 `Ctrl+C`
2. **수동 종료:** `make rds-disconnect` 또는 `./rds-disconnect.sh` 실행

---

### **🔧 문제 해결 (Troubleshooting)**

#### **"명령을 찾을 수 없음" 오류**

```bash
# 설치 확인
aws --version
session-manager-plugin --version

# PATH 확인 (Windows)
where aws

# PATH 확인 (macOS/Linux)
which aws
```

#### **"권한 거부" 오류**

```bash
# AWS 설정 확인
aws sts get-caller-identity
aws configure list
```

**혹시 안 된다면 - AWS 프로필 설정 확인:**

먼저 현재 사용 중인 프로필이 올바른지 확인해주세요:

```bash
# 현재 활성 프로필 확인
aws configure list

# 특정 프로필로 테스트
aws sts get-caller-identity --profile [프로필이름]
```

**일회성 프로필 설정 (터미널 세션 동안만 유효):**

**Windows (Git Bash):**

```bash
export AWS_PROFILE=프로필이름
# 예: export AWS_PROFILE=whatslab
```

**macOS/Linux:**

```bash
export AWS_PROFILE=프로필이름
# 예: export AWS_PROFILE=whatslab
```

**Windows (PowerShell) - 참고용:**

```powershell
$env:AWS_PROFILE = "프로필이름"
# 예: $env:AWS_PROFILE = "whatslab"
```

설정 후 다시 연결을 시도해보세요:

```bash
# 프로필 설정 확인
echo $AWS_PROFILE

# RDS 연결 재시도
make rds-connect
```

#### **"SSM 세션 시작 실패" 오류**

- EC2 인스턴스의 SSM Agent 상태 확인
- IAM 사용자의 EC2/SSM 권한 확인
- 점프 호스트 EC2의 IAM 역할에 `AmazonSSMManagedInstanceCore` 정책 연결 확인

#### **DB 접속은 되지만 쿼리 실행 오류**

- 데이터베이스 사용자 권한 문제입니다
- DBA에게 테이블 접근 권한 확인 요청

---

### **📋 현재 설정 요약**

- **로컬 포트:** `54320`
- **지원 플랫폼:** Windows (Git Bash), macOS, Linux
- **필수 도구:** AWS CLI, SSM Session Manager Plugin
- **편의 기능:** Make 명령어 지원

**⚠️ 스크립트 내의 AWS 리소스 정보는 보안상 중요하므로 외부 공유 금지!**

---

### **💡 팁**

- **Windows 사용자:** PowerShell 대신 Git Bash 사용 권장
- **Make 명령어:** 프로젝트 루트에서 `make rds-connect`가 가장 편리함
- **보안:** 정기적인 AWS 액세스 키 교체 권장
