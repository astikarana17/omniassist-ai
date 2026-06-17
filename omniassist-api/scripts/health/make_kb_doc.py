"""Generate a healthcare knowledge-base document (Markdown) for the Trugen agent.

Compiles the curated medicine reference + lab-test ranges + common conditions +
safety FAQs into one upload-ready file the user can add to the agent's KB.

Usage: python -m scripts.health.make_kb_doc
"""
from __future__ import annotations

import sys
from pathlib import Path

from scripts.health.medicines_data import MEDICINES

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

OUT = Path.home() / "Desktop" / "Aanya_Healthcare_Knowledge.txt"

INTRO = """# Healthcare Assistant Knowledge Base

This document grounds the AI Health Assistant. It is patient-education
information in simple language. It is NOT a diagnosis and does not replace a
qualified doctor. For emergencies, contact local emergency services.

---

## How to use this knowledge
- Explain medicines in simple words: what it is, why prescribed, how it works,
  common side effects, timing and food notes.
- For lab values, compare against the normal ranges below and explain high/low
  in plain words; never give a confirmed diagnosis.
- Always recommend consulting a doctor for personal medical advice.

---

## 1. Common Medicines Reference
"""

LAB_SECTION = """
---

## 2. Common Lab Tests & Normal Ranges

> Ranges are typical adult references; labs vary slightly. "High/Low" is general
> information, not a diagnosis.

### Complete Blood Count (CBC)
- Hemoglobin: Men 13.0-17.0 g/dL, Women 12.0-15.0 g/dL. Low = possible anemia.
- WBC (White Blood Cells): 4,000-11,000 /µL. High = possible infection/inflammation.
- Platelets: 150,000-410,000 /µL. Low = bleeding risk; High = clotting risk.
- RBC: 4.5-5.5 million/µL.

### Blood Sugar
- Fasting glucose: 70-99 mg/dL normal; 100-125 prediabetes; 126+ suggests diabetes.
- HbA1c: below 5.7% normal; 5.7-6.4% prediabetes; 6.5%+ suggests diabetes.
- Post-meal (PP) glucose: under 140 mg/dL normal.

### Thyroid Profile
- TSH: 0.4-4.0 mIU/L. High TSH = possible underactive thyroid (hypothyroid);
  Low TSH = possible overactive thyroid (hyperthyroid).
- T3, T4: support the TSH picture.

### Lipid Profile (cholesterol)
- Total cholesterol: under 200 mg/dL desirable.
- LDL ("bad" cholesterol): under 100 mg/dL desirable. Lower is better.
- HDL ("good" cholesterol): above 40 (men) / 50 (women). HIGHER is better.
- Triglycerides: under 150 mg/dL desirable.

### Liver Function (LFT)
- SGPT / ALT: 7-56 U/L. SGOT / AST: 10-40 U/L. High = possible liver stress.
- Bilirubin (total): 0.3-1.2 mg/dL. High = jaundice-related.

### Kidney Function
- Creatinine: 0.7-1.3 mg/dL. High = reduced kidney function.
- Blood Urea: 7-20 mg/dL.

### Vitamins
- Vitamin D: 20-50 ng/mL (below 20 = deficiency).
- Vitamin B12: 200-900 pg/mL (low = deficiency, can cause fatigue/tingling).
"""

CONDITIONS = """
---

## 3. Common Conditions (general overview)

- **High blood pressure (Hypertension):** Often no symptoms. Managed with
  lifestyle + medicines like Amlodipine/Telmisartan/Losartan. See a doctor for
  monitoring.
- **Type 2 Diabetes:** High blood sugar. Signs: thirst, frequent urination,
  fatigue. Managed with Metformin/Gliclazide + diet/exercise.
- **Hypothyroidism:** Underactive thyroid. Signs: tiredness, weight gain, cold
  intolerance. Treated with Levothyroxine.
- **Acidity / GERD:** Burning, reflux. Eased by Omeprazole/Pantoprazole and
  avoiding spicy/late meals.
- **Anemia:** Low hemoglobin. Signs: tiredness, pale skin. Iron/folic acid help.
- **Infections:** Treated with antibiotics (Amoxicillin, Azithromycin) — always
  complete the full course.
- **High cholesterol:** Raises heart risk. Statins (Atorvastatin/Rosuvastatin)
  + diet/exercise.
- **Fever / pain:** Paracetamol for fever and mild pain; NSAIDs (Ibuprofen) for
  inflammation (with food).

For any of these, this is general information — a doctor should confirm and guide treatment.
"""

FAQ = """
---

## 4. Safety FAQs

- **Is this a diagnosis?** No. This is general information to help you understand.
  Only a doctor can diagnose.
- **Should I stop or change my medicine?** Never stop or change a prescribed
  medicine on your own — ask your doctor or pharmacist.
- **What about emergencies?** Chest pain, trouble breathing, severe bleeding,
  stroke signs (face drooping, one-sided weakness), fainting, or thoughts of
  self-harm — seek emergency care or call your local emergency number immediately.
- **Can I rely on this for dosing?** No. Follow the exact dose your doctor wrote.
- **Unclear prescription photo?** Upload it in the app's "Prescription AI" tool
  for an accurate reading.
"""


def _medicine_block(m: dict) -> str:
    lines = [f"### {m['name']}" + (f" ({m['generic_name']})" if m.get("generic_name") else "")]
    fields = [
        ("Purpose", m.get("purpose")),
        ("How it works", m.get("how_it_works")),
        ("Common side effects", m.get("side_effects")),
        ("Warnings", m.get("warnings")),
        ("Food", m.get("food_instructions")),
        ("Timing", m.get("timing")),
    ]
    for label, val in fields:
        if val:
            lines.append(f"- **{label}:** {val}")
    return "\n".join(lines)


def main() -> None:
    parts = [INTRO]
    for m in sorted(MEDICINES, key=lambda x: x["name"].lower()):
        parts.append(_medicine_block(m))
        parts.append("")
    parts.append(LAB_SECTION)
    parts.append(CONDITIONS)
    parts.append(FAQ)
    doc = "\n".join(parts)
    OUT.write_text(doc, encoding="utf-8")
    print(f"[ok] wrote {OUT}")
    print(f"[info] {len(MEDICINES)} medicines + lab ranges + conditions + FAQs")
    print(f"[info] {len(doc):,} characters")


if __name__ == "__main__":
    main()
