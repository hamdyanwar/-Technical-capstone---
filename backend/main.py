"""
=============================================================================
  MED-GUARD CORE SYSTEMS — BACKEND ENTRY POINT
  SYSTEM STATUS: SECURE | ONLINE
  AUTHORITY: ENGINEER MICHAEL (LEAD SYSTEMS ARCHITECT)
=============================================================================
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import uvicorn
import models
from database import engine

# Load environment variables
load_dotenv()

from routers import devices, technicians, notifications

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart Medical Device Monitor")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.staticfiles import StaticFiles

app.include_router(devices.router)
app.include_router(technicians.router)
app.include_router(notifications.router)

# Mount frontend static files
app.mount("/frontend", StaticFiles(directory="../frontend"), name="frontend")



@app.get("/")
def read_root():
    return {
        "status": "آمن",
        "system": "طبقة ذكاء مد-جارد",
        "authorized_engineer": "مايكل",
        "message": "مستويات البروتوكول: مستقرة. الأنظمة متصلة بالإنترنت."
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
