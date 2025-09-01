# 코드 스타일 관리
quality: set-style-dep check-quality
style: set-style-dep set-style

set-style-dep:
	uv pip install ruff==0.7.2

set-style:
	uvx ruff check --fix .
	uvx ruff format .

check-quality:
	uvx ruff check .
	uvx ruff format --check .

# 개발 및 배포 관련
.PHONY: dev build-prod start-prod revision-db upgrade-db downgrade-db install

dev:
	docker compose -f docker-compose.yml build
	docker compose -f docker-compose.yml up -d

dev-build:
	docker compose -f docker-compose.yml build

dev-up:
	docker compose -f docker-compose.yml up -d

dev-down:
	docker compose -f docker-compose.yml down


# S3 LocalStack 관련 유틸리티
.PHONY: localstack-up localstack-init localstack-test localstack-down

# LocalStack 서비스만 실행
localstack-up:
	docker compose up -d localstack
	@echo "LocalStack이 시작되었습니다. 상태 확인 중..."
	@sleep 3
	@curl -s http://localhost:4566/health | jq .

# S3 버킷 초기화 (파일 업로드)
localstack-init: localstack-up
	@echo "테스트 버킷을 초기화합니다..."
	aws --endpoint-url=http://localhost:4566 s3 mb s3://test-bucket
	@echo "테스트 파일을 업로드합니다..."
	echo "테스트 콘텐츠" > /tmp/test-file.txt
	aws --endpoint-url=http://localhost:4566 s3 cp /tmp/test-file.txt s3://test-bucket/test/test-file.txt
	@echo "버킷 내 파일 목록:"
	aws --endpoint-url=http://localhost:4566 s3 ls s3://test-bucket/test/ --recursive

# S3 버킷 내용 확인
localstack-test:
	@echo "버킷 목록 확인:"
	aws --endpoint-url=http://localhost:4566 s3 ls
	@echo "test-bucket 내 파일 목록:"
	aws --endpoint-url=http://localhost:4566 s3 ls s3://test-bucket/ --recursive

# LocalStack 종료 및 볼륨 정리
localstack-down:
	@echo "LocalStack 컨테이너를 종료합니다..."
	docker compose stop localstack
	docker compose rm -f localstack
	@echo "LocalStack 볼륨을 정리합니다..."
	rm -rf ./localstack-data

# 1) 새 마이그레이션 스크립트 생성
# 사용예: make revision msg="create user table"
revision-db:
	docker compose exec app bash -c "cd /app/backend && alembic revision --autogenerate -m \"$(msg)\""

# 2) DB에 최신 스크립트 적용 (upgrade head)
upgrade-db:
	docker compose exec app bash -c "cd /app/backend && alembic upgrade head"

# 3) DB를 한 단계 다운그레이드
downgrade-db:
	docker compose exec app bash -c "cd /app/backend && alembic downgrade -1"

# 4) DB 초기화 및 최신 스크립트 적용
reset-db:
	docker compose exec app bash -c "cd /app/backend && python3 migrations/reset_db.py"

# RDS 원격 접속 스크립트 실행
.PHONY: rds-connect rds-disconnect

rds-connect:
	bash scripts/rds-connect.sh

rds-disconnect:
	bash scripts/rds-disconnect.sh
