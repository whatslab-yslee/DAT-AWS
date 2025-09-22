# DAT Infrastructure - Terraform

이 프로젝트는 DAT 애플리케이션을 위한 AWS 인프라를 Terraform으로 관리합니다.

## 구조

```
terraform/
├── main.tf                    # 메인 구성 파일
├── variables.tf               # 변수 정의
├── outputs.tf                 # 출력값 정의
├── terraform.tfvars.example   # 변수 예제 파일
├── version.tf                 # Terraform 버전 요구사항
└── modules/                   # Terraformer로 생성된 모듈들
    ├── vpc/                   # VPC 및 Internet Gateway
    ├── subnet/                # 서브넷 구성
    ├── alb/                   # Application Load Balancer
    ├── route_table/           # 라우트 테이블
    ├── ec2_instance/          # EC2 인스턴스
    └── s3/                    # S3 버킷
```

## 주요 구성 요소

### 네트워킹
- **DAT VPC**: 10.0.0.0/16 CIDR 블록
- **Public Subnets**: 10.0.0.0/24, 10.0.1.0/24
- **Private Subnets**: 10.0.10.0/24, 10.0.11.0/24
- **Internet Gateway**: DAT VPC용

### 로드 밸런서
- **Application Load Balancer**: HTTP/HTTPS 트래픽 처리
- **Target Group**: ECS 서비스용
- **Security Group**: HTTP(80), HTTPS(443) 허용

### EC2 인스턴스
- **Jump Host**: SSM을 통한 접근용 (Private Subnet)
- **NAT Instance**: Private Subnet의 아웃바운드 트래픽용

### 스토리지
- **S3 Bucket**: 애플리케이션 데이터 저장용

## 사용법

### 1. 변수 파일 설정

```bash
cp terraform.tfvars.example terraform.tfvars
```

`terraform.tfvars` 파일을 편집하여 필요한 값들을 설정합니다:

```hcl
aws_region = "ap-northeast-2"
environment = "dev"
instance_type = "t2.micro"
certificate_arn = "arn:aws:acm:..."  # SSL 인증서가 있는 경우
```

### 2. Terraform 초기화

```bash
terraform init
```

### 3. 계획 확인

```bash
terraform plan
```

### 4. 인프라 배포

```bash
terraform apply
```

### 5. 다른 리전에 배포

다른 리전에 배포하려면 `terraform.tfvars` 파일에서 `aws_region`을 변경하고:

```bash
terraform apply
```

## 출력값

배포 완료 후 다음 정보들을 확인할 수 있습니다:

- `alb_dns_name`: ALB DNS 이름
- `dat_vpc_id`: DAT VPC ID
- `jump_host_private_ip`: Jump Host Private IP
- `s3_bucket_name`: S3 버킷 이름

## 보안 고려사항

1. **CIDR 블록 제한**: `allowed_cidr_blocks`를 필요한 IP 범위로 제한
2. **SSL 인증서**: HTTPS를 사용하려면 `certificate_arn` 설정
3. **IAM 권한**: 최소 권한 원칙 적용
4. **보안 그룹**: 필요한 포트만 열기

## 모듈별 설명

### VPC 모듈
- DAT 전용 VPC 생성
- Internet Gateway 생성
- DNS 설정

### Subnet 모듈
- Public/Private 서브넷 생성
- 가용 영역별 분산 배치

### ALB 모듈
- Application Load Balancer 생성
- Target Group 생성
- HTTP/HTTPS 리스너 설정

### EC2 모듈
- Jump Host (SSM 접근용)
- NAT Instance (아웃바운드 트래픽용)
- 보안 그룹 설정

### S3 모듈
- 데이터 저장용 버킷
- 버전 관리 및 암호화 설정

## 문제 해결

### 일반적인 문제들

1. **AMI ID 오류**: 리전별로 AMI ID가 다를 수 있습니다
2. **권한 오류**: IAM 사용자/역할에 필요한 권한이 있는지 확인
3. **리소스 제한**: AWS 계정의 리소스 제한 확인

### 로그 확인

```bash
terraform logs
```

## 정리

인프라를 삭제하려면:

```bash
terraform destroy
```

⚠️ **주의**: 이 명령은 모든 리소스를 삭제합니다. 중요한 데이터는 백업을 확인하세요.
