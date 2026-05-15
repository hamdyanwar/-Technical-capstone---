from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class TelemetryBase(BaseModel):
    pressure: float
    flow_rate: float
    gas_level: float
    soda_lime: float = 100.0
    battery_level: float

class TelemetryCreate(TelemetryBase):
    pass

class Telemetry(TelemetryBase):
    id: int
    device_id: int
    timestamp: datetime

    class Config:
        orm_mode = True

class MaintenanceLogBase(BaseModel):
    device_id: int
    technician_id: int
    description: str

class MaintenanceLogCreate(MaintenanceLogBase):
    pass

class MaintenanceLog(MaintenanceLogBase):
    id: int
    date: datetime

    class Config:
        orm_mode = True

class TechnicianBase(BaseModel):
    name: str
    location: str
    price_per_hour: str
    specialty: str
    rating: float = 5.0

class TechnicianCreate(TechnicianBase):
    pass

class Technician(TechnicianBase):
    id: int

    class Config:
        orm_mode = True

class HospitalRoomBase(BaseModel):
    room_number: str
    department: str

class HospitalRoomCreate(HospitalRoomBase):
    pass

class HospitalRoom(HospitalRoomBase):
    id: int

    class Config:
        orm_mode = True

class NotificationBase(BaseModel):
    device_id: int
    receiver_type: str
    message: str
    is_read: bool = False

class NotificationCreate(NotificationBase):
    pass

class Notification(NotificationBase):
    id: int
    timestamp: datetime

    class Config:
        orm_mode = True

class DeviceBase(BaseModel):
    name: str
    type: str
    location: str
    status: Optional[str] = "Active"
    room_id: Optional[int] = None

class DeviceCreate(DeviceBase):
    pass

class HealthAnalysis(BaseModel):
    health_score: int
    status: str
    is_healthy: bool
    malfunction_probability: float
    issues: List[str]
    insights: List[str]
    prediction: str
    gas_level: Optional[float] = None
    pressure: Optional[float] = None

class Device(DeviceBase):
    id: int
    created_at: datetime
    telemetry: List[Telemetry] = []
    notifications: List[Notification] = []
    health: Optional[HealthAnalysis] = None

    class Config:
        orm_mode = True

class ChatMessage(BaseModel):
    role: str # 'user' or 'model'
    parts: List[str]

class ChatMessageSimple(BaseModel):
    text: str

class ChatRequest(BaseModel):
    message: Optional[str] = None
    text: Optional[str] = None # Added for user's specific request
    device_id: Optional[int] = None
    history: Optional[List[ChatMessage]] = []
