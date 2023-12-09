from pathlib import Path
from settings import settings
import extract


def create_report_raw(sprint_issues_report_artifact: extract.SprintReportArtifact, report_raw_path: Path):
    report_raw_path.parent.mkdir(parents=True, exist_ok=True)
    report_raw_path.write_text(sprint_issues_report_artifact.model_dump_json())
    print(f">>> report created: {report_raw_path.absolute()}")


def get_sprint_issues() -> extract.SprintReportArtifact:
    jira_api = extract.JiraAPI(**settings["jira"])
    jql_statements = extract.JQLStatements(**settings["jql_statements"])

    print("getting issues in the Jira API... (15 seconds around to be completed)")
    sprint_report_artifact = extract.get_sprint_issues(jira_api, jql_statements, settings["sprint_id"])

    return sprint_report_artifact


def main():
    sprint_report_artifact = get_sprint_issues()
    report_raw_path = Path(settings["reports_directory"], sprint_report_artifact.sprint, "report-raw.json")
    create_report_raw(sprint_report_artifact, report_raw_path)


if __name__ == "__main__":
    main()
