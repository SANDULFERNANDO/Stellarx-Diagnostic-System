from fastapi import FastAPI
from app.database import Base, engine
from app.routers import auth_router, cases_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="StellarX API", version="1.0.0")

app.include_router(auth_router)
app.include_router(cases_router)

@app.get("/")
def root():
    return {"message": "StellarX API is running"}

@app.get("/health")
def health():
    return {"status": "healthy"}