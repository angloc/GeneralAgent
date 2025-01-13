# Singleton
import os
from codyer import skills


def default_output_callback(token):
    if token is not None:
        print(token, end="", flush=True)
    else:
        print("\n", end="", flush=True)


def default_check(check_content=None):
    show = "Confirm | Continue (Enter, yes, y, ok) or directly input your thoughts\n"
    if check_content is not None:
        show = f"{check_content}\n\n{show}"
    response = input(show)
    if response.lower() in ["", "yes", "y", "ok"]:
        return None
    else:
        return response


def load_functions_with_path(python_code_path) -> tuple[list, str]:
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


def _exec(code, globals_vars={}):
    """
    Execute code and return the last expression
    """
    import ast

    tree = ast.parse(code)

    try:
        last_node = tree.body[-1]
        code_body = tree.body[0:-1]
        last_expr = ast.unparse(last_node)

        if isinstance(last_node, ast.Assign):
            code_body = tree.body
            expr_left = last_node.targets[-1]
            if isinstance(expr_left, ast.Tuple):
                last_expr = f"({', '.join([x.id for x in expr_left.elts])})"
            else:
                last_expr = expr_left.id

        elif isinstance(last_node, ast.AugAssign) or isinstance(
            last_node, ast.AnnAssign
        ):
            code_body = tree.body
            last_expr = last_node.target.id

        if len(code_body):
            main_code = compile(ast.unparse(code_body), "<string>", "exec")
            exec(main_code, globals_vars)
    except SyntaxError:
        return None

    try:
        return eval(
            compile(last_expr, "<string>", "eval"),
            globals_vars,
        )
    except SyntaxError:
        return None


if len(skills._functions) == 0:
    skills._add_function("input", input)
    skills._add_function("check", default_check)
    skills._add_function("print", default_output_callback)
    skills._add_function("output", default_output_callback)
    skills._add_function("_exec", _exec)
    funcs = load_functions_with_directory(os.path.dirname(__file__))
    for fun in funcs:
        skills._add_function(fun.__name__, fun)
