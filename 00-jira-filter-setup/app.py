from settings import settings
import jira


def main():
    jira_api = jira.JiraAPI(**settings["jira"])

    jira_filters = []

    for jql_filter in settings["jql_filters"]:
        jql_filter_name = jql_filter["jql_filter_name"]

        jql_template: str = jql_filter["jql_template"]
        jql = jql_template.format(sprint_id=settings["sprint_id"])

        jira_filter = jira.JQLFilter(
            name=jql_filter_name,
            jql=jql
        )

        jira_filters.append(jira_filter)

    for jira_filter in jira_filters:
        jira.JiraHelper.upsert_filters(jira_api, jira_filter)


if __name__ == "__main__":
    main()
