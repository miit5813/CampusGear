from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth, bookings, categories, equipment, health

app = FastAPI(
    title="CampusGear API",
    description="API сервиса аренды кампусного оборудования университета",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(equipment.router)
app.include_router(bookings.router)