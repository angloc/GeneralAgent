def get_python_version() -> str:
    """
    Return the python version, like "3.9.12"
    """
    import platform

    python_version = platform.python_version()
    return python_version


def get_os_version() -> str:
    import platform

    system = platform.system()
    if system == "Windows":
        version = platform.version()
        return f"Windows version: {version}"
    elif system == "Darwin":
        version = platform.mac_ver()[0]
        return f"macOS version: {version}"
    elif system == "Linux":
        version = platform.platform()
        return f"Linux version: {version}"
    else:
        return "Unknown system"


def get_python_code(content: str) -> str:
    """
    Return the python code text from content
    """
    template = "```python\n(.*?)\n```"
    import re

    code = re.findall(template, content, re.S)
    if len(code) > 0:
        return code[0]
    else:
        return content


def test_get_python_code():
    content = """
```python
import os
print(os.getcwd())
```
"""
    assert get_python_code(content) == "import os\nprint(os.getcwd())"


def load_functions_with_path(python_code_path) -> (list, str):
    """
    Load functions from python file
    @param python_code_path: the path of python file
    @return: a list of functions and error message (if any, else None)
    """
    try:
        import importlib.util
        import inspect

        # Specify the file path and name to load
        module_name = "skills"
        module_file = python_code_path

        # Use importlib to load the file
        spec = importlib.util.spec_from_file_location(module_name, module_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Get all functions in the file
        functions = inspect.getmembers(module, inspect.isfunction)

        # Filter functions that start with underscore
        functions = filter(lambda f: not f[0].startswith("_"), functions)

        return [f[1] for f in functions], None
    except Exception as e:
        # Code may have errors, failed to load
        import logging

        logging.exception(e)
        return [], str(e)


def load_functions_with_directory(python_code_dir) -> list:
    """
    Load functions from python directory (recursively)
    @param python_code_dir: the path of python directory
    @return: a list of functions
    """
    import os

    total_funs = []
    for file in os.listdir(python_code_dir):
        # if file is directory
        if os.path.isdir(os.path.join(python_code_dir, file)):
            total_funs += load_functions_with_directory(
                os.path.join(python_code_dir, file)
            )
        else:
            # if file is file
            if file.endswith(".py") and (
                not file.startswith("__init__")
                and not file.startswith("_")
                and not file == "main.py"
            ):
                funcs, error = load_functions_with_path(
                    os.path.join(python_code_dir, file)
                )
                total_funs += funcs
    return total_funs


def get_function_signature(func, module: str = None):
    """Returns a description string of function"""
    try:
        import inspect

        sig = inspect.signature(func)
        sig_str = str(sig)
        desc = f"{func.__name__}{sig_str}"
        if func.__doc__:
            desc += ": " + func.__doc__.strip()
        if module is not None:
            desc = f"{module}.{desc}"
        if inspect.iscoroutinefunction(func):
            desc = "" + desc
        return desc
    except Exception as e:
        import logging

        logging.exception(e)
        return ""


def python_line_is_variable_expression(line):
    """
    Return True if line is a variable expression, else False
    """
    import ast

    try:
        tree = ast.parse(line)
    except SyntaxError:
        return False

    if len(tree.body) != 1 or not isinstance(tree.body[0], ast.Expr):
        return False

    expr = tree.body[0].value
    if isinstance(expr, ast.Call):
        return False

    return True
