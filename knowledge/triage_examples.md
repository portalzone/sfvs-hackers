# Triage Escalation Knowledge Base
# NL Emergency Department — Synthetic Training Examples
# 1000 cases across 10 clinical categories

This knowledge base contains labelled triage examples to help the agent
ground its escalation reasoning in consistent clinical patterns.

---
## Category: Abdo
Total cases: 107 | Escalate: 21 | Routine: 86

### Escalation examples (flag = YES)
**Case 13** | Age: 66M | CTAS 2
Vitals: HR 110  BP 136/68  RR 18  O2 97%  Temp 37.9°C
Note: 66F, RUQ pain radiating to R shoulder tip onset 45min ago. Worse after fatty meal. Temp 38.2. Murphy sign positive.
Correct flag: YES — CTAS 2

**Case 116** | Age: 60M | CTAS 2
Vitals: HR 79  BP 103/85  RR 24  O2 96%  Temp 37.5°C
Note: Severe diffuse abdo pain, onset sudden this morning. Abdomen rigid on exam. Hx of PUD. BP 102/68. Guarding present.
Correct flag: YES — CTAS 2

**Case 205** | Age: 31M | CTAS 2
Vitals: HR 92  BP 134/72  RR 21  O2 96%  Temp 37.4°C
Note: 31F, RUQ pain radiating to R shoulder tip onset 20min ago. Worse after fatty meal. Temp 38.2. Murphy sign positive.
Correct flag: YES — CTAS 2

### Routine examples (flag = NO)
**Case 7** | Age: 64M | CTAS 3
Vitals: HR 102  BP 115/82  RR 24  O2 96%  Temp 37.8°C
Note: 64F, 1hr ago onset RLQ pain now diffuse. Sexually active, LMP 6wks ago. Positive urine hCG. Shoulder tip pain. Onset 1hr ago.
Correct flag: NO — CTAS 3

**Case 55** | Age: 31F | CTAS 3
Vitals: HR 88  BP 136/81  RR 17  O2 96%  Temp 38.2°C
Note: 31M, sudden severe epigastric pain. States pain 10/10. Vomiting x4. Rigid abdomen. Previous hx of pancreatitis. Onset earlier today.
Correct flag: NO — CTAS 3

---
## Category: Cardiac
Total cases: 115 | Escalate: 115 | Routine: 0

### Escalation examples (flag = YES)
**Case 15** | Age: 50M | CTAS 1
Vitals: HR 96  BP 180/101  RR 24  O2 92%  Temp 36.5°C
Note: Tearing chest pain radiating to back, onset sudden earlier today. Hx of Marfan syndrome. BP asymmetry noted. Pale, diaphoretic.
Correct flag: YES — CTAS 1

**Case 21** | Age: 72F | CTAS 1
Vitals: HR 103  BP 142/100  RR 24  O2 91%  Temp 36.3°C
Note: EMS arrival, 72M post ROSC. Bystander CPR x8min. AED shocked x1. Now drowsy but responsive. Onset of collapse 45min ago.
Correct flag: YES — CTAS 1

**Case 22** | Age: 60F | CTAS 1
Vitals: HR 118  BP 151/98  RR 16  O2 92%  Temp 36.6°C
Note: EMS arrival, 60M post ROSC. Bystander CPR x8min. AED shocked x1. Now drowsy but responsive. Onset of collapse 45min ago.
Correct flag: YES — CTAS 1

### Routine examples (flag = NO)
---
## Category: Fracture
Total cases: 130 | Escalate: 0 | Routine: 130

### Escalation examples (flag = YES)
### Routine examples (flag = NO)
**Case 27** | Age: 36M | CTAS 3
Vitals: HR 89  BP 130/71  RR 14  O2 100%  Temp 36.5°C
Note: Pt c/o heel pain after jump from height. Unable to wt bear bilaterally. Bilateral calcaneal tenderness. MOI 30min ago.
Correct flag: NO — CTAS 3

**Case 34** | Age: 17F | CTAS 3
Vitals: HR 95  BP 133/75  RR 16  O2 97%  Temp 36.9°C
Note: 17F, low back pain after lifting at work. Hx of osteoporosis. Unable to stand upright. No lower limb neuro deficit. Onset 45min ago.
Correct flag: NO — CTAS 3

---
## Category: Head Injury
Total cases: 66 | Escalate: 66 | Routine: 0

### Escalation examples (flag = YES)
**Case 18** | Age: 22M | CTAS 2
Vitals: HR 102  BP 149/78  RR 18  O2 95%  Temp 37.0°C
Note: Pt presents after assault, struck in head x2 with blunt object. LOC unknown. Laceration R temporal region. Onset overnight.
Correct flag: YES — CTAS 2

**Case 60** | Age: 19F | CTAS 2
Vitals: HR 91  BP 131/83  RR 20  O2 96%  Temp 36.7°C
Note: 19M, fell from ladder approx 3m. Hit head. Found by coworker confused. GCS 13. No helmet. Onset earlier today.
Correct flag: YES — CTAS 2

**Case 64** | Age: 25M | CTAS 2
Vitals: HR 73  BP 165/87  RR 16  O2 99%  Temp 36.9°C
Note: 25M, fell from ladder approx 3m. Hit head. Found by coworker confused. GCS 13. No helmet. Onset overnight.
Correct flag: YES — CTAS 2

### Routine examples (flag = NO)
---
## Category: Mental Health
Total cases: 69 | Escalate: 0 | Routine: 69

### Escalation examples (flag = YES)
### Routine examples (flag = NO)
**Case 5** | Age: 39M | CTAS 2
Vitals: HR 86  BP 136/77  RR 14  O2 97%  Temp 37.2°C
Note: Pt brought by police after found wandering. Agitated, not oriented to place or time. Hx of schizophrenia. Off meds x1wk.
Correct flag: NO — CTAS 2

**Case 10** | Age: 41M | CTAS 3
Vitals: HR 104  BP 127/70  RR 20  O2 96%  Temp 37.2°C
Note: 41F, presented after deliberate self-harm, superficial lacerations bilateral forearms. Alert. States feeling unsafe. Support person present.
Correct flag: NO — CTAS 3

---
## Category: Minor
Total cases: 217 | Escalate: 0 | Routine: 217

### Escalation examples (flag = YES)
### Routine examples (flag = NO)
**Case 1** | Age: 23F | CTAS 5
Vitals: HR 69  BP 112/69  RR 17  O2 97%  Temp 36.7°C
Note: Ear pain L side x2d, afebrile. No hearing loss reported. No vertigo. Hx of recurrent otitis media as child.
Correct flag: NO — CTAS 5

**Case 9** | Age: 45F | CTAS 5
Vitals: HR 69  BP 131/83  RR 17  O2 99%  Temp 36.8°C
Note: Mild ankle sprain, wt bearing. Soft tissue swelling only. Ottawa rules negative. MOI: twisted playing basketball.
Correct flag: NO — CTAS 5

---
## Category: Paediatric
Total cases: 47 | Escalate: 47 | Routine: 0

### Escalation examples (flag = YES)
**Case 4** | Age: 38M | CTAS 2
Vitals: HR 134  BP 87/62  RR 26  O2 96%  Temp 38.3°C
Note: 6yo F, sudden onset stridor and drooling. Appears toxic, sitting forward. Hx of no vaccinations. Onset 1.5hr ago.
Correct flag: YES — CTAS 2

**Case 35** | Age: 18M | CTAS 2
Vitals: HR 129  BP 102/59  RR 31  O2 91%  Temp 37.8°C
Note: 8yo F, sudden onset severe headache and vomiting x3. Photophobia. Neck stiffness on exam. Temp 38.9. Onset earlier today.
Correct flag: YES — CTAS 2

**Case 38** | Age: 52F | CTAS 2
Vitals: HR 145  BP 107/50  RR 40  O2 96%  Temp 38.9°C
Note: 3yo M, fever 39.8 x2d, decreased oral intake. Inconsolable crying. Bulging fontanelle noted by mother. Onset 1hr ago.
Correct flag: YES — CTAS 2

### Routine examples (flag = NO)
---
## Category: Respiratory
Total cases: 65 | Escalate: 65 | Routine: 0

### Escalation examples (flag = YES)
**Case 6** | Age: 47M | CTAS 2
Vitals: HR 120  BP 131/84  RR 33  O2 87%  Temp 37.3°C
Note: 47F, known severe asthma, not responding to nebs at home. Too breathless to complete sentences. O2 sat 88%. Onset 2hr ago.
Correct flag: YES — CTAS 2

**Case 19** | Age: 68F | CTAS 2
Vitals: HR 104  BP 124/89  RR 27  O2 92%  Temp 37.1°C
Note: 68M, sudden onset SOB and R sided chest pain onset earlier today. Tall thin male. No hx of similar. O2 sat 91% on RA.
Correct flag: YES — CTAS 2

**Case 23** | Age: 68F | CTAS 2
Vitals: HR 129  BP 127/82  RR 26  O2 89%  Temp 37.8°C
Note: Near-drowning, 68M pulled from water. Coughing, decreased O2 sat 87%. GCS 13. Brought by bystanders. Onset earlier today.
Correct flag: YES — CTAS 2

### Routine examples (flag = NO)
---
## Category: Sepsis
Total cases: 92 | Escalate: 92 | Routine: 0

### Escalation examples (flag = YES)
**Case 8** | Age: 47F | CTAS 2
Vitals: HR 110  BP 84/64  RR 27  O2 89%  Temp 39.3°C
Note: Nursing home resident, 47F, brought in unresponsive. Staff report fever x2d, not eating. Foley catheter in situ. Temp 40.1.
Correct flag: YES — CTAS 2

**Case 16** | Age: 79F | CTAS 2
Vitals: HR 129  BP 98/57  RR 29  O2 94%  Temp 39.0°C
Note: 79M IVDU, presents with fever, rigors, new cardiac murmur. Hx of previous endocarditis. Temp 39.8, HR 130. Onset 1hr ago.
Correct flag: YES — CTAS 2

**Case 17** | Age: 49M | CTAS 2
Vitals: HR 126  BP 85/46  RR 23  O2 86%  Temp 38.7°C
Note: 49M, confusion and fever. Family reports hx of recent abdo surgery 1wk ago. Wound site erythematous. HR 116, BP 94/60.
Correct flag: YES — CTAS 2

### Routine examples (flag = NO)
---
## Category: Stroke
Total cases: 92 | Escalate: 92 | Routine: 0

### Escalation examples (flag = YES)
**Case 2** | Age: 50M | CTAS 1
Vitals: HR 105  BP 160/108  RR 22  O2 96%  Temp 36.5°C
Note: Pt c/o sudden onset facial drooping L side, slurred speech x1hr ago. Wife states arm weakness noted at home. No hx of CVA. Last known well 1hr ago.
Correct flag: YES — CTAS 1

**Case 3** | Age: 55F | CTAS 1
Vitals: HR 79  BP 161/110  RR 19  O2 93%  Temp 36.4°C
Note: 55M found by family slumped in chair. Unresponsive to voice, moaning. L sided facial droop noted. Last seen normal this morning.
Correct flag: YES — CTAS 1

**Case 31** | Age: 66F | CTAS 1
Vitals: HR 98  BP 183/108  RR 20  O2 97%  Temp 36.3°C
Note: Sudden severe headache described as worst of life. Came on in seconds. Vomiting x2 en route. Onset 45min ago. Neuro exam abnormal on arrival.
Correct flag: YES — CTAS 1

### Routine examples (flag = NO)