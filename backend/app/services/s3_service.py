import logging
from typing import Any, BinaryIO, Dict, List, Optional

from app.configs.env_configs import settings
import boto3
from botocore.exceptions import ClientError


logger = logging.getLogger(__name__)


class S3Service:
    def __init__(self, bucket_name: str = None):
        # 버킷 이름을 파라미터로 받지 않으면 환경 변수에서 가져옴
        self.bucket_name = bucket_name or settings.S3_BUCKET_NAME
        self.region_name = settings.AWS_REGION

        # local 환경에서는 LocalStack 사용, 그 외(production)에는 실제 AWS S3 사용
        if settings.is_local:
            endpoint_url = settings.LOCALSTACK_ENDPOINT
            logger.info(f"로컬 환경에서 LocalStack S3를 사용합니다. 엔드포인트: {endpoint_url}")

            # LocalStack S3 클라이언트 생성
            self.s3_client = boto3.client(
                "s3",
                endpoint_url=endpoint_url,
                region_name=self.region_name,
                aws_access_key_id="test",  # LocalStack에서는 아무 값이나 사용 가능
                aws_secret_access_key="test",  # LocalStack에서는 아무 값이나 사용 가능
            )

            # 버킷이 존재하는지 확인하고 없으면 생성
            self._ensure_bucket_exists()
        else:
            # 프로덕션 환경에서는 실제 AWS S3 사용
            self.s3_client = boto3.client("s3", region_name=self.region_name)

    def _ensure_bucket_exists(self) -> None:
        """LocalStack에서 버킷이 존재하는지 확인하고 없으면 생성합니다."""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"버킷 '{self.bucket_name}'이 이미 존재합니다.")
        except ClientError:
            logger.info(f"버킷 '{self.bucket_name}'을 생성합니다.")
            try:
                self.s3_client.create_bucket(Bucket=self.bucket_name, CreateBucketConfiguration={"LocationConstraint": self.region_name})

                # CORS 설정 추가
                cors_configuration = {
                    "CORSRules": [
                        {
                            "AllowedHeaders": ["*"],
                            "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
                            "AllowedOrigins": ["*"],
                            "ExposeHeaders": ["ETag"],
                            "MaxAgeSeconds": 3000,
                        }
                    ]
                }
                self.s3_client.put_bucket_cors(Bucket=self.bucket_name, CORSConfiguration=cors_configuration)
                logger.info(f"버킷 '{self.bucket_name}'이 생성되었고 CORS 설정이 적용되었습니다.")
            except Exception as e:
                logger.error(f"버킷 생성 중 오류 발생: {e}")

    def generate_presigned_url(self, object_name: str, expiration: int = 3600) -> Optional[str]:
        """
        S3 객체에 대한 presigned URL을 생성합니다.

        Args:
            object_name (str): S3 객체 이름
            expiration (int): URL의 만료 시간(초), 기본값 1시간

        Returns:
            str: presigned URL 또는 에러 발생 시 None
        """
        try:
            response = self.s3_client.generate_presigned_url(
                "put_object", Params={"Bucket": self.bucket_name, "Key": object_name, "ContentType": "application/octet-stream"}, ExpiresIn=expiration
            )
            return response
        except ClientError as e:
            logger.error(f"Error generating presigned URL: {e}")
            return None

    def list_objects(self, prefix: str = "") -> List[Dict[str, Any]]:
        """
        S3 버킷 내 객체 목록을 조회합니다.

        Args:
            prefix (str): 객체 접두사(폴더)

        Returns:
            List[Dict]: 객체 목록
        """
        try:
            response = self.s3_client.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)

            if "Contents" in response:
                return [{"key": item["Key"], "size": item["Size"], "last_modified": item["LastModified"].isoformat()} for item in response["Contents"]]
            return []
        except ClientError as e:
            logger.error(f"Error listing S3 objects: {e}")
            return []

    def generate_download_url(self, object_name: str, expiration: int = 3600) -> Optional[str]:
        """
        S3 객체에 대한 다운로드용 presigned URL을 생성합니다.

        Args:
            object_name (str): S3 객체 이름
            expiration (int): URL의 만료 시간(초), 기본값 1시간

        Returns:
            str: presigned URL 또는 에러 발생 시 None
        """
        try:
            response = self.s3_client.generate_presigned_url("get_object", Params={"Bucket": self.bucket_name, "Key": object_name}, ExpiresIn=expiration)
            return response
        except ClientError as e:
            logger.error(f"Error generating download URL: {e}")
            return None

    def upload_file(self, file_path: str, file: BinaryIO) -> bool:
        """S3에 파일 업로드"""
        try:
            self.s3_client.upload_fileobj(file, self.bucket_name, file_path)
            return True
        except Exception as e:
            logger.error(f"Error uploading file to S3: {e}")
            return False

    def get_file_data(self, file_path: str) -> Optional[bytes]:
        """S3에서 파일 데이터 가져오기"""
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=file_path)
            return response["Body"].read()
        except ClientError as e:
            logger.error(f"Error retrieving file from S3: {e}")
            return None
