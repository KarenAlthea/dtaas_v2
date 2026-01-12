from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.routers.api import api_router
from app.routers.ui import ui_router

app = FastAPI(title="Digital Twin as a Service", version="0.2")

# UI routes (hidden from /docs)
app.include_router(ui_router)

# API routes (visible in /docs)
app.include_router(api_router, prefix="/api", tags=["API"])


@app.get("/", include_in_schema=False)
def root():
    # homepage -> UI Builder
    return RedirectResponse(url="/ui/builder")
