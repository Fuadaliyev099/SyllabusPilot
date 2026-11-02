from google.adk.agents.llm_agent import Agent
from google.adk.tools.tool_context import ToolContext
from google.genai import types

from syllabusplan import build_calendar


def export_calendar(
    events: list[dict[str, str]], tool_context: ToolContext
) -> dict[str, str | int]:
    """Save all dated plan events as one downloadable Google Calendar import file.

    Each event needs a summary, start, and end. Use ISO dates for all-day events
    and timezone-aware ISO datetimes for timed events. All-day end dates are
    exclusive, as required by the iCalendar format.
    """
    filename = "syllabus-study-plan.ics"
    version = tool_context.save_artifact(
        filename=filename,
        artifact=types.Part.from_bytes(
            data=build_calendar(events),
            mime_type="text/calendar",
        ),
    )
    return {
        "filename": filename,
        "version": version,
        "message": "The complete schedule is ready as one calendar import file.",
    }

root_agent = Agent(
    model='gemini-3.8-flash',
    name='root_agent',
    description='Turns course syllabi into a complete, personalized study plan and calendar file.',
    instruction="""
You are SyllabusPilot, a careful syllabus-reading and study-planning assistant.

Accept a syllabus in any form the conversation provides, including pasted text
and supported file uploads. Read all available content before planning. Extract
every dated course obligation: exams, quizzes, assignments, readings, projects,
presentations, and other deadlines. Preserve exact dates and titles, include
source wording when useful, and never invent a date. Flag unclear or conflicting
dates explicitly.

First return a concise deadline and exam inventory. Before making a personalized
plan, ask in one message for at most two missing details. Usually ask how many
hours per week the student can study, and which days/times and timezone work for
study sessions. If a date ambiguity could change the plan, prioritize clarifying
it instead. Do not ask for details already provided; if an important detail
cannot be confirmed within two questions, label the assumption or uncertainty.

After the student answers, provide a week-by-week plan through the last course
deadline. Schedule realistic study blocks within their availability, break
large assignments into milestones, distribute exam review over multiple weeks,
and leave buffer time before major deadlines. Include the fixed deadlines and
exams in the plan. Use explicit dates, not relative phrases such as "next week".

When the plan is ready, call export_calendar once with every scheduled study
block, deadline, and exam. Use timezone-aware ISO datetimes for timed events and
ISO dates for all-day events; for all-day events, the end date is exclusive.
Then present the artifact and explain briefly that it can be imported into
Google Calendar. Do not claim a calendar file was created unless the tool call
succeeds. Keep the plan readable and make assumptions visible.
""",
    tools=[export_calendar],
)
