

import logging
import os

import requests

CI_JOB_URL = os.getenv('CI_JOB_URL')
JIRA_URL = os.getenv('JIRA_URL')
JIRA_AUTH = os.getenv('JIRA_AUTH')
PROJECT_KEY = "XTP"

def print_env_vars() -> str:
    return (
        f'CI_JOB_URL: {CI_JOB_URL}, JIRA_URL: {JIRA_URL},
          JIRA_AUTH: {JIRA_AUTH}, PROJECT_KEY: {PROJECT_KEY}'
        )


def search_jira_execution_issue() -> str:
    """Search for the Jira issue that corresponds to the current CI job."""
    if not CI_JOB_URL or not JIRA_URL or not JIRA_AUTH or not PROJECT_KEY:
        raise ValueError(
            'Missing environment variables: '
            + print_env_vars()
        )
    
    query = (
            f'project = "{PROJECT_KEY}" '
            'AND issuetype = "TestExecution" '
            f'AND description ~ "{CI_JOB_URL}"'
        )
    
    headers = {"Authorization": f"Basic {JIRA_AUTH}"}

    
    search_api_path = '/rest/api/3/search'
    search_api_url = f'{JIRA_URL}{search_api_path}'

    # Perform the search
    response = requests.get(
        search_api_url,
        headers=headers,
        params={'jql': query}
    )

    # Check the response status
    if response.status_code == 200:
        issues = response.json().get('issues', [])
        if issues:
            for issue in issues:
                msg = f'Found Test Execution Ticket: {issue["key"]}'
                msg += f'Summary: {issue["fields"]["summary"]}'
                msg += f'Description: {issue["fields"]["description"]}'
                msg += f'URL: {JIRA_URL}/browse/{issue["key"]}'
                logging.info(msg)
        else:
            logging.warning("No matching test execution tickets found.")
    else:
        msg = f'Failed to search JIRA tickets, status code: {response.status_code}'
        msg += f'URL: {search_api_url}'
        msg += f'Query: {query}'
        msg += f'Response: {response.text}'
        logging.error(msg)

    return issues


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    search_jira_execution_issue()



    



    

    

