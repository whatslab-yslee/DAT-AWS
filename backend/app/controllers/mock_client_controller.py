from app.core.templating import templates
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse


router = APIRouter(prefix="/test", tags=["test"])


@router.get("/mock-vr", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse(request=request, name="mock_vr_client.html", context={})
