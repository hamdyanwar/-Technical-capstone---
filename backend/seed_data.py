from sqlalchemy.orm import Session
import models, database
from datetime import datetime, timedelta

def seed():
    db = next(database.get_db())
    
    # 1. Clear existing data
    db.query(models.Notification).delete()
    db.query(models.Telemetry).delete()
    db.query(models.MaintenanceLog).delete()
    db.query(models.Device).delete()
    db.query(models.Technician).delete()
    db.commit()

    # 2. Seed Technicians
    techs = [
        models.Technician(name="Ahmed Mansour", location="Cairo, Nasr City", price_per_hour="200 EGP/hr", specialty="Medical Imaging", rating=4.9),
        models.Technician(name="Sarah Williams", location="Maadi", price_per_hour="350 EGP/hr", specialty="Anesthesia Tech", rating=4.8),
        models.Technician(name="Med-Guard OnCall", location="Remote", price_per_hour="Free", specialty="Diagnostics", rating=5.0)
    ]
    db.add_all(techs)
    db.commit()

    # 3. Seed Initial Devices
    devices = [
        models.Device(name="Anesthesia Intel-G7", type="Anesthesia", location="Room 102", status="Active"),
        models.Device(name="Michael-Vent-ICU2", type="Ventilator", location="ICU-2", status="Active")
    ]
    db.add_all(devices)
    db.commit()

    # 4. Seed Telemetry (Normal)
    for dev in devices:
        for i in range(25):
            tel = models.Telemetry(
                device_id=dev.id,
                pressure=32.0 + (i * 0.1), # Slight growth simulation
                flow_rate=50.0,
                gas_level=95.0 - (i * 0.5),
                battery_level=100.0,
                timestamp=datetime.utcnow() - timedelta(days=(25-i))
            )
            db.add(tel)
    db.commit()

    print("Database seeded successfully!")

if __name__ == "__main__":
    seed()
