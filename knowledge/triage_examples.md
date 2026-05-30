# Offshore Equipment Incident & Escalation Knowledge Base
# NL Offshore Production Platforms — Ground Truth Training Reference
# 1000 logged entries across 10 operational categories

This knowledge base contains labelled equipment telemetry examples to help the agent
ground its engineering escalation and emergency-stop (ESD) reasoning in consistent operational safety patterns.

---
## Category: Gas Leak
Total cases: 107 | Escalate: 21 | Routine: 86

### Escalation examples (safety_flag = 1)
**Case 13** | Platform: Terra Nova | Severity Level: 1
Telemetry: Pressure 172 PSI | Temp 65.0°C | Vibration 8.4 mm/s | Flow 49% | Voltage 385V | RPM 1330
Log Entry: High-pressure cementing unit — gas detection system triggered past 2 hours. Confirmed hydrocarbon leak at flange. Pressure 172 PSI. Shutdown valve closed. S. Newhook coordinating isolation.
Correct safety_flag: 1 — Severity Level 1

**Case 116** | Platform: Hebron | Severity Level: 1
Telemetry: Pressure 174 PSI | Temp 65.0°C | Vibration 7.9 mm/s | Flow 49% | Voltage 438V | RPM 1145
Log Entry: Minor gas release from Rotary table drive valve stem packing intermittently since 0800. LEL reading 8% at 1m distance. Work order raised for packing replacement. Area monitored continuously.
Correct safety_flag: 1 — Severity Level 1

**Case 205** | Platform: White Rose | Severity Level: 1
Telemetry: Pressure 195 PSI | Temp 72.1°C | Vibration 11.2 mm/s | Flow 40% | Voltage 410V | RPM 1290
Log Entry: Flash gas compressor skid — area hydrocarbon sniffing sensor reading 15% LEL. Localized venting identified on secondary instrument connection line. Enclosure exhaust operating normally.
Correct safety_flag: 1 — Severity Level 1

### Routine examples (safety_flag = 0)
**Case 7** | Platform: Hibernia | Severity Level: 4
Telemetry: Pressure 140 PSI | Temp 45.2°C | Vibration 3.1 mm/s | Flow 98% | Voltage 415V | RPM 1180
Log Entry: Preventative inspection of gas detection transmitters on Deck Level 2. Units re-calibrated using span gas bump. Minor drift logged on Sensor G-204 but remained within normal parameters.
Correct safety_flag: 0 — Severity Level 4

**Case 55** | Platform: Hebron | Severity Level: 5
Telemetry: Pressure 120 PSI | Temp 38.0°C | Vibration 2.1 mm/s | Flow 100% | Voltage 400V | RPM 1200
Log Entry: Routine packing inspection on main fuel gas line isolation block. No VOC or hydrocarbon traces detected via handheld optical gas imaging (OGI) camera.
Correct safety_flag: 0 — Severity Level 5

---
## Category: Structural Fatigue
Total cases: 115 | Escalate: 115 | Routine: 0

### Escalation examples (safety_flag = 1)
**Case 15** | Platform: White Rose | Severity Level: 3
Telemetry: Pressure 278 PSI | Temp 60.2°C | Vibration 23.7 mm/s | Flow 76% | Voltage 393V | RPM 1441
Log Entry: Drawworks motor — fatigue crack discovered during inspection, approx 40mm length at weld toe. Vibration 23.7 mm/s above threshold. Crack growth rate unknown. Engineering notified.
Correct safety_flag: 1 — Severity Level 3

**Case 21** | Platform: White Rose | Severity Level: 3
Telemetry: Pressure 348 PSI | Temp 54.5°C | Vibration 49.7 mm/s | Flow 60% | Voltage 417V | RPM 1431
Log Entry: Abnormal vibration on Choke manifold — reading 49.7 mm/s vs baseline of 4 mm/s since 0600. Resonance suspected. RPM reduced from rated. Structural team reviewing.
Correct safety_flag: 1 — Severity Level 3

**Case 22** | Platform: Terra Nova | Severity Level: 2
Telemetry: Pressure 410 PSI | Temp 85.3°C | Vibration 38.2 mm/s | Flow 55% | Voltage 420V | RPM 1500
Log Entry: Main deck piping support hanger structural weld found fractured entirely at Flare Line junction. Pipe movement observed during high-flow test sequence. Dynamic bracing required.
Correct safety_flag: 1 — Severity Level 2

### Routine examples (safety_flag = 0)
---
## Category: Mechanical Failure
Total cases: 130 | Escalate: 45 | Routine: 85

### Escalation examples (safety_flag = 1)
**Case 88** | Platform: Hebron | Severity Level: 2
Telemetry: Pressure 520 PSI | Temp 112.4°C | Vibration 18.2 mm/s | Flow 25% | Voltage 380V | RPM 850
Log Entry: High-pressure injection pump outboard bearing failure. High operating temperatures leading to internal scoring. Flow output dropped severely below command setpoint.
Correct safety_flag: 1 — Severity Level 2

### Routine examples (safety_flag = 0)
**Case 27** | Platform: Hibernia | Severity Level: 5
Telemetry: Pressure 310 PSI | Temp 55.4°C | Vibration 4.2 mm/s | Flow 92% | Voltage 4