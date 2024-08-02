import ast,os
import re

# run this script as
# cd <folder of this script>
# python3 document_steps.py

# TODO this is just an experiment, not a final solution
# it needs to be engineered properly and made more parametric


class StepVisitor(ast.NodeVisitor):
    def __init__(self):
        self.steps = []
        self.scenarios = {}

    def visit_FunctionDef(self, node):
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name):
                if decorator.func.id in ['given', 'when', 'then']:
                    step_type = decorator.func.id
                    step_name = ast.literal_eval(decorator.args[0].args[0])
                    self.steps.append({
                        'type': step_type,
                        'name': step_name,
                        'function': node.name,
                        'signature': self.get_signature(node),
                        'docstring': ast.get_docstring(node),
                        'scenarios': []  # This will be filled later
                    })
                elif decorator.func.id == 'scenario':
                    scenario_name = ast.literal_eval(decorator.args[1])
                    self.scenarios[node.name] = scenario_name

    def get_signature(self, node):
        args = [arg.arg for arg in node.args.args]
        return f"def {node.name}({', '.join(args)}):"

def parse_file(filename):
    with open(filename, 'r') as file:
        tree = ast.parse(file.read())

    visitor = StepVisitor()
    visitor.visit(tree)
    return visitor.steps, visitor.scenarios

def generate_markdown(filename, steps, scenarios):
    markdown = f"# Test Steps and Scenarios from {filename}\n\n"

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


# Parse the steps
steps_file = "../../test_command_triggered.py"
steps, scenarios = parse_file(steps_file)

# Generate the markdown
markdown_content = generate_markdown(steps_file, steps, scenarios)


# Write the markdown to a file
with open('test_steps.md', 'w') as file:
    file.write(markdown_content)

print("Markdown file 'test_steps.md' has been generated.")

