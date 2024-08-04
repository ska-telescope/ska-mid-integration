import argparse
import ast
import os
from typing import Dict, List, Tuple, Optional
from datetime import datetime

# This script is used to generate markdown files from Python files containing test steps and scenarios.
# The script scans the Python files and extracts the test steps and scenarios using AST.
# It then generates a markdown file with the extracted information for each input file.
# Use the script as follows:
# python document_steps.py <input_folder> <output_folder>

import argparse
import ast
import os
import re
from typing import Dict, List, Tuple, Optional
from datetime import datetime


class MarkdownFormatter:
    """Class for managing the output and MD formatting."""

    @staticmethod
    def generate_markdown(filepath: str, steps: List[Dict], scenarios: Dict[str, str]) -> str:
        """Generate markdown content from steps and scenarios."""
        current_time = datetime.now().strftime("%d %B %Y %H:%M:%S")
        markdown = f"# Test Steps and Scenarios from {filepath}\n\n"
        markdown += f"Last updated on: {current_time}\n\n"

        if scenarios:
            markdown += "## Scenarios\n\n"
            for func_name, scenario_name in scenarios.items():
                markdown += f"- {scenario_name} (`{func_name}`)\n"
            markdown += "\n"

        if steps:
            markdown += "## Steps\n\n"
            for step in steps:
                markdown += f"### {step['type'].capitalize()}: {step['name']}\n\n"
                markdown += f"**Function:** `{step['function']}`\n\n"
                markdown += f"**Signature:**\n```python\n{step['signature']}\n```\n\n"
                markdown += f"**Description:**\n{step['docstring']}\n\n"
                markdown += "---\n\n"
        else:
            markdown += "No steps found in this file.\n"

        return markdown

    @staticmethod
    def write_markdown(content: str, output_file: str) -> None:
        """Write markdown content to a file."""
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as file:
            file.write(content)
        print(f"Markdown file '{output_file}' has been generated.")
        print(f"Last updated on: {datetime.now().strftime('%d %B %Y %H:%M:%S')}")

    @staticmethod
    def format_feature_file(content: str) -> str:
        """Format feature file content as Markdown."""
        markdown = "# Feature\n\n"
        lines = content.split('\n')
        in_scenario = False
        in_example = False
        example_table = []

        for line in lines:
            stripped_line = line.strip()
            if stripped_line.startswith('Feature:'):
                markdown += f"## {stripped_line}\n\n"
            elif stripped_line.startswith('Scenario:') or stripped_line.startswith('Scenario Outline:'):
                if in_example:
                    markdown += MarkdownFormatter._format_example_table(example_table)
                    example_table = []
                    in_example = False
                in_scenario = True
                markdown += f"### {stripped_line}\n\n"
            elif stripped_line.startswith('Given ') or stripped_line.startswith('When ') or stripped_line.startswith('Then ') or stripped_line.startswith('And ') or stripped_line.startswith('But '):
                markdown += f"- {stripped_line}\n"
            elif stripped_line.startswith('Examples:'):
                in_example = True
                markdown += f"#### {stripped_line}\n\n"
            elif in_example and '|' in stripped_line:
                example_table.append(stripped_line)
            elif stripped_line == '' and in_scenario:
                if in_example:
                    markdown += MarkdownFormatter._format_example_table(example_table)
                    example_table = []
                    in_example = False
                in_scenario = False
                markdown += "\n"
            else:
                markdown += f"{line}\n"

        # Handle case where file ends with an example table
        if example_table:
            markdown += MarkdownFormatter._format_example_table(example_table)

        return markdown

    @staticmethod
    def _format_example_table(table_lines: List[str]) -> str:
        """Format an example table in Markdown."""
        if not table_lines:
            return ""

        # Strip leading and trailing pipes and spaces
        cleaned_lines = [line.strip().strip('|').strip() for line in table_lines]

        # Split each line into cells
        table_data = [line.split('|') for line in cleaned_lines]

        # Strip spaces from each cell
        table_data = [[cell.strip() for cell in row] for row in table_data]

        # Find the maximum width for each column
        col_widths = [max(len(cell) for cell in col) for col in zip(*table_data)]

        # Generate the formatted table
        formatted_table = "| " + " | ".join(cell.ljust(width) for cell, width in zip(table_data[0], col_widths)) + " |\n"
        formatted_table += "| " + " | ".join("-" * width for width in col_widths) + " |\n"
        for row in table_data[1:]:
            formatted_table += "| " + " | ".join(cell.ljust(width) for cell, width in zip(row, col_widths)) + " |\n"

        return formatted_table + "\n"


class FileScanner:
    """Class to scan the file and extract steps and scenarios."""

    @staticmethod
    def parse_file(filename: str) -> Tuple[List[Dict], Dict[str, str]]:
        """Parse the given file and return steps and scenarios."""
        try:
            with open(filename, 'r') as file:
                content = file.read()
            tree = ast.parse(content)
            visitor = FileScanner.StepVisitor()
            visitor.visit(tree)
            return visitor.steps, visitor.scenarios
        except SyntaxError as e:
            print(f"SyntaxError in file {filename}: {str(e)}")
            return [], {}
        except Exception as e:
            print(f"Error parsing file {filename}: {str(e)}")
            return [], {}


    class StepVisitor(ast.NodeVisitor):
        """Visitor class to extract steps and scenarios from AST."""

        def __init__(self):
            self.steps = []
            self.scenarios = {}

        def visit_FunctionDef(self, node):
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name):
                    if decorator.func.id in ['given', 'when', 'then']:
                        self._process_step(node, decorator)
                    elif decorator.func.id == 'scenario':
                        self._process_scenario(node, decorator)

        def _process_step(self, node, decorator):
            step_type = decorator.func.id
            step_name = self._extract_step_name(decorator)
            if step_name is not None:
                self.steps.append({
                    'type': step_type,
                    'name': step_name,
                    'function': node.name,
                    'signature': self._get_signature(node),
                    'docstring': ast.get_docstring(node),
                })
            else:
                print(f"Warning: Could not extract step name for function {node.name}")

        def _extract_step_name(self, decorator) -> Optional[str]:
            if decorator.args:
                # If there are positional arguments
                if isinstance(decorator.args[0], ast.Str):
                    # If the argument is a simple string
                    return decorator.args[0].s
                elif isinstance(decorator.args[0], ast.Call):
                    # If the argument is a function call (like _)
                    if decorator.args[0].args:
                        if isinstance(decorator.args[0].args[0], ast.Str):
                            return decorator.args[0].args[0].s
            elif decorator.keywords:
                # If there are keyword arguments
                for keyword in decorator.keywords:
                    if keyword.arg in ['text', 'name']:
                        if isinstance(keyword.value, ast.Str):
                            return keyword.value.s
            return None

        def _process_scenario(self, node, decorator):
            scenario_name = self._extract_scenario_name(decorator)
            if scenario_name is not None:
                self.scenarios[node.name] = scenario_name
            else:
                print(f"Warning: Could not extract scenario name for function {node.name}")

        def _extract_scenario_name(self, decorator) -> Optional[str]:
            if len(decorator.args) >= 2:
                if isinstance(decorator.args[1], ast.Str):
                    return decorator.args[1].s
            for keyword in decorator.keywords:
                if keyword.arg == 'name' and isinstance(keyword.value, ast.Str):
                    return keyword.value.s
            return None

        @staticmethod
        def _get_signature(node):
            args = [arg.arg for arg in node.args.args]
            return f"def {node.name}({', '.join(args)}):"


class FolderProcessor:
    """Class to process a folder of Python and feature files."""

    @staticmethod
    def find_repository_root(path: str) -> str:
        """Find the root of the repository by looking for .git folder."""
        current_path = os.path.abspath(path)
        while current_path != '/':
            if os.path.exists(os.path.join(current_path, '.git')):
                return current_path
            current_path = os.path.dirname(current_path)
        return path  # If no .git folder found, return the original path

    @staticmethod
    def process_folder(input_folder: str, output_folder: str) -> None:
        """Process all Python and feature files in the given folder."""
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        repo_root = FolderProcessor.find_repository_root(input_folder)
        print(f"Repository root: {repo_root}")

        for root, _, files in os.walk(input_folder):
            for filename in files:
                input_path = os.path.join(root, filename)
                relative_path = os.path.relpath(input_path, repo_root)

                if filename.endswith('.py'):
                    # Place Python step files in the 'steps' subfolder
                    output_path = os.path.join(output_folder, 'steps', f"{os.path.splitext(relative_path)[0]}.md")
                    steps, scenarios = FileScanner.parse_file(input_path)

                    if steps or scenarios:
                        markdown_content = MarkdownFormatter.generate_markdown(relative_path, steps, scenarios)
                        MarkdownFormatter.write_markdown(markdown_content, output_path)
                        print(f"Processed Python file: {relative_path}")
                    else:
                        print(f"No steps or scenarios found in {relative_path}. Skipping.")

                elif filename.endswith('.feature'):
                    # Place feature files in the 'features' subfolder
                    output_path = os.path.join(output_folder, 'features', f"{os.path.splitext(relative_path)[0]}.md")
                    try:
                        with open(input_path, 'r') as feature_file:
                            feature_content = feature_file.read()
                        markdown_content = MarkdownFormatter.format_feature_file(feature_content)
                        MarkdownFormatter.write_markdown(markdown_content, output_path)
                        print(f"Processed feature file: {relative_path}")
                    except Exception as e:
                        print(f"Error processing feature file {relative_path}: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="Generate markdown from test steps and feature files in a folder.")
    parser.add_argument("input_folder", help="Path to the input folder containing Python and feature files")
    parser.add_argument("output_folder", help="Path to the output folder for markdown files")
    args = parser.parse_args()

    FolderProcessor.process_folder(args.input_folder, args.output_folder)


if __name__ == "__main__":
    main()