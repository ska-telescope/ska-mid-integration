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
        'AND issuetype = "TestExecution" '
        f'AND description ~ "{CI_JOB_URL}"'
    )

    search_api_path = "/rest/api/2/search"
    search_api_url = f"{JIRA_URL}{search_api_path}"

    # Perform the search
    response = requests.get(
        search_api_url, headers=auth_header(), params={"jql": query}
    )

    # Check the response status
    if response.status_code == 200:
        issues = response.json().get("issues", [])
        if issues:
            for issue in issues:
                msg = f'Found Test Execution Ticket: {issue["key"]}.\n'
                msg += f'Summary: {issue["fields"]["summary"]}\n'
                msg += f'Description: {issue["fields"]["description"]}\n'
                msg += f'URL: {JIRA_URL}/browse/{issue["key"]}\n'
                logging.info(msg)
        else:
            logging.warning("No matching test execution tickets found.")
    else:
        msg = "Failed to search JIRA tickets:\n"
        msg += f"status code: {response.status_code}\n"
        msg += f"URL: {search_api_url}\n"
        msg += f"Query: {query}\n"
        msg += f"Response: {response.text}\n"
        logging.error(msg)

    return issues


def publish_test_report_on_issue(issue) -> None:
    """Update the JIRA issue with the test report."""
    issue_ticket = issue["key"]

    update_api_path = f"/rest/api/2/issue/{issue_ticket}"
    update_api_url = f"{JIRA_URL}{update_api_path}"

    new_description = issue["fields"]["description"]
    new_description += f"Hello world! This is a test update for {issue_ticket}"

    update_payload = {
        "fields": {
            "description": new_description,
        }
    }

    response = requests.put(
        update_api_url, headers=auth_header(), json=update_payload
    )

    if response.status_code == 204:
        logging.info(f"Updated description for {issue_ticket}")
    else:
        msg = "Failed to update JIRA ticket:\n"
        msg += f"status code: {response.status_code}\n"
        msg += f"URL: {update_api_url}\n"
        msg += f"Payload: {update_payload}\n"
        msg += f"Response: {response.text}\n"
        logging.error(msg)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    search_jira_execution_issue()
