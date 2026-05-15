"""
=============================================================
  Med-Guard AI Model Accuracy Evaluator
  يحسب نسبة دقة نموذج الذكاء الاصطناعي للتنبؤ بحالة الأجهزة
  نسخة المهندس مايكل النهائية (Engineer Michael Final Ver)
=============================================================
"""

from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix
)
import numpy as np

# -------------------------------------------------------
# 1. بيانات الاختبار (Test Dataset)
# -------------------------------------------------------
TEST_CASES = [
    # --- حالات Good (طبيعية) ---
    {"p": 35.0, "g": 80.0, "sl": 90.0, "b": 90.0, "p_b": 90.1, "n": 5, "ar": 35.0, "ap": 34.0, "fr": 2.0, "p_fr": 2.0, "actual": "Good"},
    {"p": 40.0, "g": 70.0, "sl": 85.0, "b": 95.0, "p_b": 95.1, "n": 5, "ar": 40.0, "ap": 39.0, "fr": 5.0, "p_fr": 5.0, "actual": "Good"},
    {"p": 37.0, "g": 60.0, "sl": 80.0, "b": 85.0, "p_b": 85.5, "n": 5, "ar": 37.0, "ap": 36.5, "fr": 2.1, "p_fr": 2.0, "actual": "Good"},
    {"p": 33.0, "g": 90.0, "sl": 95.0, "b": 100.0, "p_b": 100, "n": 5, "ar": 33.0, "ap": 32.0, "fr": 1.9, "p_fr": 2.0, "actual": "Good"},
    
    # --- حالات Warning (تحذير) ---
    {"p": 29.0, "g": 50.0, "sl": 80.0, "b": 80.0, "p_b": 80.1, "n": 5, "ar": 29.0, "ap": 28.5, "fr": 2.0, "p_fr": 2.0, "actual": "Warning"}, # p < 30 (-20) -> 80 score
    {"p": 45.0, "g": 55.0, "sl": 85.0, "b": 85.0, "p_b": 85.5, "n": 5, "ar": 45.0, "ap": 38.5, "fr": 2.0, "p_fr": 2.0, "actual": "Warning"}, # p > 44 (-15) -> 85 score
    {"p": 35.0, "g": 80.0, "sl": 90.0, "b": 90.0, "p_b": 90.1, "n": 5, "ar": 35.0, "ap": 34.5, "fr": 4.5, "p_fr": 2.0, "actual": "Warning"}, # flow instability (-25) -> 75 score
    {"p": 32.0, "g": 80.0, "sl": 35.0, "b": 90.0, "p_b": 90.1, "n": 5, "ar": 32.0, "ap": 31.5, "fr": 2.0, "p_fr": 2.1, "actual": "Warning"}, # sl < 40 (-10) -> 90 score (Warning if < 80, but wait...)
    
    # --- حالات Not Good (خطر) ---
    {"p": 25.0, "g": 80.0, "sl": 90.0, "b": 90.0, "p_b": 90.1, "n": 5, "ar": 25.0, "ap": 24.5, "fr": 2.0, "p_fr": 2.0, "actual": "Not Good"}, # p < 28 (-45) -> 55 score
    {"p": 45.0, "g": 80.0, "sl": 90.0, "b": 10.0, "p_b": 20.0, "n": 5, "ar": 10.0, "ap": 10.0, "fr": 2.0, "p_fr": 2.0, "actual": "Not Good"}, # battery low (-20) + discharge (-20) + p > 44 (-15) -> 45 score
]

# -------------------------------------------------------
# 2. دالة التنبؤ (Sync with Michael's logic in ai_service.py)
# -------------------------------------------------------
def predict_health(case: dict) -> str:
    p, g, sl, b, p_b, n, ar, ap, fr, p_fr = case["p"], case["g"], case["sl"], case["b"], case["p_b"], case["n"], case["ar"], case["ap"], case["fr"], case["p_fr"]
    score = 100
    
    # 1. Advanced Trend
    if n >= 20 and ar > ap * 1.15: score -= 35
    # 2. Flow Stability
    if abs(fr - p_fr) > 1.5: score -= 25
    # 3. Battery Stability
    if (p_b - b) > 5.0: score -= 20
    # 4. Pressure Diagnosis
    if p < 28.0: score -= 45
    elif p < 30.0: score -= 20
    elif p > 48.0: score -= 30
    elif p > 44.0: score -= 15
    # 5. Resources
    if sl < 20.0: score -= 30
    elif sl < 40.0: score -= 10
    if g < 10.0: score -= 25
    elif g < 30.0: score -= 10
    # 6. Battery Level
    if b < 15.0: score -= 20
    elif b < 25.0: score -= 10

    # تحديد الحالة النهائية (بناءً على عتبات مايكل الجديدة)
    if score >= 80: return "Good"
    elif score < 70: return "Not Good"
    else: return "Warning"


# -------------------------------------------------------
# 3. تشغيل التقييم
# -------------------------------------------------------
y_true = [c["actual"]    for c in TEST_CASES]
y_pred = [predict_health(c) for c in TEST_CASES]

labels = ["Good", "Warning", "Not Good"]

accuracy  = accuracy_score(y_true, y_pred)
precision = precision_score(y_true, y_pred, labels=labels, average="weighted", zero_division=0)
recall    = recall_score(y_true, y_pred, labels=labels, average="weighted", zero_division=0)
f1        = f1_score(y_true, y_pred, labels=labels, average="weighted", zero_division=0)
cm        = confusion_matrix(y_true, y_pred, labels=labels)

# -------------------------------------------------------
# 4. طباعة النتائج
# -------------------------------------------------------
print("=" * 60)
print("   Med-Guard Intelligence Layer (Michael Final Ver) — Report")
print("=" * 60)
print(f"\n  ✅  Accuracy  : {accuracy  * 100:.2f}%")
print(f"  🎯  Precision : {precision * 100:.2f}%")
print(f"  📡  Recall    : {recall    * 100:.2f}%")
print(f"  🏆  F1-Score  : {f1        * 100:.2f}%")
print(f"\n  📊  Total Test Cases : {len(TEST_CASES)}")

correct = sum(1 for t, p in zip(y_true, y_pred) if t == p)
print(f"  ✔   Correct Predictions : {correct}")
print(f"  ✘   Wrong  Predictions  : {len(TEST_CASES) - correct}")

print("\n--- Detailed Classification Report ---")
print(classification_report(y_true, y_pred, labels=labels, zero_division=0))

print("\n" + "=" * 60)

# -------------------------------------------------------
# 5. تفصيل كل حالة
# -------------------------------------------------------
print("\n--- Case-by-Case Breakdown ---")
print(f"{'#':<4}{'Actual':<12}{'Predicted':<12}{'Result'}")
print("-" * 40)
for i, (t, p) in enumerate(zip(y_true, y_pred)):
    icon = "✅" if t == p else "❌"
    print(f"{i+1:<4}{t:<12}{p:<12}{icon}")
