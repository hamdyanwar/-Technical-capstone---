"""
=============================================================================
  MED-GUARD INTELLIGENCE LAYER — AI SERVICE UNIT
  CENTRAL CLINICAL ENGINEERING ARCHITECTURE
  AUTHORIZED BY: ENGINEER MICHAEL
=============================================================================
"""
import google.generativeai as genai
import os
from datetime import datetime
from typing import List
import schemas

# ---------------------------------------------------------------------------
# GLOBAL PROTOCOL CONFIGURATION  
# ---------------------------------------------------------------------------

# إعداد مفتاح API الخاص بـ Gemini
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY") 
MOCK_MODE = not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE"

def predict_device_health(telemetry_data: List[schemas.Telemetry]) -> dict:
    """
    خوارزمية تحليل الصحة الهندسية للأجهزة بناءً على منطق Med-Guard المطور تحت إشراف مايكل.
    """
    if not telemetry_data:
        return {
            "health_score": 100,
            "status": "No Data",
            "is_healthy": True,
            "malfunction_probability": 0.0,
            "issues": [],
            "insights": ["لا توجد بيانات تيليمترية مسجلة حالياً لمركز مايكل."],
            "prediction": "Unknown"
        }

    sorted_data = sorted(telemetry_data, key=lambda x: x.timestamp)
    latest = sorted_data[-1]
    
    health_score = 100
    issues = []
    insights = []
    malfunction_probability = 0.0

    # 1. Advanced Trend Analysis (Abnormal Growth)
    if len(sorted_data) >= 20:
        recent_pressures = [d.pressure for d in sorted_data[-10:]]
        past_pressures = [d.pressure for d in sorted_data[-20:-10]]
        avg_recent = sum(recent_pressures) / len(recent_pressures)
        avg_past = sum(past_pressures) / len(past_pressures)
        if avg_recent > avg_past * 1.15:
            health_score -= 35
            malfunction_probability = 0.85
            issues.append("نمو غير طبيعي في الضغط (صمام تالف)")
            insights.append("تنبيه تنبؤي: تقارير النمو تشير إلى فشل الصمام خلال 14 يوماً.")

    # 2. Flow Rate Stability Analysis
    if len(sorted_data) >= 2:
        flow_diff = abs(sorted_data[-1].flow_rate - sorted_data[-2].flow_rate)
        if flow_diff > 1.5:
            health_score -= 25
            issues.append("عدم استقرار في معدل التدفق")
            insights.append("خلل ميكانيكي: رصد Valve Jitter في توصيل الغاز.")

    # 3. Battery Stability
    if len(sorted_data) >= 2:
        battery_drop = sorted_data[-2].battery_level - sorted_data[-1].battery_level
        if battery_drop > 5.0:
            health_score -= 20
            issues.append("تفريغ بطارية متسارع (خلل في الخلايا)")
            insights.append("بروتوكول 14: رصد تدهور في خلايا الطاقة.")

    # 4. Pressure Sensor Diagnosis
    if latest.pressure < 28.0:
        health_score -= 45
        malfunction_probability = 0.95
        issues.append("انخفاض حرج في ضغط الغاز (بروتوكول 9)")
    elif latest.pressure < 30.0:
        health_score -= 20
        issues.append("تحذير: ضغط الغاز منخفض")
    elif latest.pressure > 48.0:
        health_score -= 30
        issues.append("ضغط نظام مرتفع جداً")
    elif latest.pressure > 44.0:
        health_score -= 15
        issues.append("ارتفاع في ضغط العمل")

    # 5. Resource Levels
    if latest.soda_lime < 20.0:
        health_score -= 30
        issues.append("استنفاذ حرج للصودا لايم")
    elif latest.soda_lime < 40.0:
        health_score -= 10
    
    # 5. Resource Levels (Gas Level Prediction using Linear Regression)
    if len(sorted_data) >= 5:
        try:
            from sklearn.linear_model import LinearRegression
            import numpy as np
            
            # Prepare data for regression
            X_reg = np.array(range(len(sorted_data))).reshape(-1, 1)
            y_reg = [d.gas_level for d in sorted_data]
            
            # Smooth data a bit
            y_smooth = np.convolve(y_reg, np.ones(3)/3, mode='valid')
            X_smooth = X_reg[1:-1]
            
            if len(y_smooth) >= 3:
                reg_model = LinearRegression().fit(X_smooth, y_smooth)
                slope = reg_model.coef_[0]
                intercept = reg_model.intercept_
                
                # Predict when it hits the threshold (e.g., 20%)
                GAS_THRESHOLD = 20.0
                if slope < 0:
                    readings_to_empty = (GAS_THRESHOLD - intercept) / slope - len(sorted_data)
                    if readings_to_empty > 0:
                        insights.append(f"توقع ذكاء اصطناعي: مستوى الغاز سيصل للحد الحرج خلال {int(readings_to_empty)} قراءة تقريباً.")
                    else:
                        insights.append("تنبيه: مستوى الغاز في نطاق الخطر حالياً.")
                elif slope > 0.5:
                    insights.append("رصد زيادة غير معتادة في مخزون الغاز (عملية ملء؟)")
        except Exception as e:
            try:
                # Pure Python fallback for Linear Regression and Moving Average
                y_reg = [d.gas_level for d in sorted_data]
                y_smooth = [(y_reg[i-1] + y_reg[i] + y_reg[i+1]) / 3.0 for i in range(1, len(y_reg)-1)]
                X_smooth = [float(i) for i in range(1, len(y_reg)-1)]
                
                n = len(y_smooth)
                if n >= 3:
                    sum_x = sum(X_smooth)
                    sum_y = sum(y_smooth)
                    sum_xx = sum(x*x for x in X_smooth)
                    sum_xy = sum(x*y for x, y in zip(X_smooth, y_smooth))
                    
                    denom = n * sum_xx - sum_x * sum_x
                    if abs(denom) > 1e-9:
                        slope = (n * sum_xy - sum_x * sum_y) / denom
                        intercept = (sum_y - slope * sum_x) / n
                        
                        GAS_THRESHOLD = 20.0
                        if slope < 0:
                            readings_to_empty = (GAS_THRESHOLD - intercept) / slope - len(sorted_data)
                            if readings_to_empty > 0:
                                insights.append(f"توقع ذكاء اصطناعي: مستوى الغاز سيصل للحد الحرج خلال {int(readings_to_empty)} قراءة تقريباً.")
                            else:
                                insights.append("تنبيه: مستوى الغاز في نطاق الخطر حالياً.")
                        elif slope > 0.5:
                            insights.append("رصد زيادة غير معتادة في مخزون الغاز (عملية ملء؟)")
            except Exception as inner_e:
                pass

    if latest.gas_level < 10.0:
        health_score -= 25
        issues.append("مستوى غاز منخفض جداً")
    elif latest.gas_level < 30.0:
        health_score -= 10

    # 6. Battery Level
    if latest.battery_level < 15.0:
        health_score -= 20
    elif latest.battery_level < 25.0:
        health_score -= 10

    # تحديد الحالة النهائية
    is_good = health_score >= 80
    status = "Good" if is_good else "Not Good" if health_score < 70 else "Warning"
    
    prediction_text = "النظام مستقر" if is_good else ("فشل وشيك" if malfunction_probability > 0.8 else "مطلوب تدخل هندسي")

    return {
        "health_score": max(0, health_score),
        "status": status,
        "is_healthy": is_good,
        "malfunction_probability": malfunction_probability,
        "issues": issues,
        "insights": insights,
        "prediction": prediction_text
    }
