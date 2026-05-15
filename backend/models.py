from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Float
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Device(Base):
    __tablename__ = "devices"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    type = Column(String)
    location = Column(String)
    status = Column(String, default="Active")
    room_id = Column(Integer, ForeignKey("hospital_rooms.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    telemetry = relationship("Telemetry", back_populates="device")
    maintenance_logs = relationship("MaintenanceLog", back_populates="device")
    room = relationship("HospitalRoom", back_populates="devices")
    notifications = relationship("Notification", back_populates="device")

class Telemetry(Base):
    __tablename__ = "telemetry"
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    pressure = Column(Float)
    flow_rate = Column(Float)
    gas_level = Column(Float)
    soda_lime = Column(Float, default=100.0)
    battery_level = Column(Float)
    
    device = relationship("Device", back_populates="telemetry")

class MaintenanceLog(Base):
    __tablename__ = "maintenance_logs"
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"))
    technician_id = Column(Integer, ForeignKey("technicians.id"))
    description = Column(String)
    date = Column(DateTime, default=datetime.utcnow)
    
    device = relationship("Device", back_populates="maintenance_logs")
    technician = relationship("Technician", back_populates="maintenance_logs")

class Technician(Base):
    __tablename__ = "technicians"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    location = Column(String)
    price_per_hour = Column(String)
    specialty = Column(String)
    rating = Column(Float, default=5.0)
    
    maintenance_logs = relationship("MaintenanceLog", back_populates="technician")

class HospitalRoom(Base):
    __tablename__ = "hospital_rooms"
    id = Column(Integer, primary_key=True, index=True)
    room_number = Column(String, unique=True, index=True)
    department = Column(String)
    
    devices = relationship("Device", back_populates="room")

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"))
    receiver_type = Column(String)  # "Doctor" or "Technician"
    message = Column(String)
    is_read = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    device = relationship("Device", back_populates="notifications")

