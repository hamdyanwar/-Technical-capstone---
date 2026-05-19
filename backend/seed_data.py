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
        models.Technician(name="م. أحمد منصور", location="القاهرة، مدينة نصر", price_per_hour="200 ج.م/ساعة", specialty="أشعة طبية", rating=4.9),
        models.Technician(name="م. سارة ويليامز", location="المعادي", price_per_hour="350 ج.م/ساعة", specialty="صيانة أجهزة تخدير", rating=4.8),
        models.Technician(name="فريق الدعم المناوب", location="عن بعد", price_per_hour="مجاني", specialty="تشخيص ذكي", rating=5.0)
    ]
    db.add_all(techs)
    db.commit()

    # 3. Seed Initial Devices
    devices = [
        models.Device(name="أداة التخدير الذكية G7", type="أجهزة تخدير", location="الغرفة 102", status="نشط"),
        models.Device(name="جهاز تنفس مايكل ICU2", type="جهاز تنفس صناعي", location="العناية المركزة 2", status="نشط")
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
