from datetime import date, datetime, timezone, timedelta
from uuid import uuid4
from zoneinfo import ZoneInfo

def _escape_ics(value: str) -> str:
	return (
		value.replace("\\", "\\\\")
		.replace("\n", "\\n")
		.replace(";", "\\;")
		.replace(",", "\\,")
	)


def _fold_ics_line(line: str) -> list[str]:
	folded: list[str] = []
	current = ""
	for character in line:
		if len((current + character).encode("utf-8")) > 75:
			folded.append(current)
			current = " "
		current += character
	folded.append(current)
	return folded



def _format_ics_datetime(value: str) -> tuple[str, str, date | datetime]:
    try:
        parsed_date = date.fromisoformat(value)
    except ValueError:
        parsed_date = None

    if parsed_date is not None:
        return ";VALUE=DATE", parsed_date.strftime("%Y%m%d"), parsed_date

    parsed_datetime = datetime.fromisoformat(value.replace("Z", "+00:00"))

    # Use Riga time if the datetime does not specify a timezone.
    if parsed_datetime.utcoffset() is None:
        parsed_datetime = parsed_datetime.replace(
            tzinfo=ZoneInfo("Europe/Riga")
        )

    utc_value = parsed_datetime.astimezone(timezone.utc)
    return "", utc_value.strftime("%Y%m%dT%H%M%SZ"), utc_value

def build_calendar(events: list[dict[str, str]]) -> bytes:
	"""Serialize dated plan events as a Google Calendar-compatible ICS file."""
	lines = [
		"BEGIN:VCALENDAR",
		"VERSION:2.0",
		"PRODID:-//SyllabusPilot//Study Plan//EN",
		"CALSCALE:GREGORIAN",
		"METHOD:PUBLISH",
	]

	for index, event in enumerate(events, start=1):
		summary = event.get("summary", "").strip()
		start = event.get("start", "").strip()
		end = event.get("end", "").strip()
		description = event.get("description", "").strip()
		if not summary or not start or not end:
			raise ValueError(f"Event {index} needs summary, start, and end")

		start_param, start_value, parsed_start = _format_ics_datetime(start)
		end_param, end_value, parsed_end = _format_ics_datetime(end)
		if bool(start_param) != bool(end_param):
			raise ValueError(f"Event {index} must use dates or datetimes for both ends")
		if parsed_end <= parsed_start:
			if start_param:
				parsed_end = parsed_start + timedelta(days=1)
				end_value = parsed_end.strftime("%Y%m%d")
			else:
				parsed_end = parsed_start + timedelta(hours=1)
				end_value = parsed_end.strftime("%Y%m%dT%H%M%SZ")
			description = (
				description + "\nDuration automatically adjusted; please verify."
			).strip()

		lines.extend(
			[
				"BEGIN:VEVENT",
				f"UID:{uuid4()}@syllabus-pilot",
				f"DTSTAMP:{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
				f"DTSTART{start_param}:{start_value}",
				f"DTEND{end_param}:{end_value}",
				f"SUMMARY:{_escape_ics(summary)}",
			]
		)
		if description:
			lines.append(f"DESCRIPTION:{_escape_ics(description)}")
		lines.append("END:VEVENT")

	lines.append("END:VCALENDAR")
	folded_lines = [part for line in lines for part in _fold_ics_line(line)]
	return ("\r\n".join(folded_lines) + "\r\n").encode("utf-8")
