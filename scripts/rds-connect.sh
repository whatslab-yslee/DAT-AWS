#!/bin/bash
set -euo pipefail

# Determine script directory so that auxiliary files are stored consistently
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="${SCRIPT_DIR}/ssm_session.pid"

# --- ⚙️ 설정 영역 (필요시 수정) ---
# 스크립트가 리소스를 찾기 위해 사용할 태그 정보입니다.
JUMP_HOST_TAG_NAME="dat-ssm-jump-host"
RDS_ENDPOINT="whatslab-dat-db.cvwa6qk2eyzm.ap-northeast-2.rds.amazonaws.com"
RDS_PORT="5432"
INSTANCE_ID="i-0338c7857fe633bc4"


# 내 PC에서 DB 클라이언트가 접속할 포트 번호입니다.
LOCAL_PORT="54320"
# ------------------------------------

echo ""
echo "▶ 점프 호스트 EC2 인스턴스를 시작합니다..."
INSTANCE_STATE=$(aws ec2 describe-instances \
    --instance-ids "$INSTANCE_ID" \
    --query "Reservations[0].Instances[0].State.Name" --output text)

if [ "$INSTANCE_STATE" == "stopped" ]; then
    aws ec2 start-instances --instance-ids $INSTANCE_ID > /dev/null
    echo "▶ 인스턴스가 실행 상태가 될 때까지 기다립니다..."
    aws ec2 wait instance-running --instance-ids $INSTANCE_ID
else
    echo "ℹ️  점프 호스트가 이미 실행 중입니다. (state: $INSTANCE_STATE)"
fi

echo ""
echo "✅ SSM 터널이 생성되었습니다. 이제 DB 클라이언트에서 접속하세요."
echo "   - Host: localhost"
echo "   - Port: $LOCAL_PORT"
echo ""

# 세션 및 인스턴스 자동 정리를 위한 함수
cleanup() {
    echo -e "\n🛑 중단 신호 감지 또는 세션 종료. 점프 호스트를 중지합니다..."
    # SSM 세션 종료
    if [ -f "$PID_FILE" ]; then
        if ps -p $(cat "$PID_FILE") > /dev/null 2>&1; then
            kill $(cat "$PID_FILE") 2>/dev/null || true
        fi
        rm -f "$PID_FILE"
    fi

    # EC2 인스턴스 중지
    if [ -n "${INSTANCE_ID:-}" ]; then
        aws ec2 stop-instances --instance-ids "$INSTANCE_ID" > /dev/null || true
        echo "✅ 점프 호스트(ID: $INSTANCE_ID)가 중지되었습니다."
    fi
}

# INT(CTRL+C) 또는 TERM 신호 수신 시 cleanup 실행
trap cleanup INT TERM

# 백그라운드로 SSM 세션을 시작하고, 프로세스 ID를 파일에 저장
aws ssm start-session \
    --target $INSTANCE_ID \
    --document-name AWS-StartPortForwardingSessionToRemoteHost \
    --parameters "host=$RDS_ENDPOINT,portNumber=$RDS_PORT,localPortNumber=$LOCAL_PORT" &

# 백그라운드 PID 저장 후 세션 종료까지 대기
SSM_PID=$!
echo $SSM_PID > "$PID_FILE"

echo "ℹ️  연결을 종료하려면 터미널에서 Ctrl+C 를 누르세요."

# SSM 세션이 끝날 때까지 대기
wait $SSM_PID

# 세션이 자연 종료된 경우 cleanup 호출
cleanup

# rds-disconnect.sh 를 별도 실행할 필요 없이 자동 정리됨