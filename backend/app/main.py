# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.routers import auth_router, cases_router, images_router, symptoms_router  # ← ADD symptoms_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="StellarX API",
    version="1.0.0",
    description="AI-Powered Point-of-Care System for Tinea Diagnosis"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(cases_router)
app.include_router(images_router)
app.include_router(symptoms_router)  # ← This line was already there


@app.get("/")
def root():
    return {"message": "StellarX API is running"}


@app.get("/health")
def health():
    return {"status": "healthy", "service": "StellarX API"}