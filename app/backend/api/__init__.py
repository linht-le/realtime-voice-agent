from app.backend.api.prompts import router as prompts_router
from app.backend.api.settings import router as settings_router
from app.backend.api.tools import router as tools_router
from app.backend.api.websocket import router as websocket_router

routers = [
    websocket_router,
    settings_router,
    prompts_router,
    tools_router,
]
