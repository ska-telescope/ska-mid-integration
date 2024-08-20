"""Publish HTML BDD test report to JIRA Test Execution issue."""

import logging
import os

import requests

CI_JOB_URL = os.getenv("CI_JOB_URL")
JIRA_URL = os.getenv("JIRA_URL")
JIRA_AUTH = os.getenv("JIRA_AUTH")
PROJECT_KEY = "XTP"


def auth_header() -> dict:
    """Return the authorization header for JIRA API."""
    return {"Authorization": f"Basic {JIRA_AUTH}"}


def print_env_vars() -> str:
    """Print the environment variables for debugging."""
    msg = f"CI_JOB_URL: {CI_JOB_URL}, JIRA_URL: {JIRA_URL}, "
    msg += f'JIRA_AUTH: {"[something]" if JIRA_AUTH else "[None]"}, '
    msg += f"PROJECT_KEY: {PROJECT_KEY}"
    return msg


def search_jira_execution_issue() -> list[dict]:
    """Search for the Jira issue that corresponds to the current CI job."""
    if not CI_JOB_URL or not JIRA_URL or not JIRA_AUTH or not PROJECT_KEY:
        raise ValueError("Missing environment variables: " + print_env_vars())

    query = (
        f'project = "{PROJECT_KEY}" '
        'AND issuetype = "Test Execution" '
        f'AND description ~ "{CI_JOB_URL}"'
    )

    search_api_path = "/rest/api/2/search"
    search_api_url = f"{JIRA_URL}{search_api_path}"

    logging.info(
        "Searching a JIRA ticket containing the CI job URL: %s", CI_JOB_URL
    )

    # Perform the search
    response = requests.get(
        search_api_url, headers=auth_header(), params={"jql": query}
    )

    # Check the response status
    if response.status_code != 200:
        msg = "Failed to search JIRA tickets. "
        msg += f"Status code: {response.status_code}. "
        msg += f"Response:\n{response.text}"
        logging.error(msg)
        return []

    return response.json().get("issues", [])


def get_new_text_with_report_links() -> str:
    """Return the new text to append to the JIRA issue description.

    The new text contains:
    - a link to the HTML execution report
    """
    new_text = "\n\nHTML BDD execution report: "
    new_text += CI_JOB_URL + "/artifacts/browse/build/report.html"
    new_text += "\n\n"
    return new_text


def append_text_to_issue_description(issue, new_text) -> None:
    """Update the JIRA issue with the test report."""
    issue_ticket = issue["key"]

    update_api_path = f"/rest/api/2/issue/{issue_ticket}"
    update_api_url = f"{JIRA_URL}{update_api_path}"

    update_payload = {
        "fields": {
            "description": issue["fields"]["description"] + new_text,
        }
    }

    logging.info(
        "Updating JIRA ticket %s description with links to generated reports",
        issue_ticket,
    )

    response = requests.put(
        update_api_url, headers=auth_header(), json=update_payload
    )

    if response.status_code == 204:
        logging.info("Updated successfully %s", issue_ticket)
    else:
        msg = "Failed to update JIRA ticket:\n"
        msg += f"status code: {response.status_code}\n"
        msg += f"URL: {update_api_url}\n"
        msg += f"Payload: {update_payload}\n"
        msg += f"Response: {response.text}\n"
        logging.error(msg)


def print_issues_links(issues):
    """Print the links to the JIRA issues."""
    issues_msg = "This job is related to the following JIRA issues:"
    for issue in issues:
        issues_msg += f"\n- {JIRA_URL}/browse/{issue['key']}"
    logging.info(issues_msg)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    issues = search_jira_execution_issue()

    if not issues:
        logging.error(
            "No JIRA Test Execution issue found for this CI job. "
            "We cannot publish the further test reports to JIRA."
        )

    print_issues_links(issues)

    if len(issues) > 1:
        logging.warning(
            "Found multiple JIRA Test Execution issues "
            "referring to this CI job. We will update just the first one."
        )

    append_text_to_issue_description(
        issues[0], get_new_text_with_report_links()
    )
