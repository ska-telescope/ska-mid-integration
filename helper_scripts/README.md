# Helper scripts

This directory contains a collection of helper scripts that can be used
to automate certain test-related tasks.

Currently, the following scripts are available:

1. `document_steps.py` - this script can be used to automatically generate
   a markdown documentation to document a set of tests. The script,
   essentially, reads both the (Gherkin) definition of the features and the
   scenarios and the actual implementation of the steps and generates a
   documentation starting from definitions, method signatures and
   docstrings. Differently from the simple sphinx documentation, this includes
   the Gherkin definitions too, and in general structures the output in a way
   which is more suitable for a test documentation.

2. `publish_test_report.py` - this script is an utility that takes the
   HTML BDD test report (generated through the plugin and
   [pytest-bdd-report](https://github.com/mattiamonti/pytest-bdd-report))
   and (optionally) a link to the most updated test documentation and publishes
   them as a link in the JIRA XRAY ticket that is associated with the
   current CI JOB.

The first script, for now, is designed to be used manually to occasionally
update the test documentation. The second script instead is designed to be
used in a CI/CD pipeline to automatically update the JIRA ticket with the
latest test report.

> **IMPORTANT NOTE**: at the current state, those two script are more a
> proof-of-concept than a production-ready tool. Neither their design, nor
> their implementation, nor their actual usage, nor their location in this
> repository are final. They are here prevalently to show how through a
> set of scripts and plugin you can enhance the test documentation
> and the test report publication. Things may change in PI24 and/or in the
> followings. If you have any feedback, questions, ideas, or you want to
> contribute, please contact Emanuele Lena and Giorgio Brajnik.

## 1. Document Steps

### Overview

The Test Documentation Generator is a Python script designed to automatically generate markdown documentation from Python test files and Gherkin feature files. It's particularly useful for projects using Behaviour Driven Development (BDD) methodologies.

### Installation

To use the Test Documentation Generator, you need Python 3.6 or higher. Clone the repository and install the required dependencies:

```bash
git clone https://github.com/your-repo/test-documentation-generator.git
cd test-documentation-generator
pip install -r requirements.txt
```

### Usage

Run the script from the command line, providing the input folder containing your Python and feature files, and the desired output folder for the markdown files:

```bash
python document_steps.py <input_folder> <output_folder>
```

For example:

```bash
python document_steps.py ../../tests out/
```

This will process all Python (.py) and feature (.feature) files in the input
folder and its subfolders, generating corresponding markdown
files in the output folder.

### Key Components

- `FileScanner`: This class is responsible for parsing Python files to extract
  test steps and scenarios. It uses the `ast` module to analyse the 
  abstract syntax tree of Python files.
- `MarkdownFormatter`: This class handles the generation of markdown content.
  It formats the extracted steps and scenarios into a readable markdown
  structure.
- `FolderProcessor`: This class orchestrates the entire process. It walks
  through the input folder, identifies relevant files, and coordinates the
  parsing and markdown generation for each file.
- `PostProcessor`: This class creates an index file that provides links to all
   generated markdown files, preserving the folder structure of the original
   files.

### File Handling

The script handles two types of files:

1. **Python Files (.py)**: These are parsed to extract test steps
  (decorated with `@given`, `@when`, `@then`) and scenarios
  (decorated with `@scenario`).

2. **Feature Files (.feature)**: These Gherkin syntax files are converted
   directly to markdown, preserving their structure and formatting.

### Output Structure

The generated documentation follows this structure:

```
out/
├── features/
│   └── [Feature files converted to markdown]
├── steps/
│   └── [Python files converted to markdown]
└── index.md
```

The `index.md` file provides a navigable structure of
all generated documentation.

### Customization

You can customize the script's behaviour by modifying the following classes:

- `StepVisitor`: Adjust how steps and scenarios are extracted from Python files.
- `MarkdownFormatter`: Modify the markdown formatting for different elements.
- `FolderProcessor`: Change how files are processed or add support for new
  file types.

### Limitations

- The script assumes a specific structure for test files and may
  need adjustments for different project structures.
- It does not verify the correctness of the test implementations,
  only extracts and documents them.


## 2. Publish Test Report

### Overview:
This script is designed to automate the process of publishing an
HTML BDD test report to a JIRA Test Execution issue. It is primarily
used in CI/CD pipelines and works by updating the description of
the relevant JIRA issue with a link to the HTML BDD test report.

### Key Features:
- Publishes an HTML BDD test report link to a JIRA Test Execution issue.
- Looks up the JIRA issue associated with the current CI job and updates
  its description.
- Handles authentication and communication with JIRA via its API.
- Provides options to include additional documentation links in the JIRA
  issue description.

### Expected Inputs:
- **Environment variables:**
  - `CI_JOB_URL`: URL of the current CI job.
  - `JIRA_URL`: URL of the JIRA instance.
  - `JIRA_AUTH`: Authentication token for JIRA API.
  - `HTML_REPORT_TARGET_FILE`: Path to the HTML test report
    (defaults to `build/report.html`).
  - `TEST_DOCS_LINK`: Optional link to additional test documentation
    (defaults to `None` and if not provided, it is not included in
    the JIRA issue description).

- **JIRA Project Key:** Hardcoded to `PROJECT_KEY = "XTP"`.

### Key Functionalities:

1. **Environment Variables Check:**
   The script verifies the presence of required environment variables
   (`CI_JOB_URL`, `JIRA_URL`, `JIRA_AUTH`).

2. **Generate Report Link:**
   The script builds the URL for the HTML BDD test report based on the
   `CI_JOB_URL` and `HTML_REPORT_TARGET_FILE`.

3. **Search for JIRA Issue:**
   Using the `CI_JOB_URL`, the script searches JIRA for the corresponding
   Test Execution issue in project `XTP`.

4. **Update JIRA Issue Description:**
   It appends the link to the HTML test report (and optionally the test
   documentation) to the description of the JIRA issue.

### Program Flow:

1. **Environment Validation:**
   The script checks if all required environment variables are available,
   raising an exception if not.
   
2. **Search for the JIRA Issue:**
   A search query is constructed to find a JIRA Test Execution issue that
   matches the `CI_JOB_URL`. If no issue is found, the script stops
   with an error.

3. **Update JIRA Issue:**
   Once the relevant JIRA issue is identified, the script updates the issue
   description by appending a link to the test report. 
   If multiple issues are found, it logs a warning and only
   updates the first one.

### Dependencies:
- Python standard libraries: `os`, `logging`.
- Third-party library: `requests` (for interacting with the JIRA API).

### Exception Handling:
- Raises `ValueError` if any required environment variables are missing.
- Raises `RuntimeError` if any step of interacting with the JIRA API fails.

### Example Use Case:
Run this script in a CI job after generating a test report with
`pytest` and `pytest-bdd-report`. The script will automatically search
for the relevant JIRA issue and update it with the test report link.

### Limitations:

- The test report's file accessibility check is currently deactivated
due to permission issues (HTTP 403 status code).
- Currently the script is very rigid in its structure and in its
  behaviour. It is designed to work in a specific context and may
  require modifications to be used in different environments.


