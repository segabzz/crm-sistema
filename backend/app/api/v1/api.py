from fastapi import APIRouter
from app.api.v1.endpoints import dishes, reviews, analytics, admin, orders

api_router = APIRouter()
api_router.include_router(dishes.router, prefix="/dishes", tags=["Platillos (Catálogo)"])
api_router.include_router(orders.router, prefix="/orders", tags=["Pedidos y QR (Mesero)"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["Reseñas"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analíticas y Ranking"])
api_router.include_router(admin.router, prefix="/admin", tags=["Administración"])
