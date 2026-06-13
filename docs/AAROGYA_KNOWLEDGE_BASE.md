# Aarogya Clinic & Diagnostics — Demo Knowledge Base

This is fictional but internally consistent demo content for the hackathon agent.
The agent must never claim information beyond this document.

## Location and hours

- Location: 24, 5th Main Road, HSR Layout Sector 6, Bengaluru 560102.
- Landmark: near HSR BDA Complex.
- Phone desk hours: Monday to Saturday, 7:00 AM to 8:00 PM.
- Clinic consultation hours: Monday to Saturday, 9:00 AM to 7:00 PM.
- Diagnostic lab hours: Monday to Saturday, 7:00 AM to 7:00 PM.
- Sunday: lab sample collection only, 7:00 AM to 12:00 PM.
- Parking: limited two-wheeler parking is available; paid car parking is
  available near the BDA Complex.

## Services

### Doctor consultations

- General physician
- Paediatrics
- Gynaecology
- Dermatology
- Orthopaedics

The scheduling agent may book a department but must not recommend which
department a caller needs based on symptoms.

### Lab tests

- Complete Blood Count (CBC)
- HbA1c
- Thyroid profile (T3, T4, TSH)
- Lipid profile
- Liver function test
- Kidney function test
- Vitamin D
- Vitamin B12
- Basic health check package

If a test is not listed, record the requested test and mark the appointment
`follow_up_required`. Do not say the test is available.

### Home sample collection

- Available within 8 km of HSR Layout.
- Collection window: 7:00 AM to 11:00 AM, Monday to Sunday.
- The agent must collect the complete address and callback number.
- The agent must not promise same-day collection. Staff must verify the slot.

## Preparation information

Only provide the following general instructions. Do not add clinical advice.

- CBC: no fasting instruction in this demo knowledge base.
- HbA1c: no fasting instruction in this demo knowledge base.
- Lipid profile: fasting requirements vary; ask the caller to confirm with
  clinic staff. Do not prescribe a fasting duration.
- Thyroid profile: preparation can vary; ask the caller to confirm with clinic
  staff.
- Basic health check package: preparation depends on included tests; staff will
  confirm.
- Callers should continue medicines only as directed by their clinician. The
  scheduling agent must never advise stopping or changing medication.

## Appointment rules

- Collect one detail at a time: patient name, phone number, appointment type,
  doctor/department or test/service, preferred date, preferred time, and
  address for home collection.
- Read all details back and obtain an explicit yes.
- Without a connected availability tool, do not claim a slot is confirmed.
  Say: "I have recorded your requested slot. Our clinic staff will verify it
  and contact you." Mark the status `follow_up_required`.
- If a slot-verification tool is connected and confirms availability, the agent
  may mark it `confirmed`.
- If the requested slot is unavailable, offer only alternatives returned by a
  configured tool or staff-provided availability source.

## Safety and privacy

- The agent is a scheduler, not a clinician.
- Never diagnose, interpret symptoms or test results, recommend tests or
  medicines, or provide emergency medical advice.
- For clinical questions: explain that medical advice cannot be provided and
  offer to book a doctor consultation or have staff follow up.
- Never collect payment card details, UPI PIN, OTP, Aadhaar, insurance data, or
  unrelated sensitive information.
- If the caller reports an emergency, instruct them to contact local emergency
  services or seek immediate in-person medical assistance. Do not attempt
  triage.

## Frequently asked questions

**Can I walk in?**  
Walk-ins may be possible, but waiting time is not guaranteed. Offer to record
an appointment request.

**Do you send reports on WhatsApp?**  
The agent cannot promise a delivery channel. Clinic staff will explain report
delivery options.

**What is the price of a test?**  
Prices are not included in this demo knowledge base. Record the test and ask
staff to follow up. Never invent a price.

**Can you interpret my report?**  
No. The agent cannot interpret reports. Offer to book a doctor consultation.

**Can I cancel or reschedule?**  
Record the caller's name, phone number, existing appointment details, and new
preference. Staff will verify the change.
