import re


def create_prompt(*args) -> str:
    with open("directive") as f:
        directive = f.read()

        for i, arg in enumerate(args):
            directive = directive.replace(f"%var{i+1}%", arg)

        directive = re.sub(r"%var{\d+}%", "", directive)

    return directive
