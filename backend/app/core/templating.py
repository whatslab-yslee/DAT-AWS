from fastapi.templating import Jinja2Templates


# backend/main.py 에서 uvicorn을 실행하므로, main.py 파일의 위치를 기준으로 경로 설정
templates = Jinja2Templates(directory="/app/backend/templates")
