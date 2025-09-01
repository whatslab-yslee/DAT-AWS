from app.controllers import (
    auth_controller,
    diagnosis_record_controller,
    diagnosis_web_controller,
    diagnosis_ws_controller,
    mock_client_controller,
    patient_controller,
)
from app.utils import load_api_description_from_json
from fastapi import FastAPI


def create_app() -> FastAPI:
    VERSION = "1.1.1"
    app = FastAPI(
        title="Whatslab DAT API Server",
        version=VERSION,
        description=load_api_description_from_json(),
        root_path="/api",
    )

    app.include_router(auth_controller.router)
    app.include_router(patient_controller.router)
    app.include_router(diagnosis_web_controller.router)
    app.include_router(diagnosis_record_controller.router)
    app.include_router(diagnosis_ws_controller.router)
    app.include_router(mock_client_controller.router)

    @app.get("/")
    def version_check():
        return {"version": VERSION}

    return app


app = create_app()
