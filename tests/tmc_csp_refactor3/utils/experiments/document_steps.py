import argparse
import ast
import os
from typing import Dict, List, Tuple, Optional
from datetime import datetime


class MarkdownFormatter:
    """Class for managing the output and MD formatting."""

    @staticmethod
    def generate_markdown(filename: str, steps: List[Dict], scenarios: Dict[str, str]) -> str:
        """Generate markdown content from steps and scenarios."""
        current_time = datetime.now().strftime("%d %B %Y %H:%M:%S")
        markdown = f"# Test Steps and Scenarios from {filename}\n\n"
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
        with open(output_file, 'w') as file:
            file.write(content)
        print(f"Markdown file '{output_file}' has been generated.")
        # print(f"Last updated on: {datetime.now().strftime('%d %B %Y %H:%M:%S')}")


class FileScanner:
    """Class to scan the file and extract steps and scenarios."""


    @staticmethod
    def parse_file(filename: str) -> Tuple[List[Dict], Dict[str, str]]:
        """Parse the given file and return steps and scenarios."""
        with open(filename, 'r') as file:
            tree = ast.parse(file.read())

        visitor = FileScanner.StepVisitor()
        visitor.visit(tree)
        return visitor.steps, visitor.scenarios

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
    """Class to process a folder of Python files."""

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
        """Process all Python files in the given folder."""
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        repo_root = FolderProcessor.find_repository_root(input_folder)
        print(f"Repository root: {repo_root}")

        for filename in os.listdir(input_folder):
            if filename.endswith('.py'):
                input_path = os.path.join(input_folder, filename)
                relative_path = os.path.relpath(input_path, repo_root)
                output_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}.md")
                steps, scenarios = FileScanner.parse_file(input_path)

                if steps or scenarios:
                    markdown_content = MarkdownFormatter.generate_markdown(relative_path, steps, scenarios)
                    MarkdownFormatter.write_markdown(markdown_content, output_path)
                    print(f"Processed: {relative_path}")
                else:
                    print(f"No steps or scenarios found in {relative_path}. Skipping.")



def main():
    parser = argparse.ArgumentParser(description="Generate markdown from test steps files in a folder.")
    parser.add_argument("input_folder", help="Path to the input folder containing Python files")
    parser.add_argument("output_folder", help="Path to the output folder for markdown files")
    args = parser.parse_args()

    FolderProcessor.process_folder(args.input_folder, args.output_folder)


if __name__ == "__main__":
    main()