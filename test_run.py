from syllabusplan import build_calendar

# Test üçün nümunə tapşırıqlar və imtahanlar
events = [
    {
        "summary": "Midterm Exam (30%)",
        "start": "2026-11-18",
        "end": "2026-11-19"
    },
    {
        "summary": "Essay Due (20%)",
        "start": "2026-12-02",
        "end": "2026-12-03"
    }
]

# Təqvim faylını yaradırıq
ics_data = build_calendar(events)
with open("plan.ics", "wb") as f:
    f.write(ics_data)

print("Uğurludur! plan.ics faylı yaradıldı.")
