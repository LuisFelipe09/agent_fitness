from fastapi import APIRouter
from src.interfaces.api.routers import (
    auth,
    users,
    plans,
    admin,
    trainer,
    nutritionist,
    versions,
    comments,
    notifications
)

router = APIRouter()

router.include_router(auth.router, tags=["Auth"])
router.include_router(users.router, tags=["Users"])
router.include_router(plans.router, tags=["Plans"])
router.include_router(admin.router, tags=["Admin"])
router.include_router(trainer.router, tags=["Trainer"])
router.include_router(nutritionist.router, tags=["Nutritionist"])
router.include_router(versions.router, tags=["Versions"])
router.include_router(comments.router, tags=["Comments"])
router.include_router(notifications.router, tags=["Notifications"])
