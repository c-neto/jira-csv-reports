# NOTE:
# It was tested the [python-jira](https://github.com/pycontribs/jira) library, but does not found
# advantages that justify this third party module. Included, the python-jira are limited in the
# Jira Rest Endpoint in the '/cloud/jira/platform/rest/v2/...', when already exists
# '/cloud/jira/platform/rest/v3/...' endpoints.


import requests
from pydantic import BaseModel
from requests.auth import HTTPBasicAuth


class JQLFilter(BaseModel):
    name: str
    jql: str


class JiraAPI:
    def __init__(self, email: str, auth_token: str, domain: str):
        self.domain = domain
        self.auth_token = HTTPBasicAuth(email, auth_token)

    def get_filter_id(self, filter_name: str) -> str:
        """get filter id by name.
        more details:
            - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-filters/#api-rest-api-3-filter-search-get
        """
        url = f"{self.domain}/rest/api/3/filter/search"
        query_param = {"filterName": filter_name}

        response = requests.get(url, auth=self.auth_token, timeout=60, params=query_param)
        response.raise_for_status()
        response_json = response.json()

        filter_id = None

        for filter_object in response_json["values"]:
            if filter_object["name"] == filter_name:
                filter_id = filter_object["id"]

        return filter_id

    def update_filter_jql(self, filter_id: str, filter_jql: str):
        """
        more details:
            - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-filters/#api-rest-api-3-filter-id-put
        """
        url = f"{self.domain}/rest/api/3/filter/{filter_id}"
        payload = {"jql": filter_jql}

        response = requests.put(url, auth=self.auth_token, timeout=60, json=payload)
        response.raise_for_status()

    def create_filter_jql(self, filter_name: str, filter_jql: str):
        """
        more details:
            - https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-filters/#api-rest-api-3-filter-post
        """
        url = f"{self.domain}/rest/api/3/filter"
        payload = {"name": filter_name, "jql": filter_jql}

        response = requests.post(url, auth=self.auth_token, timeout=60, json=payload)
        response.raise_for_status()


class JiraHelper:
    @staticmethod
    def upsert_filters(jira_api: JiraAPI, jql_filter: JQLFilter):
        filter_id = jira_api.get_filter_id(jql_filter.name)

        jql_filter_doesnt_exists = not filter_id

        if jql_filter_doesnt_exists:
            print(f"creating filter | {jql_filter}")
            jira_api.create_filter_jql(jql_filter.name, jql_filter.jql)
        else:
            print(f"updating filter | {jql_filter}")
            jira_api.update_filter_jql(filter_id, jql_filter.jql)
