#!/bin/bash
set -euo pipefail

# Determine script directory consistently
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="${SCRIPT_DIR}/ssm_session.pid"

# --- ⚙️ 설정 영역 (connect 스크립트와 동일해야 함) ---
INSTANCE_ID="i-0338c7857fe633bc4"
# ----------------------------------------------------

if [ ! -f "$PID_FILE" ]; then
    echo "ℹ️  실행 중인 SSM 세션이 없는 것 같습니다. 점프 호스트를 강제로 중지합니다."
else
    echo "▶ 실행 중인 SSM 터널(PID: $(cat $PID_FILE))을 종료합니다..."
    kill $(cat $PID_FILE)
    rm $PID_FILE
fi


if [ -z "$INSTANCE_ID" ] || [ "$INSTANCE_ID" == "None" ]; then
    echo "⚠️  점프 호스트를 찾을 수 없어 중지시키지 못했습니다. AWS 콘솔을 확인해주세요."
    exit 1
fi

echo "▶ 비용 절감을 위해 점프 호스트 EC2(ID: $INSTANCE_ID)를 중지합니다."
aws ec2 stop-instances --instance-ids $INSTANCE_ID > /dev/null
echo "✅ 모든 연결이 안전하게 종료되었습니다."