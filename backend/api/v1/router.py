from fastapi import APIRouter

from .documents import router as documents_router
from .chat import router as chat_router
from .kiro import router as kiro_router
from .invoices import router as invoices_router
from .agent import router as agent_router

router = APIRouter()

# Include all sub-routers
router.include_router(
    documents_router,
    prefix="/documents",
    tags=["Documents"]
)

router.include_router(
    chat_router,
    prefix="/chat",
    tags=["AI Chat History"]
)

router.include_router(
    kiro_router,
    prefix="/kiro",
    tags=["Kiro IDE Logs"]
)

router.include_router(
    invoices_router,
    prefix="/invoices",
    tags=["Car Maintenance"]
)

router.include_router(
    agent_router,
    prefix="/agent",
    tags=["Agent"]
)