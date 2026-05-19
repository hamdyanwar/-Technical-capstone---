"""
=============================================================
  Med-Guard AI Model Accuracy Evaluator
  Calculates the accuracy percentage of the AI model to predict device status.
  Engineer Michael's Final Edition.
=============================================================
"""

# -------------------------------------------------------
# 1. Test Dataset
# -------------------------------------------------------
TEST_CASES = [
    # --- Good cases (Normal) ---
    {"p": 35.0, "g": 80.0, "sl": 90.0, "b": 90.0, "p_b": 90.1, "n": 5, "ar": 35.0, "ap": 34.0, "fr": 2.0, "p_fr": 2.0, "actual": "Good"},
    {"p": 40.0, "g": 70.0, "sl": 85.0, "b": 95.0, "p_b": 95.1, "n": 5, "ar": 40.0, "ap": 39.0, "fr": 5.0, "p_fr": 5.0, "actual": "Good"},
    {"p": 37.0, "g": 60.0, "sl": 80.0, "b": 85.0, "p_b": 85.5, "n": 5, "ar": 37.0, "ap": 36.5, "fr": 2.1, "p_fr": 2.0, "actual": "Good"},
    {"p": 33.0, "g": 90.0, "sl": 95.0, "b": 100.0, "p_b": 100, "n": 5, "ar": 33.0, "ap": 32.0, "fr": 1.9, "p_fr": 2.0, "actual": "Good"},
    
    # --- Warning cases (Warning) ---
    {"p": 29.0, "g": 50.0, "sl": 80.0, "b": 80.0, "p_b": 80.1, "n": 5, "ar": 29.0, "ap": 28.5, "fr": 2.0, "p_fr": 2.0, "actual": "Good"},
    {"p": 45.0, "g": 55.0, "sl": 85.0, "b": 85.0, "p_b": 85.5, "n": 5, "ar": 45.0, "ap": 38.5, "fr": 2.0, "p_fr": 2.0, "actual": "Good"},
    {"p": 35.0, "g": 80.0, "sl": 90.0, "b": 90.0, "p_b": 90.1, "n": 5, "ar": 35.0, "ap": 34.5, "fr": 4.5, "p_fr": 2.0, "actual": "Warning"},
    {"p": 32.0, "g": 80.0, "sl": 35.0, "b": 90.0, "p_b": 90.1, "n": 5, "ar": 32.0, "ap": 31.5, "fr": 2.0, "p_fr": 2.1, "actual": "Warning"},
    
    # --- Danger cases (Not Good) ---
    {"p": 25.0, "g": 80.0, "sl": 90.0, "b": 90.0, "p_b": 90.1, "n": 5, "ar": 25.0, "ap": 24.5, "fr": 2.0, "p_fr": 2.0, "actual": "Not Good"},
    {"p": 45.0, "g": 80.0, "sl": 90.0, "b": 10.0, "p_b": 20.0, "n": 5, "ar": 10.0, "ap": 10.0, "fr": 2.0, "p_fr": 2.0, "actual": "Not Good"},
    {"p": 32.0, "g": 5.0, "sl": 15.0, "b": 90.0, "p_b": 90.1, "n": 5, "ar": 5.0, "ap": 5.0, "fr": 2.0, "p_fr": 2.0, "actual": "Not Good"},
]

# -------------------------------------------------------
# 2. Prediction Function (Sync with Michael's logic in ai_service.py)
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

    # Determine final state based on Michael's thresholds
    if score >= 80: return "Good"
    elif score < 70: return "Not Good"
    else: return "Warning"

# -------------------------------------------------------
# 3. Run Evaluation
# -------------------------------------------------------
y_true = [c["actual"] for c in TEST_CASES]
y_pred = [predict_health(c) for c in TEST_CASES]

labels = ["Good", "Warning", "Not Good"]

# Pure Python metrics calculation
total = len(y_true)
correct = sum(1 for t, p in zip(y_true, y_pred) if t == p)
accuracy = correct / total if total > 0 else 0

metrics = {}
for label in labels:
    tp = sum(1 for t, p in zip(y_true, y_pred) if t == label and p == label)
    fp = sum(1 for t, p in zip(y_true, y_pred) if t != label and p == label)
    fn = sum(1 for t, p in zip(y_true, y_pred) if t == label and p != label)
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    support = sum(1 for t in y_true if t == label)
    
    metrics[label] = {
        "precision": precision,
        "recall": recall,
        "f1-score": f1,
        "support": support
    }

weighted_precision = sum(metrics[lbl]["precision"] * metrics[lbl]["support"] for lbl in labels) / total if total > 0 else 0
weighted_recall = sum(metrics[lbl]["recall"] * metrics[lbl]["support"] for lbl in labels) / total if total > 0 else 0
weighted_f1 = sum(metrics[lbl]["f1-score"] * metrics[lbl]["support"] for lbl in labels) / total if total > 0 else 0

# -------------------------------------------------------
# 4. Print Results
# -------------------------------------------------------
print("=" * 60)
print("   Med-Guard Intelligence Layer - AI Model Accuracy Report")
print("=" * 60)
print(f"\n  Accuracy  : {accuracy  * 100:.2f}%")
print(f"  Precision : {weighted_precision * 100:.2f}%")
print(f"  Recall    : {weighted_recall    * 100:.2f}%")
print(f"  F1-Score  : {weighted_f1        * 100:.2f}%")
print(f"\n  Total Test Cases : {len(TEST_CASES)}")
print(f"  Correct Predictions : {correct}")
print(f"  Wrong Predictions  : {len(TEST_CASES) - correct}")

print("\n--- Detailed Classification Report ---")
print(f"{'Label':<12}{'Precision':<15}{'Recall':<18}{'F1-Score':<15}{'Support':<10}")
print("-" * 70)
for label in labels:
    m = metrics[label]
    print(f"{label:<12}{m['precision']*100:<15.2f}%{m['recall']*100:<18.2f}%{m['f1-score']*100:<15.2f}%{m['support']:<10}")

print("\n" + "=" * 60)

# -------------------------------------------------------
# 5. Case-by-Case Breakdown
# -------------------------------------------------------
print("\n--- Case-by-Case Breakdown ---")
print(f"{'#':<4}{'Actual':<12}{'Predicted':<12}{'Result'}")
print("-" * 40)
for i, (t, p) in enumerate(zip(y_true, y_pred)):
    icon = "OK" if t == p else "FAIL"
    print(f"{i+1:<4}{t:<12}{p:<12}{icon}")
