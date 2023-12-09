# NOTE:
# It was tested the [python-jira](https://github.com/pycontribs/jira) library, but does not found
# advantages that justify this third party module. Included, the python-jira are limited in the
# Jira Rest Endpoint in the '/cloud/jira/platform/rest/v2/...', when already exists
# '/cloud/jira/platform/rest/v3/...' endpoints.


from concurrent.futures import ThreadPoolExecutor
import requests
from pydantic import BaseModel
from requests.auth import HTTPBasicAuth


class SprintReportArtifact(BaseModel):
    sprint: str
    issues_planned: list[dict]
    issues_unplanned: list[dict]


class JQLStatements(BaseModel):
    issues_planned: str
    issues_unplanned: str


class JiraAPI:
    def __init__(self, email: str, auth_token: str, domain: str):
        self.domain = domain
        self.auth_token = HTTPBasicAuth(email, auth_token)

    def run_jql(self, jql_query: str, hard_limit=200, timeout_sec=60) -> list[dict]:
        """
        more details: https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-search/#api-rest-api-3-search-get
        """
        url = f"{self.domain}/rest/api/3/search"
        issues = []

        for start_at in range(0, hard_limit, 100):
            query_param = {"jql": jql_query, "maxResults": 100, "startAt": start_at}

            response = requests.get(
                url, auth=self.auth_token, timeout=timeout_sec, params=query_param
            )

            response.raise_for_status()
            response_json = response.json()

            issues.extend(response_json["issues"])

        return issues


def get_sprint_issues(jira_api: JiraAPI, jql_sprint_filters: JQLStatements, sprint_id: str) -> SprintReportArtifact:
    with ThreadPoolExecutor() as executor:
        thread_planned_issues = executor.submit(jira_api.run_jql, jql_sprint_filters.issues_planned)
        thread_unplanned_issues = executor.submit(jira_api.run_jql, jql_sprint_filters.issues_unplanned)

        sprint_report_artifact = SprintReportArtifact(
            sprint=sprint_id,
            issues_planned=thread_planned_issues.result(),
            issues_unplanned=thread_unplanned_issues.result(),
        )

    return sprint_report_artifact
