import json
import os


def load_api_description_from_json() -> str:
    _BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    _JSON_DIR = os.path.join(_BASE_DIR, "docs", "websocket_api_docs.json")
    try:
        with open(_JSON_DIR, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("description", "API 문서를 불러오는 데 실패했습니다.")
    except (FileNotFoundError, json.JSONDecodeError):
        return "API 문서 파일을 찾을 수 없거나 파일 형식이 잘못되었습니다."
