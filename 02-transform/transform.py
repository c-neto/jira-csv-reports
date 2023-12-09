from pydantic import BaseModel
import pydash as py_
from settings import settings


UNDEFINED_FIELD_VALUE = "UNDEFINED"


class ReportRaw(BaseModel):
    sprint: str
    issues_planned: list[dict]
    issues_unplanned: list[dict]


class ReportProcessedRow(BaseModel):
    sprint: str
    area: str | None
    assignee_email: str | None
    assignee_name: str | None
    epic_link_summary: str | None
    is_planned: bool
    issue_key: str
    issue_type: str
    priority: str | None
    sprint_count: int
    status_category: str | None
    status: str | None
    summary: str | None
    team: str | None
    time_original_estimate: float | None
    time_spent: float | None


def _jira_time_convert(time_in_seconds: int | None) -> float:
    if not time_in_seconds:
        return 0

    time_in_minutes = time_in_seconds / 60
    time_in_hours = time_in_minutes / 60
    # day_work = hours / 8

    time_in_hours_rounded = round(time_in_hours, 2)

    return time_in_hours_rounded


# WARNING: Jira API is bizarre...
#
# Don't trust in 'fields.status.statusCategory.name' to get the status category.
# The values will be not matches with Jira Sprint Insights.

# The "Scheduled" Issue Status is on "In progress" category
#
# >>> issue["fields"]["status"]
# {
#     "name": "Scheduled",
#     "statusCategory": {
#         "name": "In Progress"
#     }
# }
def get_status_category(issue: dict) -> str:
    done = "done"
    doing = "doing"
    todo = "todo"
    undefined = UNDEFINED_FIELD_VALUE

    status_name_to_category = {
        "reopened": todo,
        "scheduled": todo,
        "new": todo,
        "backlog": todo,
        "assigned": todo,
        "triggered": todo,

        "in progress": doing,
        "acknowledge": doing,
        "canceled": doing,
        "to deploy": doing,
        "on hold": doing,
        "deploy in progress": doing,

        "closed": done,
        "resolved": done,
    }

    status_name = py_.get(issue, "fields.status.name")
    status_name_lower = py_.lower_case(status_name)

    status_category_name = status_name_to_category.get(status_name_lower, undefined)

    return status_category_name


def get_assignee_email(issue: dict):
    assignee_email = py_.get(issue, "fields.assignee.emailAddress")

    if assignee_email is None:
        return UNDEFINED_FIELD_VALUE

    return assignee_email


def get_assignee_name(issue: dict):
    # assignee_name = py_.get(issue, "fields.assignee.displayName")

    assignee_email = py_.get(issue, "fields.assignee.emailAddress")

    if assignee_email is None:
        return UNDEFINED_FIELD_VALUE

    name_surname, *_ = assignee_email.split("@")
    name, surname, *_ = name_surname.split(".")

    assignee_name = f"{name} {surname}".title()

    return assignee_name


def get_area(issue: dict, issue_custom_field_area: str):
    issue_area = py_.get(issue, issue_custom_field_area)

    if issue_area is None:
        return UNDEFINED_FIELD_VALUE

    issue_area = py_.lower_case(issue_area)

    return issue_area


def get_epic_link_summary(issue: dict):
    epic_name = py_.get(issue, "fields.parent.fields.summary")

    return epic_name


def get_team(issue: dict, issue_custom_field_team: str):
    issue_team = py_.get(issue, issue_custom_field_team)

    if issue_team is None:
        return UNDEFINED_FIELD_VALUE

    issue_team = py_.lower_case(issue_team)

    issue_team = py_.lower_case(issue_team)

    return issue_team


def get_issue_key(issue: dict):
    key = issue["key"]
    return key


def get_issue_type(issue: dict):
    issue_type = py_.get(issue, "fields.issuetype.name")
    issue_type = py_.lower_case(issue_type)

    return issue_type


def get_time_original_estimate(issue: dict):
    originalestimate = py_.get(issue, "fields.timeoriginalestimate")
    hours_time_original_estimate = _jira_time_convert(originalestimate)

    return hours_time_original_estimate


def get_priority(issue: dict):
    priority = py_.get(issue, "fields.priority.name")
    priority = py_.lower_case(priority)
    return priority


def get_status(issue: dict):
    issues_status = py_.get(issue, "fields.status.name")
    issue_type = py_.lower_case(issues_status)

    return issue_type


def get_summary(issue: dict):
    summary = py_.get(issue, "fields.summary")
    summary = py_.lower_case(summary)
    return summary


def get_time_spent(issue: dict):
    timespent = py_.get(issue, "fields.timespent")
    hours_time_spent = _jira_time_convert(timespent)

    return hours_time_spent


def get_sprint_count(issue: dict, custom_field: str):
    sprints = py_.get(issue, custom_field)
    sprints_count = len(sprints)
    return sprints_count


def _make_processed_report_row(issue: dict, is_planned: bool, sprint: str):
    assignee_email = get_assignee_email(issue)
    assignee_name = get_assignee_name(issue)
    area = get_area(issue, settings["issue_custom_field"]["area"]["api_path"])
    epic_link_summary = get_epic_link_summary(issue)
    team = get_team(issue, settings["issue_custom_field"]["team"]["api_path"])
    issue_key = get_issue_key(issue)
    issue_type = get_issue_type(issue)
    time_original_estimate = get_time_original_estimate(issue)
    priority = get_priority(issue)
    status = get_status(issue)
    status_category = get_status_category(issue)
    summary = get_summary(issue)
    time_spent = get_time_spent(issue)
    sprint_count = get_sprint_count(issue, settings["issue_custom_field"]["sprints"]["api_path"])

    issue_row = ReportProcessedRow(
        assignee_email=assignee_email,
        assignee_name=assignee_name,
        area=area,
        team=team,
        epic_link_summary=epic_link_summary,
        issue_key=issue_key,
        issue_type=issue_type,
        time_original_estimate=time_original_estimate,
        priority=priority,
        status=status,
        status_category=status_category,
        sprint=sprint,
        summary=summary,
        time_spent=time_spent,
        is_planned=is_planned,
        sprint_count=sprint_count
    )

    return issue_row


def process_report(raw_report: ReportRaw) -> list[ReportProcessedRow]:
    issues_rows = []

    for issue in raw_report.issues_planned:
        issue = _make_processed_report_row(issue=issue, is_planned=True, sprint=raw_report.sprint)
        issues_rows.append(issue)

    for issue in raw_report.issues_unplanned:
        issue = _make_processed_report_row(issue=issue, is_planned=False, sprint=raw_report.sprint)
        issues_rows.append(issue)

    return issues_rows
