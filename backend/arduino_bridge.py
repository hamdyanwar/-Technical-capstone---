"""
=============================================================================
  MED-GUARD — جسر الهاردوير الموحد (Hardware Bridge - Unified)
  الاتجاه: ثنائي الاتجاه ← → (Software ↔ Arduino)
=============================================================================
  كيف يعمل:
    1. يقرأ قيم الأجهزة (gas_level, pressure, soda_lime) من API الباكند
    2. يُرسل أوامر الحالة للأردوينو عبر Serial بروتوكول موحد:
         CMD:RED_GAS      → خطر غاز (LED أحمر + بازر حاد)
         CMD:RED_PRESSURE → خطر ضغط (LED أحمر + بازر متقطع)
         CMD:GREEN        → آمن تماماً (LED أخضر)
    3. يستقبل قراءات من الأردوينو ويحدّث السوفتوير بها

  المتطلبات:
    pip install pyserial requests

  التشغيل:
    python arduino_bridge.py
    - أو -
    انقر مرتين على start_arduino_bridge.bat
=============================================================================
"""

import subprocess, sys

# تثبيت تلقائي للمكتبات إذا لم تكن موجودة
def _install(pkg):
    subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "--quiet"])

try:
    import serial
    import serial.tools.list_ports
except ImportError:
    print("[SETUP] جاري تثبيت pyserial...")
    _install("pyserial")
    import serial
    import serial.tools.list_ports

try:
    import requests
except ImportError:
    print("[SETUP] جاري تثبيت requests...")
    _install("requests")
    import requests

import time
import os
from datetime import datetime

# ─────────────────────────────────────────────
#   إعدادات النظام / System Configuration
# ─────────────────────────────────────────────

API_BASE_URL   = "http://localhost:8000"
BAUD_RATE      = 9600
POLL_INTERVAL  = 2.0      # ثواني بين كل دورة
RECONNECT_WAIT = 5.0      # ثواني قبل إعادة المحاولة عند انقطاع الاتصال

# حدود التنبيه — يجب أن تتطابق مع arduino_code.ino
GAS_THRESHOLD      = 45.0   # % → تنبيه إذا انخفض عن هذا الحد
PRESSURE_THRESHOLD = 45.0   # cmH₂O → تنبيه إذا انخفض عن هذا الحد

# ─────────────────────────────────────────────
#   الكشف التلقائي عن الأردوينو
# ─────────────────────────────────────────────

def find_arduino_port():
    """يبحث تلقائياً عن منفذ الأردوينو ثم يطلب من المستخدم إذا لم يجد"""
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        return None

    # أولاً: بحث ذكي بالوصف
    keywords = ["arduino", "ch340", "ch341", "ftdi", "usb serial", "usb-serial"]
    for port in ports:
        desc = port.description.lower()
        if any(kw in desc for kw in keywords):
            print(f"[Auto] تم اكتشاف الأردوينو تلقائياً على: {port.device} ({port.description})")
            return port.device

    # ثانياً: عرض قائمة للمستخدم للاختيار
    print("\n🔌 المنافذ المتاحة (Available Serial Ports):")
    print("-" * 50)
    for i, port in enumerate(ports):
        print(f"  [{i}] {port.device:<10} — {port.description}")
    print("-" * 50)

    try:
        choice = input("\nاختر رقم المنفذ (أو اضغط Enter للإلغاء): ").strip()
        if choice == "":
            return None
        idx = int(choice)
        if 0 <= idx < len(ports):
            return ports[idx].device
    except (ValueError, IndexError):
        pass

    return None


# ─────────────────────────────────────────────
#   التواصل مع الـ Backend API
# ─────────────────────────────────────────────

def check_backend() -> bool:
    """التحقق من أن الـ Backend يعمل"""
    try:
        r = requests.get(API_BASE_URL, timeout=3)
        return r.status_code == 200
    except:
        return False


def get_all_devices():
    """جلب كل الأجهزة مع حالتها الصحية من الـ API"""
    try:
        r = requests.get(f"{API_BASE_URL}/devices/", timeout=3)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        print(f"[!] فشل الاتصال بالـ Backend: {e}")
    return []


def update_software_with_hardware_data(device_id: int, gas_val: int, sound_val: int):
    """
    تحديث السوفتوير بقراءات الهاردوير
    gas_val / sound_val: قراءات خام من analogRead (0-1023)
    يتم تحويلها لنسبة مئوية (0-100)
    """
    # تحويل قراءة analog (0-1023) لنسبة مئوية
    gas_pct   = round((gas_val   / 1023.0) * 100.0, 2)
    sound_pct = round((sound_val / 1023.0) * 100.0, 2)

    payload = {
        "pressure":      round(sound_pct, 2),
        "flow_rate":     5.0,
        "gas_level":     round(gas_pct, 2),
        "soda_lime":     round(sound_pct, 2),
        "battery_level": 95.0
    }

    try:
        r = requests.post(
            f"{API_BASE_URL}/devices/{device_id}/telemetry",
            json=payload,
            timeout=3
        )
        if r.status_code == 200:
            ts = datetime.now().strftime("%H:%M:%S")
            print(f"  [{ts}] ⬆ هاردوير→سوفتوير | غاز: {gas_pct:.1f}% | صوت/ضغط: {sound_pct:.1f}%")
    except Exception as e:
        pass  # تجاهل أخطاء الشبكة اللحظية


# ─────────────────────────────────────────────
#   منطق التحكم في الهاردوير
# ─────────────────────────────────────────────

# حالة آخر أمر أُرسل (لتجنب إرسال نفس الأمر مراراً)
_last_sent_cmd = None


def determine_alarm(devices) -> str:
    """
    يحدد أمر الحالة بناءً على بيانات الأجهزة
    يعيد: 'CMD:RED_GAS', 'CMD:RED_PRESSURE', 'CMD:GREEN', أو None
    """
    alarm_gas      = False
    alarm_pressure = False
    has_devices    = False

    for device in devices:
        health = device.get("health", {})
        if not health:
            continue

        has_devices = True
        gas_level  = health.get("gas_level")
        soda_lime  = health.get("soda_lime")
        is_healthy = health.get("is_healthy", True)

        # فحص مستوى الغاز
        if gas_level is not None and gas_level < GAS_THRESHOLD:
            alarm_gas = True

        # فحص الضغط / سودا لايم
        if soda_lime is not None and soda_lime < PRESSURE_THRESHOLD:
            alarm_pressure = True

        # إذا كان النظام غير سليم بشكل عام
        if not is_healthy:
            alarm_pressure = True

    if alarm_gas:
        return "CMD:RED_GAS"
    elif alarm_pressure:
        return "CMD:RED_PRESSURE"
    elif has_devices:
        return "CMD:GREEN"

    return None


def send_command_if_changed(ser: serial.Serial, cmd: str):
    """يرسل الأمر للأردوينو فقط إذا تغيّر عن الحالة السابقة"""
    global _last_sent_cmd

    if cmd != _last_sent_cmd:
        try:
            ser.write((cmd + "\n").encode("utf-8"))
            _last_sent_cmd = cmd

            ts = datetime.now().strftime("%H:%M:%S")
            icon = "🔴" if "RED" in cmd else "🟢"
            label = {
                "CMD:RED_GAS":      "خطر غاز → LED أحمر + بازر حاد",
                "CMD:RED_PRESSURE": "خطر ضغط → LED أحمر + بازر متقطع",
                "CMD:GREEN":        "آمن تماماً → LED أخضر"
            }.get(cmd, cmd)

            print(f"  [{ts}] {icon} ⬇ سوفتوير→أردوينو | {label}")
        except serial.SerialException as e:
            raise  # أعد الخطأ للمستوى الأعلى


# ─────────────────────────────────────────────
#   معالجة البيانات القادمة من الأردوينو
# ─────────────────────────────────────────────

def process_arduino_data(line: str, devices: list):
    """
    يعالج سطراً قادماً من الأردوينو
    البروتوكول: DATA,Gas:<val>,Sound:<val>
    """
    if not line.startswith("DATA,"):
        return

    try:
        parts = line.split(",")
        # parts = ['DATA', 'Gas:512', 'Sound:300']
        if len(parts) < 3:
            return

        gas_part   = parts[1].split(":")
        sound_part = parts[2].split(":")

        if len(gas_part) < 2 or len(sound_part) < 2:
            return

        gas_raw   = int(gas_part[1].strip())
        sound_raw = int(sound_part[1].strip())

        # تحديث السوفتوير بقراءات الهاردوير (الجهاز الأول كافتراضي)
        if devices:
            device_id = devices[0].get("id", 1)
            update_software_with_hardware_data(device_id, gas_raw, sound_raw)

    except (ValueError, IndexError) as e:
        pass  # تجاهل أسطر تالفة


# ─────────────────────────────────────────────
#   البرنامج الرئيسي
# ─────────────────────────────────────────────

def print_banner():
    os.system("cls" if os.name == "nt" else "clear")
    print("=" * 60)
    print("  🏥  MED-GUARD — Hardware Bridge (Unified)")
    print("  الجسر البرمجي الموحد بين السوفتوير والأردوينو")
    print("=" * 60)
    print(f"  Backend   : {API_BASE_URL}")
    print(f"  Baud Rate : {BAUD_RATE}")
    print(f"  حد الغاز  : < {GAS_THRESHOLD}%")
    print(f"  حد الضغط  : < {PRESSURE_THRESHOLD}%")
    print("=" * 60)
    print()


def connect_to_arduino():
    """يحاول الاتصال بالأردوينو ويُعيد كائن Serial أو None"""
    port = find_arduino_port()
    if not port:
        return None, None

    try:
        ser = serial.Serial(port, BAUD_RATE, timeout=1)
        time.sleep(2)  # انتظار إعادة تشغيل الأردوينو بعد فتح Serial
        print(f"✅ متصل بالأردوينو على: {port} @ {BAUD_RATE} baud\n")
        return ser, port
    except serial.SerialException as e:
        print(f"❌ فشل فتح المنفذ {port}: {e}")
        return None, None


def main():
    print_banner()

    # 1. التحقق من الـ Backend
    print("🔍 التحقق من الـ Backend...")
    retries = 0
    while not check_backend():
        retries += 1
        print(f"  [⏳ {retries}] الـ Backend غير متاح، جاري الانتظار... (شغّل start_backend.bat أولاً)")
        time.sleep(3)
        if retries >= 10:
            print("❌ تعذّر الاتصال بالـ Backend بعد عدة محاولات. تأكد من تشغيله.")
            input("\nاضغط Enter للخروج...")
            sys.exit(1)
    print(f"✅ Backend متصل على {API_BASE_URL}\n")

    # 2. الكشف عن الأردوينو
    print("🔍 البحث عن الأردوينو...")
    ser, port = connect_to_arduino()
    if not ser:
        print("❌ لم يُعثر على الأردوينو! تأكد من توصيل كبل USB.")
        input("\nاضغط Enter للخروج...")
        sys.exit(1)

    print("🚀 الجسر يعمل الآن... (اضغط Ctrl+C للإيقاف)")
    print("=" * 60)
    print()

    last_poll_time  = 0.0
    last_hw_update  = 0.0
    devices         = []

    try:
        while True:
            current_time = time.time()

            # ══════════════════════════════════════════════
            # قراءة البيانات القادمة من الأردوينو (هاردوير → سوفتوير)
            # ══════════════════════════════════════════════
            try:
                while ser.in_waiting > 0:
                    raw = ser.readline()
                    try:
                        line = raw.decode("utf-8").strip()
                        if line and line.startswith("DATA,"):
                            # فقط نحدّث السوفتوير كل ثانيتين لتجنب ضغط الشبكة
                            if current_time - last_hw_update > 2.0:
                                process_arduino_data(line, devices)
                                last_hw_update = current_time
                    except UnicodeDecodeError:
                        pass

            except serial.SerialException as e:
                print(f"\n⚠️  انقطع اتصال Serial: {e}")
                print(f"   جاري إعادة المحاولة خلال {RECONNECT_WAIT} ثوانٍ...")
                ser = None
                _last_sent_cmd = None
                time.sleep(RECONNECT_WAIT)
                ser, port = connect_to_arduino()
                if not ser:
                    print("❌ فشلت إعادة الاتصال. أعد توصيل الأردوينو وشغّل البرنامج مجدداً.")
                    break
                continue

            # ══════════════════════════════════════════════
            # استعلام الـ Backend وإرسال الأوامر (سوفتوير → أردوينو)
            # ══════════════════════════════════════════════
            if current_time - last_poll_time >= POLL_INTERVAL:
                devices = get_all_devices()

                if devices:
                    cmd = determine_alarm(devices)
                    if cmd and ser:
                        send_command_if_changed(ser, cmd)
                else:
                    # لا يوجد أجهزة في السوفتوير
                    print(f"  [{datetime.now().strftime('%H:%M:%S')}] ℹ️  لا توجد أجهزة مسجّلة في السوفتوير")

                last_poll_time = current_time

            time.sleep(0.05)  # دورة سريعة لاستقبال بيانات الهاردوير

    except KeyboardInterrupt:
        print("\n\n🛑 تم إيقاف الجسر بواسطة المستخدم")

    finally:
        if ser and ser.is_open:
            # إرسال أمر أخضر قبل الإغلاق
            try:
                ser.write(b"CMD:GREEN\n")
                time.sleep(0.2)
            except:
                pass
            ser.close()
            print("🔌 تم إغلاق اتصال Serial بأمان")
        print("👋 وداعاً!")


if __name__ == "__main__":
    main()
