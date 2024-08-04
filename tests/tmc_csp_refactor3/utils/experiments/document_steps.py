import argparse
import ast
from typing import Dict, List, Tuple
from datetime import datetime

class MarkdownFormatter:
    """Class for managing the output and MD formatting."""

    @staticmethod
    def generate_markdown(filename: str, steps: List[Dict], scenarios: Dict[str, str]) -> str:
        """Generate markdown content from steps and scenarios."""
        current_time = datetime.now().strftime("%d %B %Y %H:%M:%S")
        markdown = f"# Test Steps and Scenarios from {filename}\n\n"
        markdown += f"Last updated on: {current_time}\n\n"

        markdown += "## Scenarios\n\n"
        for func_name, scenario_name in scenarios.items():
            markdown += f"- {scenario_name} (`{func_name}`)\n"

        markdown += "\n## Steps\n\n"
        for step in steps:
            markdown += f"### {step['type'].capitalize()}: {step['name']}\n\n"
            markdown += f"**Function:** `{step['function']}`\n\n"
            markdown += f"**Signature:**\n```python\n{step['signature']}\n```\n\n"
            markdown += f"**Description:**\n{step['docstring']}\n\n"
            markdown += "---\n\n"
        return markdown

    @staticmethod
    def write_markdown(content: str, output_file: str) -> None:
        """Write markdown content to a file."""
        with open(output_file, 'w') as file:
            file.write(content)
        print(f"Markdown file '{output_file}' has been generated.")
        print(f"Last updated on: {datetime.now().strftime('%d %B %Y %H:%M:%S')}")

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
            step_name = ast.literal_eval(decorator.args[0].args[0])
            self.steps.append({
                'type': step_type,
                'name': step_name,
                'function': node.name,
                'signature': self._get_signature(node),
                'docstring': ast.get_docstring(node),
                'scenarios': []  # This will be filled later if needed
            })

        def _process_scenario(self, node, decorator):
            scenario_name = ast.literal_eval(decorator.args[1])
            self.scenarios[node.name] = scenario_name

        @staticmethod
        def _get_signature(node):
            args = [arg.arg for arg in node.args.args]
            return f"def {node.name}({', '.join(args)}):"

def main():
    parser = argparse.ArgumentParser(description="Generate markdown from test steps file.")
    parser.add_argument("input_file", help="Path to the input test steps file")
    parser.add_argument("output_file", help="Path to the output markdown file")
    args = parser.parse_args()

    steps, scenarios = FileScanner.parse_file(args.input_file)
    markdown_content = MarkdownFormatter.generate_markdown(args.input_file, steps, scenarios)
    MarkdownFormatter.write_markdown(markdown_content, args.output_file)

if __name__ == "__main__":
    main()