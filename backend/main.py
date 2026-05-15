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

app.include_router(devices.router)
app.include_router(technicians.router)
app.include_router(notifications.router)



@app.get("/")
def read_root():
    return {
        "status": "Secure",
        "system": "Med-Guard Intelligence Layer",
        "authorized_engineer": "Michael",
        "message": "Protocol levels: Stable. Systems are Online."
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
