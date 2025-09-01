# import os

# import httpx


# ENV = os.environ.get("ENV", "production")

# if ENV.lower() == "local":
#     BASE_URL = "http://fastapi:8000"
# else:
#     BASE_URL = "http://localhost/api"


# # 동기용 클라이언트
# request = httpx.Client(base_url=BASE_URL)
