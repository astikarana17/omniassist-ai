"""Curated general-health knowledge corpus for the AI Health Assistant RAG.

Patient-friendly, non-diagnostic reference entries. Each is embedded and retrieved
to ground the assistant's answers. Safe by design: general information only, with
clear "see a doctor / emergency" guidance where relevant. Expand freely — for large
scale, ingest a trusted corpus (e.g. MedQuAD/MedlinePlus) into the same table.
"""
from __future__ import annotations

# Each entry: {title, category, content}
HEALTH_KNOWLEDGE: list[dict] = [
    # ---- Common conditions ----
    {"title": "Common cold", "category": "condition",
     "content": "A viral infection of the nose and throat. Symptoms: runny or blocked nose, sneezing, sore throat, mild cough, sometimes low fever. Usually clears in 7–10 days. Rest, fluids, warm saltwater gargles and paracetamol for aches help. Antibiotics do NOT work on colds. See a doctor if fever is high or lasts >3 days, breathing is hard, or symptoms worsen after a week."},
    {"title": "Influenza (flu)", "category": "condition",
     "content": "A viral infection causing sudden high fever, body aches, headache, dry cough, fatigue and chills — usually more severe than a cold. Rest, fluids and paracetamol help. Antivirals may help if started early in high-risk people. Seek care for trouble breathing, chest pain, confusion, or persistent high fever. Annual flu vaccination reduces risk."},
    {"title": "Hypertension (high blood pressure)", "category": "condition",
     "content": "Blood pressure persistently at or above 140/90 mmHg (often no symptoms). Long-term risk: heart attack, stroke, kidney disease. Managed with less salt, weight control, exercise, limiting alcohol, not smoking, and prescribed medicines (e.g. amlodipine, telmisartan). Take medicines daily as directed even if you feel fine. Get readings checked regularly."},
    {"title": "Type 2 diabetes", "category": "condition",
     "content": "A condition where blood sugar stays high because the body resists or under-produces insulin. Symptoms can include excess thirst, frequent urination, tiredness, slow-healing wounds. Managed with diet, exercise, weight loss and medicines (e.g. metformin). Untreated high sugar harms eyes, kidneys, nerves and heart. Regular HbA1c and foot/eye checks are important."},
    {"title": "Asthma", "category": "condition",
     "content": "A long-term condition where airways narrow and inflame, causing wheezing, cough, chest tightness and breathlessness, often triggered by dust, smoke, cold air, exercise or allergens. Managed with inhalers — relievers (e.g. salbutamol) for symptoms and preventers (steroid inhalers) daily. Seek emergency care if a reliever inhaler isn't helping or speaking is hard."},
    {"title": "Migraine", "category": "condition",
     "content": "A throbbing, often one-sided headache that can come with nausea and sensitivity to light or sound, sometimes preceded by visual 'aura'. Rest in a dark quiet room, hydrate, and use painkillers early. Identifying triggers (stress, skipped meals, poor sleep, certain foods) helps. See a doctor for frequent migraines, a sudden 'worst-ever' headache, or headache with weakness, confusion or stiff neck."},
    {"title": "Acid reflux / GERD", "category": "condition",
     "content": "Stomach acid flowing back into the food pipe, causing heartburn (burning behind the chest), sour taste, or cough — often worse after large or fatty meals and when lying down. Helps: smaller meals, avoiding late-night eating, weight loss, cutting spicy/fatty foods, raising the bed head. Antacids and acid-reducers (e.g. omeprazole) are used. Persistent symptoms, trouble swallowing or weight loss need a doctor."},
    {"title": "Urinary tract infection (UTI)", "category": "condition",
     "content": "An infection (usually bacterial) of the urinary system causing burning when urinating, frequent urge, cloudy or smelly urine, and lower-belly discomfort. Drink plenty of water. Most need prescribed antibiotics. Seek urgent care for fever, back/flank pain, vomiting or blood in urine, which can mean a kidney infection."},
    {"title": "Anemia", "category": "condition",
     "content": "Low red blood cells or hemoglobin, often from iron deficiency, causing tiredness, pale skin, breathlessness and dizziness. Iron-rich foods (leafy greens, legumes, red meat) and treating the cause help; iron supplements may be prescribed. Heavy periods, poor diet or bleeding can cause it. A blood test (CBC) confirms it."},
    {"title": "Hypothyroidism", "category": "condition",
     "content": "An underactive thyroid making too little hormone, causing fatigue, weight gain, cold intolerance, dry skin and low mood. Diagnosed by TSH/T4 blood tests and treated with daily thyroid hormone (levothyroxine), usually taken on an empty stomach. Lifelong monitoring keeps levels right."},

    # ---- Symptoms ----
    {"title": "Fever", "category": "symptom",
     "content": "A body temperature above ~38°C (100.4°F), usually a sign the body is fighting infection. Rest, fluids, and paracetamol or ibuprofen for comfort. Seek care for fever above 39.5°C, fever lasting >3 days, in infants under 3 months, or with rash, stiff neck, breathing difficulty, confusion or dehydration."},
    {"title": "Cough", "category": "symptom",
     "content": "Usually from colds, flu, allergies or irritation; most resolve in 1–2 weeks. Warm fluids, honey (not for under-1s) and steam help. See a doctor for a cough lasting >3 weeks, coughing blood, breathlessness, chest pain, high fever, or unexplained weight loss."},
    {"title": "Sore throat", "category": "symptom",
     "content": "Often viral and self-limiting; warm saltwater gargles, fluids and lozenges soothe it. A bacterial 'strep' throat (severe pain, fever, swollen tonsils with white patches, no cough) may need antibiotics. Seek care for difficulty breathing or swallowing, drooling, or a muffled voice."},
    {"title": "Headache", "category": "symptom",
     "content": "Most are tension-type (a tight band) or migraine and ease with rest, hydration, regular meals and simple painkillers. Red flags needing urgent care: a sudden severe 'thunderclap' headache, headache with fever and stiff neck, weakness, vision loss, confusion, or after a head injury."},
    {"title": "Abdominal (stomach) pain", "category": "symptom",
     "content": "Common causes include indigestion, gas, constipation, period cramps or a stomach bug. Rest, fluids and a light diet often help. Seek urgent care for severe or worsening pain, pain with high fever or vomiting, a rigid swollen belly, blood in stool or vomit, or pain in the lower-right belly (possible appendicitis)."},
    {"title": "Dizziness", "category": "symptom",
     "content": "Feeling lightheaded or like the room is spinning, from causes such as dehydration, low blood sugar, inner-ear problems, low blood pressure or certain medicines. Sit or lie down, hydrate and rise slowly. Seek care for dizziness with chest pain, fainting, severe headache, slurred speech, weakness or trouble walking."},
    {"title": "Diarrhea", "category": "symptom",
     "content": "Loose, frequent stools usually from a viral or bacterial gut infection or food. The main risk is dehydration — drink oral rehydration solution (ORS) and fluids. Most settle in a few days. Seek care for blood in stool, high fever, signs of dehydration (very dry mouth, little urine, dizziness), or symptoms lasting beyond a few days; this is especially urgent in babies and the elderly."},

    # ---- Lab tests & vitals ----
    {"title": "Complete blood count (CBC)", "category": "lab_test",
     "content": "Measures red cells, white cells, hemoglobin and platelets. Low hemoglobin suggests anemia; high white cells often suggest infection; low platelets can affect clotting. It's a broad screening test — abnormal values are interpreted together with symptoms by a doctor."},
    {"title": "Blood sugar (glucose) and HbA1c", "category": "lab_test",
     "content": "Fasting glucose 70–99 mg/dL is normal; 100–125 is prediabetes; 126+ on two tests suggests diabetes. HbA1c reflects average sugar over ~3 months: under 5.7% normal, 5.7–6.4% prediabetes, 6.5%+ diabetes. These guide diagnosis and how well diabetes is controlled."},
    {"title": "Lipid profile (cholesterol)", "category": "lab_test",
     "content": "Measures total, LDL ('bad'), HDL ('good') cholesterol and triglycerides. High LDL and triglycerides raise heart-disease risk; higher HDL is protective. Diet, exercise, weight control and sometimes statins improve it. Targets depend on overall heart risk."},
    {"title": "Thyroid function (TSH)", "category": "lab_test",
     "content": "TSH is the main screen for thyroid problems. High TSH usually means an underactive thyroid (hypothyroidism); low TSH means an overactive thyroid (hyperthyroidism). It's read alongside T3/T4 and symptoms."},
    {"title": "Liver function test (LFT)", "category": "lab_test",
     "content": "Checks enzymes (ALT, AST), bilirubin and proteins to assess liver health. Raised enzymes can come from fatty liver, alcohol, viral hepatitis or some medicines. Mild changes are common; a doctor interprets the pattern with your history."},
    {"title": "Kidney function (creatinine, eGFR)", "category": "lab_test",
     "content": "Creatinine and the calculated eGFR estimate how well kidneys filter blood. High creatinine / low eGFR can indicate reduced kidney function from dehydration, diabetes, high blood pressure or other causes. Trends over time matter more than a single value."},
    {"title": "Blood pressure reading", "category": "vital",
     "content": "Written as systolic/diastolic (e.g. 120/80 mmHg). Normal is under 120/80; 120–129/<80 is elevated; 130–139/80–89 is stage 1 and 140/90+ is stage 2 high blood pressure. Measure rested and seated; a single high reading isn't a diagnosis."},
    {"title": "Normal vital sign ranges (adult)", "category": "vital",
     "content": "Resting heart rate ~60–100 beats/min; breathing ~12–20 per min; oxygen saturation (SpO2) 95–100%; temperature ~36.1–37.2°C. Values outside these, especially SpO2 under 92% or a very fast/slow heart rate with symptoms, warrant medical attention."},

    # ---- Medication classes ----
    {"title": "Paracetamol (acetaminophen)", "category": "medication_class",
     "content": "A common pain and fever reliever, usually gentle on the stomach. Adults typically take it as directed, not exceeding the daily limit on the label, because overdose harms the liver. Avoid combining multiple products that all contain paracetamol. Follow your doctor's or the label's dosing."},
    {"title": "NSAIDs (ibuprofen, diclofenac)", "category": "medication_class",
     "content": "Reduce pain, fever and inflammation. Best taken with food as they can irritate the stomach; long-term or high-dose use can cause ulcers and affect kidneys and blood pressure. Caution in people with stomach ulcers, kidney disease or on blood thinners. Use the lowest effective dose for the shortest time."},
    {"title": "Antibiotics", "category": "medication_class",
     "content": "Treat bacterial infections — they do NOT work against viruses (colds, flu, most sore throats). Always finish the full prescribed course even if you feel better, to prevent resistance and relapse. Never share or reuse leftover antibiotics. Tell your doctor about allergies (e.g. to penicillin)."},
    {"title": "Antihistamines", "category": "medication_class",
     "content": "Relieve allergy symptoms like sneezing, itching, runny nose and hives. Newer ones (cetirizine, loratadine) cause less drowsiness than older ones (chlorpheniramine). Useful for hay fever and mild allergic reactions; severe reactions need emergency care."},
    {"title": "Antacids and acid reducers", "category": "medication_class",
     "content": "Antacids neutralize stomach acid for quick heartburn relief; H2 blockers and proton-pump inhibitors (e.g. omeprazole) reduce acid production for longer control of reflux and ulcers. Persistent symptoms, trouble swallowing or weight loss should be checked by a doctor."},

    # ---- First aid ----
    {"title": "Minor cuts and scrapes", "category": "first_aid",
     "content": "Wash hands, rinse the wound under clean running water, apply gentle pressure with a clean cloth to stop bleeding, then cover with a sterile dressing. Seek care for deep wounds, heavy bleeding that won't stop, signs of infection (spreading redness, pus, fever), or if tetanus protection is not up to date."},
    {"title": "Burns (minor)", "category": "first_aid",
     "content": "Cool the burn under cool (not ice-cold) running water for ~20 minutes, remove tight items before swelling, and cover loosely with cling film or a clean non-stick dressing. Do not apply butter, toothpaste or ice. Seek care for large burns, burns on the face/hands/genitals, deep or blistering burns, or chemical/electrical burns."},
    {"title": "Nosebleed", "category": "first_aid",
     "content": "Sit up, lean slightly forward, and pinch the soft part of the nose firmly for 10–15 minutes while breathing through the mouth. Avoid tilting the head back. Seek care if bleeding doesn't stop after 20 minutes, is very heavy, follows an injury, or recurs frequently."},
    {"title": "Choking (adult)", "category": "first_aid",
     "content": "If someone can't breathe, speak or cough, give up to 5 firm back blows between the shoulder blades, then up to 5 abdominal thrusts (Heimlich), alternating until the object clears. If they become unconscious, call emergency services and start CPR. Always call for emergency help early."},
    {"title": "Sprains and strains", "category": "first_aid",
     "content": "Use R.I.C.E.: Rest, Ice (20 min wrapped, not directly on skin), Compression with a bandage, and Elevation. Avoid heat early on. Most improve in days to weeks. Seek care if you can't bear weight, the joint looks deformed, is very swollen, or pain is severe."},

    # ---- Prevention, lifestyle, nutrition ----
    {"title": "Staying hydrated", "category": "prevention",
     "content": "Most adults need roughly 2–3 litres of fluid a day, more in heat, exercise or illness with fever/diarrhea. Signs of good hydration include pale-yellow urine. Water is best; limit sugary drinks. Older adults and children dehydrate faster and need closer attention."},
    {"title": "Healthy balanced diet", "category": "nutrition",
     "content": "Fill half the plate with vegetables and fruit, include whole grains, lean protein (beans, fish, eggs, poultry) and healthy fats, and limit salt, added sugar and ultra-processed foods. This supports weight, heart, sugar and gut health. Portion size and consistency matter more than any single 'superfood'."},
    {"title": "Physical activity guidance", "category": "prevention",
     "content": "Adults benefit from at least 150 minutes of moderate activity (brisk walking, cycling) per week plus muscle-strengthening twice weekly. Even short daily walks help blood pressure, sugar, mood and weight. Start gradually and build up; check with a doctor first if you have heart disease or are very inactive."},
    {"title": "Better sleep (sleep hygiene)", "category": "prevention",
     "content": "Adults generally need 7–9 hours. Keep a regular schedule, a dark cool quiet room, and avoid screens, caffeine and heavy meals before bed. Persistent insomnia, loud snoring with daytime sleepiness (possible sleep apnea), or unrefreshing sleep should be discussed with a doctor."},
    {"title": "Vaccination basics", "category": "prevention",
     "content": "Vaccines train the immune system to prevent serious infections. Routine childhood immunisations, plus adult boosters (e.g. tetanus) and seasonal flu and COVID-19 vaccines for eligible people, are widely recommended. Mild soreness or low fever after a shot is normal. Follow your local immunisation schedule."},
    {"title": "Quitting smoking", "category": "prevention",
     "content": "Stopping smoking quickly lowers risks of heart disease, stroke, lung disease and cancer, and benefits begin within days. Nicotine-replacement (patches, gum), prescribed medicines and counselling roughly double success rates. Setting a quit date and removing triggers helps."},

    # ---- Mental health ----
    {"title": "Stress and anxiety", "category": "mental_health",
     "content": "Feeling worried or tense at times is normal. Helpful steps: regular sleep and exercise, slow breathing, limiting caffeine, talking to someone, and breaking tasks into small steps. If anxiety is persistent, interferes with daily life, or comes with panic attacks, a doctor or counsellor can help with therapy and, if needed, medication."},
    {"title": "Low mood and depression", "category": "mental_health",
     "content": "Persistent sadness, loss of interest, low energy, sleep or appetite changes, or hopelessness lasting more than two weeks may indicate depression. It's common and treatable with talking therapy and/or medication. Reach out to a doctor. If you have thoughts of harming yourself, seek emergency help or a crisis line immediately."},

    # ---- Women's & child health ----
    {"title": "Menstrual cramps", "category": "womens_health",
     "content": "Lower-belly cramping around periods is common, from the uterus contracting. Heat packs, gentle exercise, hydration and NSAIDs like ibuprofen (with food) usually help. See a doctor for very severe pain, periods that disrupt life, unusually heavy bleeding, or pain with fever."},
    {"title": "Pregnancy warning signs", "category": "womens_health",
     "content": "During pregnancy, seek prompt care for heavy bleeding, severe abdominal pain, severe headache with vision changes or swelling, high fever, reduced baby movements, or fluid leaking. Routine antenatal check-ups, folic acid, and avoiding alcohol and smoking support a healthy pregnancy. Always confirm medication safety with a doctor."},
    {"title": "Fever in children", "category": "child_health",
     "content": "Keep the child comfortable and hydrated; weight-appropriate paracetamol or ibuprofen can ease discomfort. Seek urgent care for any fever in a baby under 3 months, a fever with a non-fading rash, stiff neck, breathing difficulty, persistent vomiting, drowsiness, a seizure, or signs of dehydration. Never give aspirin to children."},

    # ---- Emergencies & when to seek care ----
    {"title": "Heart attack warning signs", "category": "emergency",
     "content": "Call emergency services immediately for chest pain or pressure (which may spread to the arm, jaw or back), breathlessness, cold sweat, nausea or lightheadedness — especially in people with diabetes, high blood pressure or heart disease. Do not drive yourself; chew aspirin only if advised. Every minute matters."},
    {"title": "Stroke warning signs (FAST)", "category": "emergency",
     "content": "Use FAST: Face drooping, Arm weakness, Speech difficulty — Time to call emergency services. Other signs include sudden numbness on one side, confusion, severe headache, or trouble seeing or walking. Act immediately; rapid treatment can limit brain damage."},
    {"title": "Severe allergic reaction (anaphylaxis)", "category": "emergency",
     "content": "Signs include swelling of the lips/tongue/throat, difficulty breathing, widespread hives, dizziness or collapse, often soon after a trigger (food, sting, medicine). Use an adrenaline auto-injector (EpiPen) if available and call emergency services immediately. This is life-threatening and needs urgent care."},
    {"title": "When to seek emergency care", "category": "emergency",
     "content": "Call emergency services for trouble breathing, chest pain, stroke signs, severe bleeding that won't stop, sudden severe pain, fainting, a seizure, confusion, a severe allergic reaction, or thoughts of self-harm. When unsure, it is safer to get checked promptly."},

    # ---- Meta / about ----
    {"title": "What this AI Health Assistant can and cannot do", "category": "general",
     "content": "It explains medicines, lab results, symptoms and general health questions in plain language, grounded in a medical knowledge base. It does NOT diagnose, prescribe doses, or replace a doctor. For personal medical decisions, always consult a qualified clinician, and for emergencies seek urgent care."},
]
