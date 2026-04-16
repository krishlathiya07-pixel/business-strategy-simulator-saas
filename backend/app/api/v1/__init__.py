from fastapi import APIRouter
from backend.app.api.v1.endpoints import simulation, auth, user

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(user.router, prefix="/users", tags=["users"])
api_router.include_router(simulation.router, prefix="/simulation", tags=["simulation"])
